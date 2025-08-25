# Weather Data Service API

A Flask-based REST API service that fetches weather data from the Open-Meteo API and provides Excel and PDF export capabilities with integrated charts.

## Overview

This service provides a comprehensive weather data solution with:

- Real-time weather data fetching and storage
- Excel export with formatted data
- PDF report generation with embedded charts
- RESTful API endpoints with comprehensive validation
- Clean, modular architecture following best practices

## Project Architecture

```
assignment/
├── app.py                     # Main Flask application
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
├── test_api.py               # Comprehensive test suite
├── models/
│   └── database.py           # Database models and operations
├── services/
│   ├── weather_service.py    # Weather API integration service
│   └── export_service.py     # Excel and PDF export service
├── templates/
│   └── weather_report.html   # HTML template for PDF generation
├── utils/
│   └── database_utils.py     # Database utilities and setup
└── exports/                  # Generated export files directory
```

## API Endpoints

| Endpoint          | Method | Description                  | Output                  |
| ----------------- | ------ | ---------------------------- | ----------------------- |
| `/health`         | GET    | Service health check         | JSON status             |
| `/weather-report` | GET    | Fetch and store weather data | JSON response           |
| `/export/excel`   | GET    | Generate Excel export        | Downloadable .xlsx file |
| `/export/pdf`     | GET    | Generate PDF report          | Downloadable .pdf file  |

## Quick Start Guide

### Step 1: System Prerequisites

**Required:**

- Python 3.8 or higher
- Internet connection for API access

**For PDF Generation (Windows only):**

- GTK3 Runtime Environment

### Step 2: GTK3 Setup (Windows Users)

PDF generation requires GTK3 and Pango on Windows for WeasyPrint to function correctly. Based on development experience with Windows, here are the working installation methods:

**Option A: Download GTK3 Runtime**

1. Visit [GTK for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)
2. Download and install the latest GTK3 Runtime Environment
3. Restart your command prompt

**Option B: Install via MSYS2 (Recommended)**

```bash
# Install MSYS2 first, then run:
pacman -S mingw-w64-x86_64-pango
```

**Note:** During development on Windows, it was necessary to install Pango separately for WeasyPrint PDF generation to work properly. This is documented in the [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows). The MSYS2 method includes both GTK3 and Pango dependencies.

### Step 3: Environment Setup

```bash
# 1. Clone or download the project
cd assignment

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Step 4: Start the Service

```bash
# Ensure virtual environment is activated
python app.py
```

You should see:

```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### Step 5: Verify Installation

Open a new terminal and test the health endpoint:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "service": "weather-api",
  "status": "healthy"
}
```

## Docker Deployment (Alternative)

⚠️ **Important Note**: Due to development environment constraints, the Docker setup is untested. **For reliable deployment, please use the manual setup process above.**

For containerized deployment, you can use Docker instead of manual setup:

### Prerequisites

- Docker and Docker Compose installed
- No need for Python, GTK3, or virtual environment setup

### Quick Docker Start

```bash
# Clone/download the project
cd assignment

# Build and start the service
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

The service will be available at `http://localhost:5000`

### Docker Commands

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# Access container shell
docker-compose exec weather-api bash
```

### Docker Features

- **Automatic Dependencies**: All system dependencies (GTK3, Pango) pre-installed
- **Persistent Storage**: Database and exports mounted as volumes
- **Health Checks**: Built-in container health monitoring
- **Easy Deployment**: Single command deployment
- **Cross-Platform**: Works on Windows, macOS, and Linux
  "service": "weather-api",
  "status": "healthy"
  }

````

## Usage Instructions

### 1. Fetch Weather Data

**Endpoint:** `GET /weather-report`

**Parameters:**

- `lat` (required): Latitude (-90 to 90)
- `lon` (required): Longitude (-180 to 180)

**Example:**

```bash
# Fetch weather data for Zurich, Switzerland
curl "http://localhost:5000/weather-report?lat=47.37&lon=8.55"
````

**Response:**

