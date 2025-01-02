# OllamaAI

**OllamaAI** is a comprehensive Python-based project designed for managing, rewriting, and parsing property data. It supports efficient data migrations, leverages AI for generating property descriptions and reviews, and provides a modular design for easy extensibility. The project uses Docker for seamless deployment and development.

## Table of Contents

1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure)
4. [Setup and Installation](#setup-and-installation)
5. [Usage](#usage)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Contributing](#contributing)
9. [License](#license)

---

## Features

- **Data Parsing**: Extract property data from SQL dumps using a robust parsing module.
- **AI-Powered Text Generation**: Automatically rewrite property titles, descriptions, summaries, and reviews using the Gemini AI API.
- **Database Management**: Efficiently handles property data with Django ORM and supports spatial data with PostGIS.
- **Testing**: Comprehensive unit testing using `pytest` ensures reliability.
- **Docker Integration**: Simplifies development and deployment with Docker and `docker-compose`.

---

## Technologies Used

- **Python 3.12**
- **Django 5.1**
- **PostgreSQL** with **PostGIS** for geospatial data
- **Tabulate** for formatting terminal output
- **Docker** and **Docker Compose** for containerization
- **Pytest** for unit testing
- **Gemini AI API** for natural language generation

---

## Project Structure

```plaintext
OLAMAAI/
├── app
│   ├── alembic/                    # Alembic migrations for database schema
│   ├── Data_Parsing/
│   │   ├── __init__.py
│   │   ├── parse.py                # Parses property data from SQL files
│   │   └── tripcom_backup.sql      # Sample SQL file for parsing
│   ├── property_manager/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── generate_data.py # Command to generate and rewrite property data
│   │   │       └── regenerate_properties.py # Command to regenerate properties
│   │   ├── tests/
│   │   │   ├── test_generate_data.py # Tests for `generate_data.py`
│   │   │   └── test_models.py       # Tests for Django models
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── models.py               # Defines Property, PropertySummary, and PropertyRating models
│   ├── property_rewriter/          # Main Django app for managing property rewriting
├── manage.py                       # Django management script
├── Dockerfile                      # Docker setup for application
├── docker-compose.yml              # Multi-container Docker setup
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

## Setup and Installation

### Prerequisites

1. **Docker** and **Docker Compose** installed on your system.
2. Python 3.12 or higher (if running locally without Docker).
3. PostgreSQL with PostGIS extension enabled.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mdadnanshuvo/OllamaAI.git
   cd OllamaAI
   ```
 2. Build and Start Docker Containers

 ```bash
 docker-compose up --build
 ```
  Run Database Migrations

  ```bash
  docker-compose exec web python manage.py migrate

  ```
## Usage

### Access the Application

1. **Start the development server**:
   ```bash
   docker-compose up
   ```
   Open in Browser
   - **Web Application:** [http://localhost:8000](http://localhost:8000)
   - **PgAdmin:** [http://localhost:5050](http://localhost:5050)

# CLI Commands

## Generate Data with AI

Regenerate Property Data
```bash

docker-compose exec web python manage.py generate_data
```

The re-generated and newly-generated data can be seen in the terminal. For the full updated data in the existing database, please access the PgAdmin panel using the following credentials:

- **Username:** myuser
- **Password:** mypassword
- **Database:** tripcom_data
- **Host:** localhost
- **Port:** 5432
 


## Parse Data from SQL

### Parse SQL Dump

Ensure the SQL file is placed in `app/Data_Parsing/`. Run:

```bash
docker-compose exec web python manage.py parse_properties
```

The data utilized in this project is derived from the previously completed assignment, scrapy-data. Specifically, a backup file from that assignment serves as the source. The parse.py script is employed to parse the SQL backup file, process its contents, and prepare the data for use as input into the Gemini system. This structured workflow ensures seamless integration and efficient data handling.


## Testing

### Run Tests
To ensure reliability, run the test suite:

```bash
docker-compose exec web pytest --cov=property_manager --cov-report=term
```




