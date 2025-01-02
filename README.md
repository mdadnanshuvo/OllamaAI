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
