# Quorum Legislative Data System

A Django application for processing and displaying legislative voting data from CSV files.

## Project Overview

This application will process legislative data from CSV files to provide insights about voting patterns. Currently in initial setup phase.

## Technology Stack

- **Backend**: Django 5
- **Data Processing**: Pandas for CSV handling
- **Testing**: pytest with Django integration
- **Code Quality**: black, isort, flake8

## Project Structure

```
quorum-coding-challenge/
├── manage.py
├── requirements.txt
├── .env.example
├── core/                      # Main Django project
├── legislative/               # Main app (to be implemented)
│   ├── models.py              # Django models
│   ├── views.py               # Views
│   └── templates/             # HTML templates
├── csv_data/                  # CSV files directory
├── tests/                     # Test files
└── .venv/                     # Virtual environment
```

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/leandromsd/quorum-coding-challenge.git
   cd quorum-coding-challenge
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations and start server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

6. **Access the application**
   - Django welcome page: http://localhost:8000/

## Development Status

✅ **Phase 1 - Project Setup** (Completed)
- Django project structure
- Development environment configuration
- Code quality tools setup

🔄 **Phase 2 - Data Processing** (Next)
- CSV data models
- Data processing services
- API endpoints

⏳ **Phase 3 - Web Interface** (Planned)
- HTML templates
- Data visualization tables

## Development Commands

### Running Tests
```bash
# Run all tests (when implemented)
python manage.py test

# Run with pytest and coverage
pytest tests/ -v --cov
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Check code style
flake8 .

# Run all quality checks
black . && isort . && flake8 .
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Run with specific port
python manage.py runserver 8080
```

## Contributing

1. Follow PEP 8 style guidelines
2. Write tests for new functionality
3. Ensure all tests pass before committing
4. Use meaningful commit messages

## License

This project is developed as part of the Quorum coding challenge.