```json
{
  "latitude": 47.37,
  "longitude": 8.55,
  "message": "Weather data fetched and stored successfully",
  "records_added": 72,
  "status": "success"
}
```

### 2. Export to Excel

**Endpoint:** `GET /export/excel`

Generates Excel file with the latest weather data.

```bash
curl -O -J "http://localhost:5000/export/excel"
```

**Output:** `weather_data.xlsx` saved in `exports/` folder

- Contains timestamped weather data
- Auto-formatted columns for readability
- Includes location coordinates and measurements

### 3. Generate PDF Report

**Endpoint:** `GET /export/pdf`

Creates professional PDF report with charts.

```bash
curl -O -J "http://localhost:5000/export/pdf"
```

**Output:** `weather_report.pdf` saved in `exports/` folder

- Layout with metadata
- Temperature and humidity trend charts
- Location and time range information

## Testing the API

### Automated Test Suite

Run the comprehensive test suite:

```bash
python test_api.py
```

The test suite validates:

- ✅ Health endpoint functionality
- ✅ Weather data fetching for multiple locations
- ✅ Input validation and error handling
- ✅ Excel export generation
- ✅ PDF report creation
- ✅ Concurrent request handling
- ✅ Response time performance

### Manual Testing

**1. Test Health Check:**

```bash
curl "http://localhost:5000/health"
```

**2. Test Weather Data Fetching:**

```bash
curl "http://localhost:5000/weather-report?lat=40.7128&lon=-74.0060"
```

**3. Test Excel Export:**

```bash
curl -O "http://localhost:5000/export/excel"
```

**4. Test PDF Export:**

```bash
curl -O "http://localhost:5000/export/pdf"
```

## Database Schema

The service uses SQLite with the following schema:

```sql
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    temperature_2m REAL NOT NULL,
    relative_humidity_2m REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Technology Stack

| Component           | Technology | Purpose               |
| ------------------- | ---------- | --------------------- |
| **Framework**       | Flask      | REST API server       |
| **Database**        | SQLite     | Data storage          |
| **HTTP Client**     | Requests   | External API calls    |
| **Data Processing** | Pandas     | Data manipulation     |
| **Charts**          | Matplotlib | Graph generation      |
| **PDF Generation**  | WeasyPrint | PDF report creation   |
| **Excel Export**    | OpenPyXL   | Excel file generation |

## Output Files

All generated files are saved in the `exports/` directory:

| File                 | Description                     | Format            |
| -------------------- | ------------------------------- | ----------------- |
| `weather_data.xlsx`  | Weather data export             | Excel spreadsheet |
| `weather_report.pdf` | Professional report with charts | PDF document      |

## Troubleshooting

### Common Issues

**1. Import Errors**

```
Solution: Ensure virtual environment is activated
Command: venv\Scripts\activate (Windows) or source venv/bin/activate (Linux/macOS)
```

**2. API Connection Issues**

```
Solution: Check internet connection and Open-Meteo API availability
Test: curl "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m"
```

**3. PDF Generation Fails (Windows)**

```text
Error: WeasyPrint errors or missing dependencies
Solution: Install GTK3 Runtime Environment and Pango
Verification: Restart Flask service after GTK3 installation
Note: Based on Windows development experience, Pango is specifically required for WeasyPrint
```

**4. File Permission Errors**

```
Solution: Ensure write permissions for exports/ directory
Command: Check if exports/ folder exists and is writable
```

### Error Response Format

The API returns structured error responses:

```json
{
  "error": "Description of the error",
  "status": "error"
}
```

### Getting Help

1. **Check Flask Console**: Detailed error messages appear in the server console
2. **Run Test Suite**: Use `python test_api.py` to identify specific issues
3. **Verify Dependencies**: Ensure all packages in `requirements.txt` are installed
4. **Check GTK3**: For PDF issues on Windows, verify GTK3 installation

## Data Sources

- **Weather Data**: [Open-Meteo API](https://open-meteo.com/) - MeteoSwiss provider
- **Coverage**: Global weather data with hourly resolution
- **Parameters**: 2-meter temperature and relative humidity
- **Time Range**: Last 48 hours from request time
