# OllamaAI

OllamaAI is a comprehensive project designed to manage and rewrite properties, parse data, and handle migrations efficiently. The project is primarily written in Python with support for Docker to ease deployment and development.

## Project Structure

The project is organized as follows:

```plaintext
OLAMAAI/
├── app
│   ├── alembic/
│   ├── Data_Parsing/
│   │   ├── __init__.py
│   │   ├── parse.py
│   │   └── tripcom_backup_20241230123803.sql
│   ├── property_manager/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       ├── generate_data.py
│   │   │       └── regenerate_properties.py
│   │   ├── migrations/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_generate_data.py
│   │   │   └── test_models.py
│   │   ├── test_parse.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── models.py
│   ├── property_rewriter/
│   └── __init__.py
├── .coverage
├── alembic.ini
├── manage.py
├── pytest.ini
├── settings.py
├── urls.py
├── test.api.py
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
