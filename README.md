# Cocktail API

Welcome to the **Cocktail API**, a RESTful API built with Python, FastAPI, and SQLite, designed to manage cocktail recipes efficiently. This API allows users to add new cocktails, retrieve a list of all cocktails, and fetch details of a specific cocktail by its ID. The database schema is normalized to minimize data duplication and follows best practices.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Clone the Repository](#1-clone-the-repository)
  - [Set Up a Virtual Environment (Optional)](#2-set-up-a-virtual-environment-optional)
  - [Install Dependencies](#3-install-dependencies)
  - [Run the Application](#4-run-the-application)
- [Using Docker (Alternative Installation)](#using-docker-alternative-installation)
  - [Build the Docker Image](#1-build-the-docker-image)
  - [Run the Docker Container](#2-run-the-docker-container)
- [API Endpoints](#api-endpoints)
  - [1. Add a Cocktail](#1-add-a-cocktail)
  - [2. Get All Cocktails](#2-get-all-cocktails)
  - [3. Get a Cocktail by ID](#3-get-a-cocktail-by-id)
- [Data Models](#data-models)
  - [Cocktail Model](#cocktail-model)
  - [Ingredient Model](#ingredient-model)
  - [Metadata Model](#metadata-model)
- [Database Schema](#database-schema)
---

## Features

- **Add Cocktails**: Create new cocktail recipes with detailed ingredients, instructions, and metadata.
- **Retrieve Cocktails**: Fetch all cocktails or retrieve a specific cocktail by its ID.
- **Normalized Database**: Minimizes data duplication by using a normalized schema with relationships.
- **Database Best Practices**: Uses SQLAlchemy ORM for efficient database interactions.
- **FastAPI Framework**: Provides high performance and easy-to-use API development.

---

## Architecture

The Cocktail API is built using:

- **Python 3.12**
- **FastAPI**: Modern, fast (high-performance), web framework for building APIs.
- **SQLite**: Lightweight disk-based database.
- **SQLAlchemy**: Powerful ORM for database interactions.

---

## Requirements

- **Python 3.12** or higher
- **pip** package installer
- **Git** (optional, for cloning the repository)
- **Docker** (optional, for running the app in a container)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/CasualCodersProjects/cocktail-api.git
cd cocktail-api
```

### 2. Set Up a Virtual Environment (Optional)

It's recommended to use a virtual environment to manage dependencies.

```bash
python3.12 -m venv venv
```

Activate the virtual environment:

- On macOS and Linux:

  ```bash
  source venv/bin/activate
  ```

- On Windows:

  ```bash
  venv\Scripts\activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

- The `--reload` flag enables hot reloading, which restarts the server when code changes are detected.
- The application will be available at `http://localhost:8000`.

---

## Using Docker (Alternative Installation)

You can run the Cocktail API inside a Docker container.

### 1. Build the Docker Image

```bash
docker build -t cocktail-api .
```

### 2. Run the Docker Container

```bash
docker run -d --name cocktail-api-container -p 8000:8000 -v $(pwd)/data:/app/data cocktail-api
```

- `-d` runs the container in detached mode.
- `--name` assigns the container a name.
- `-p 8000:8000` maps host port 8000 to container port 8000.
- `-v $(pwd)/data:/app/data` mounts the host directory `./data` to the container directory `/app/data`.


---

## API Endpoints

### 1. Add a Cocktail

- **Endpoint**: `POST /cocktails`
- **Description**: Adds a new cocktail to the database.
- **Request Body**:

  ```json
  {
    "title": "Cocktail Title",
    "author": "Author Name",
    "description": "Cocktail description.",
    "ingredients": [
      {
        "name": "Ingredient Name",
        "quantity": "Amount",
        "unit": "Unit",
        "notes": "Additional notes."
      }
    ],
    "instructions": [
      "Step 1",
      "Step 2",
      "Step 3"
    ],
    "metadata": {
      "difficulty": "easy",
      "glass_type": "rocks",
      "garnish": ["Garnish Item"],
      "tags": ["tag1", "tag2"],
      "flavor_tags": ["flavor1", "flavor2"],
      "cover_image": "https://example.com/image.jpg"
    }
  }
  ```

- **Response**: Returns the newly created cocktail with its assigned ID.

### 2. Get All Cocktails

- **Endpoint**: `GET /cocktails`
- **Description**: Retrieves a list of all cocktails.
- **Response**: An array of cocktail objects.

### 3. Get a Cocktail by ID

- **Endpoint**: `GET /cocktails/{cocktail_id}`
- **Description**: Retrieves a specific cocktail by its ID.
- **Parameters**:
  - `cocktail_id`: The ID of the cocktail to retrieve.
- **Response**: The cocktail object with the specified ID.

---

## Data Models

### Cocktail Model

- **id**: Integer (Auto-incremented primary key)
- **title**: String (Name of the cocktail)
- **author**: String (Author or source)
- **description**: String (Detailed description)
- **ingredients**: List of ingredients associated with the cocktail.
- **instructions**: List of step-by-step instructions.
- **metadata**: Additional information like difficulty, glass type, tags, and cover image URL.

### Ingredient Model

- **name**: String (Ingredient name)
- **quantity**: String (Amount required)
- **unit**: String (Measurement unit)
- **notes**: String (Additional notes or preparation instructions)

### Metadata Model

- **difficulty**: String (e.g., easy, medium, hard)
- **glass_type**: String (Type of glassware)
- **garnish**: List of strings (Garnishes used)
- **tags**: List of strings (General tags)
- **flavor_tags**: List of strings (Flavor profile)
- **cover_image**: String (URL to the cover image)

---

## Database Schema

The database is designed using SQLAlchemy ORM with normalized tables to minimize data duplication.

- **cocktails**: Stores cocktail information.
- **ingredients**: Stores unique ingredients.
- **cocktail_ingredients**: Association table linking cocktails and ingredients with details like quantity and unit.
- **instructions**: Stores step-by-step instructions for each cocktail.
- **tags**: Stores tags and flavor tags.
- **garnishes**: Stores garnish items.
- **Association Tables**:
  - **cocktail_tags**: Links cocktails with their tags.
  - **cocktail_garnishes**: Links cocktails with their garnishes.

---

## Additional Information

### Accessing API Documentation

FastAPI provides interactive API documentation built-in.

- **Swagger UI**: Accessible at `http://localhost:8000/docs`
- **ReDoc**: Accessible at `http://localhost:8000/redoc`

### Persisting Data with Docker

By default, data inside a Docker container is ephemeral. To persist the SQLite database:

- Create a data directory on your host machine:

  ```bash
  mkdir /path/to/your/local/data
  ```

- Modify the `DATABASE_URL` in `main.py`:

  ```python
  # Use the data directory inside the container
  DATABASE_URL = 'sqlite:///./data/cocktails.db'
  ```

- Run the Docker container with volume mounting:

  ```bash
  docker run -d --name cocktail-api-container -p 8000:8000 -v /path/to/your/local/data:/app/data cocktail-api
  ```

## Sample Data

Here's an example of a cocktail JSON structure you can use to test the API.

```json
{
  "title": "Old Fashioned",
  "author": "Classic Cocktail",
  "description": "The Old Fashioned is a classic cocktail made with whiskey, sugar, bitters, and a twist of citrus.",
  "ingredients": [
    {
      "name": "Whiskey",
      "quantity": "2",
      "unit": "oz",
      "notes": "Bourbon or Rye. High Quality."
    },
    {
      "name": "Simple Syrup",
      "quantity": "0.25",
      "unit": "oz",
      "notes": "Alternatively, muddle a sugar cube."
    },
    {
      "name": "Angostura Bitters",
      "quantity": "2",
      "unit": "dash",
      "notes": "To taste. Sub any bitter."
    },
    {
      "name": "Orange Peel",
      "quantity": "1",
      "unit": "slice",
      "notes": "Expressed."
    },
    {
      "name": "Cherry",
      "quantity": "1",
      "unit": "",
      "notes": "Optional garnish."
    }
  ],
  "instructions": [
    "Add one large, clear ice cube to a rocks glass.",
    "Add the Whiskey, Syrup, and Bitters.",
    "Stir until well chilled.",
    "Garnish with a twist of orange peel and optionally a cherry."
  ],
  "metadata": {
    "difficulty": "easy",
    "glass_type": "rocks",
    "garnish": ["orange peel", "cherry"],
    "tags": ["cocktail", "whiskey", "classic", "bitter", "drink"],
    "flavor_tags": ["bitter", "sweet", "citrusy", "smooth", "strong"],
    "cover_image": "https://example.com/images/old-fashioned.jpg"
  }
}
```

---

## Error Handling

The API uses appropriate HTTP status codes to indicate success or failure.

- **200 OK**: Successful request.
- **201 Created**: Resource successfully created.
- **400 Bad Request**: Invalid request data.
- **404 Not Found**: Resource not found.

---

## Future Enhancements

- **Authentication and Authorization**: Implement JWT tokens for secure access.
- **Pagination**: Add pagination to the `GET /cocktails` endpoint for better performance with large datasets.
- **Search Functionality**: Allow searching cocktails by title, ingredients, or tags.
- **Caching**: Implement caching for frequently accessed data.
- **Unit Tests**: Add comprehensive unit and integration tests.

---
