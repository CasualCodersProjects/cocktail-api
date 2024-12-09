from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base

# Database setup
DATABASE_URL = 'sqlite:///./data/cocktails.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Association tables for many-to-many relationships
cocktail_tags_table = Table('cocktail_tags', Base.metadata,
    Column('cocktail_id', Integer, ForeignKey('cocktails.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

cocktail_garnishes_table = Table('cocktail_garnishes', Base.metadata,
    Column('cocktail_id', Integer, ForeignKey('cocktails.id')),
    Column('garnish_id', Integer, ForeignKey('garnishes.id'))
)

# SQLAlchemy models
class Cocktail(Base):
    __tablename__ = 'cocktails'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String)
    description = Column(String)
    difficulty = Column(String)
    glass_type = Column(String)
    cover_image = Column(String)  # New field for cover_image URL

    ingredients = relationship('CocktailIngredient', back_populates='cocktail', cascade='all, delete-orphan')
    instructions = relationship('Instruction', back_populates='cocktail', cascade='all, delete-orphan')
    tags = relationship('Tag', secondary=cocktail_tags_table, back_populates='cocktails')
    garnishes = relationship('Garnish', secondary=cocktail_garnishes_table, back_populates='cocktails')

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    cocktails = relationship('CocktailIngredient', back_populates='ingredient')

class CocktailIngredient(Base):
    __tablename__ = 'cocktail_ingredients'
    id = Column(Integer, primary_key=True)
    cocktail_id = Column(Integer, ForeignKey('cocktails.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    quantity = Column(String)
    unit = Column(String)
    notes = Column(String)

    cocktail = relationship('Cocktail', back_populates='ingredients')
    ingredient = relationship('Ingredient', back_populates='cocktails')

class Instruction(Base):
    __tablename__ = 'instructions'
    id = Column(Integer, primary_key=True)
    cocktail_id = Column(Integer, ForeignKey('cocktails.id'))
    step_number = Column(Integer)
    instruction_text = Column(String)

    cocktail = relationship('Cocktail', back_populates='instructions')

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)  # 'tag' or 'flavor_tag'

    cocktails = relationship('Cocktail', secondary=cocktail_tags_table, back_populates='tags')

class Garnish(Base):
    __tablename__ = 'garnishes'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    cocktails = relationship('Cocktail', secondary=cocktail_garnishes_table, back_populates='garnishes')

# Pydantic models
class IngredientCreate(BaseModel):
    name: str
    quantity: Optional[str]
    unit: Optional[str]
    notes: Optional[str]

class InstructionCreate(BaseModel):
    instruction_text: str

class MetadataCreate(BaseModel):
    difficulty: Optional[str]
    glass_type: Optional[str]
    garnish: Optional[List[str]]
    tags: Optional[List[str]]
    flavor_tags: Optional[List[str]]
    cover_image: Optional[str]  # New field for cover_image URL

class CocktailCreate(BaseModel):
    title: str
    author: Optional[str]
    description: Optional[str]
    ingredients: List[IngredientCreate]
    instructions: List[str]
    metadata: Optional[MetadataCreate]

class IngredientRead(BaseModel):
    name: str
    quantity: Optional[str]
    unit: Optional[str]
    notes: Optional[str]

    class Config:
        orm_mode = True

class MetadataRead(BaseModel):
    difficulty: Optional[str]
    glass_type: Optional[str]
    garnish: Optional[List[str]]
    tags: Optional[List[str]]
    flavor_tags: Optional[List[str]]
    cover_image: Optional[str]

class CocktailRead(BaseModel):
    id: int
    title: str
    author: Optional[str]
    description: Optional[str]
    ingredients: List[IngredientRead]
    instructions: List[str]
    metadata: Optional[MetadataRead]

    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Serialization function
def serialize_cocktail(cocktail: Cocktail):
    return {
        'id': cocktail.id,
        'title': cocktail.title,
        'author': cocktail.author,
        'description': cocktail.description,
        'ingredients': [
            {
                'name': ci.ingredient.name,
                'quantity': ci.quantity,
                'unit': ci.unit,
                'notes': ci.notes
            } for ci in cocktail.ingredients
        ],
        'instructions': [instr.instruction_text for instr in sorted(cocktail.instructions, key=lambda x: x.step_number)],
        'metadata': {
            'difficulty': cocktail.difficulty,
            'glass_type': cocktail.glass_type,
            'garnish': [garnish.name for garnish in cocktail.garnishes],
            'tags': [tag.name for tag in cocktail.tags if tag.type == 'tag'],
            'flavor_tags': [tag.name for tag in cocktail.tags if tag.type == 'flavor_tag'],
            'cover_image': cocktail.cover_image  # Include cover_image in the serialized output
        }
    }

# Endpoint to add a cocktail
@app.post("/cocktails", status_code=201, response_model=CocktailRead)
def create_cocktail(cocktail: CocktailCreate, db: Session = Depends(get_db)):
    # Create the Cocktail
    new_cocktail = Cocktail(
        title=cocktail.title,
        author=cocktail.author,
        description=cocktail.description,
        difficulty=cocktail.metadata.difficulty if cocktail.metadata else None,
        glass_type=cocktail.metadata.glass_type if cocktail.metadata else None,
        cover_image=cocktail.metadata.cover_image if cocktail.metadata else None  # Set cover_image
    )
    db.add(new_cocktail)
    db.commit()
    db.refresh(new_cocktail)

    # Handle ingredients
    for ing in cocktail.ingredients:
        # Check if Ingredient exists
        ingredient_obj = db.query(Ingredient).filter(Ingredient.name == ing.name).first()
        if not ingredient_obj:
            ingredient_obj = Ingredient(name=ing.name)
            db.add(ingredient_obj)
            db.commit()
            db.refresh(ingredient_obj)
        # Create CocktailIngredient
        cocktail_ingredient = CocktailIngredient(
            cocktail_id=new_cocktail.id,
            ingredient_id=ingredient_obj.id,
            quantity=ing.quantity,
            unit=ing.unit,
            notes=ing.notes
        )
        db.add(cocktail_ingredient)

    # Handle instructions
    for idx, instruction_text in enumerate(cocktail.instructions):
        instruction = Instruction(
            cocktail_id=new_cocktail.id,
            step_number=idx + 1,
            instruction_text=instruction_text
        )
        db.add(instruction)

    # Handle garnishes
    if cocktail.metadata and cocktail.metadata.garnish:
        for garnish_name in cocktail.metadata.garnish:
            garnish_obj = db.query(Garnish).filter(Garnish.name == garnish_name).first()
            if not garnish_obj:
                garnish_obj = Garnish(name=garnish_name)
                db.add(garnish_obj)
                db.commit()
                db.refresh(garnish_obj)
            new_cocktail.garnishes.append(garnish_obj)

    # Handle tags
    if cocktail.metadata and cocktail.metadata.tags:
        for tag_name in cocktail.metadata.tags:
            tag_obj = db.query(Tag).filter(Tag.name == tag_name, Tag.type == 'tag').first()
            if not tag_obj:
                tag_obj = Tag(name=tag_name, type='tag')
                db.add(tag_obj)
                db.commit()
                db.refresh(tag_obj)
            new_cocktail.tags.append(tag_obj)
    # Handle flavor_tags
    if cocktail.metadata and cocktail.metadata.flavor_tags:
        for tag_name in cocktail.metadata.flavor_tags:
            tag_obj = db.query(Tag).filter(Tag.name == tag_name, Tag.type == 'flavor_tag').first()
            if not tag_obj:
                tag_obj = Tag(name=tag_name, type='flavor_tag')
                db.add(tag_obj)
                db.commit()
                db.refresh(tag_obj)
            new_cocktail.tags.append(tag_obj)

    db.commit()
    db.refresh(new_cocktail)
    return serialize_cocktail(new_cocktail)

# Endpoint to get all cocktails
@app.get("/cocktails", response_model=List[CocktailRead])
def get_cocktails(db: Session = Depends(get_db)):
    cocktails = db.query(Cocktail).all()
    return [serialize_cocktail(cocktail) for cocktail in cocktails]

# Endpoint to get a single cocktail by ID
@app.get("/cocktails/{cocktail_id}", response_model=CocktailRead)
def get_cocktail(cocktail_id: int, db: Session = Depends(get_db)):
    cocktail = db.query(Cocktail).filter(Cocktail.id == cocktail_id).first()
    if not cocktail:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    return serialize_cocktail(cocktail)

# Create the database tables
Base.metadata.create_all(bind=engine)
