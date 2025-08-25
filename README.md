# Weather Data Service

A Flask-based backend service that fetches time-series weather data from the Open-Meteo API and generates Excel files and PDF reports with charts.

## Features

- 🌤️ Fetch weather data (temperature & humidity) from Open-Meteo MeteoSwiss API
- 💾 Store data in SQLite database
- 📊 Export data to Excel format
- 📄 Generate PDF reports with weather charts
- 🔍 RESTful API endpoints
- 🧹 Clean, modular code structure

## Project Structure

```
assignment/
├── app.py                 # Main Flask application with clean endpoints
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── test_api.py           # API testing script
├── models/
│   └── database.py       # Database operations and models
├── services/
│   ├── weather_service.py    # Weather API integration
│   └── export_service.py     # Excel and PDF export functions
├── templates/
│   └── weather_report.html  # PDF report HTML template
├── utils/
│   └── database_utils.py     # Database utilities and initialization
├── exports/              # Generated export files
└── venv/                 # Virtual environment
```

## API Endpoints

### 1. Weather Report

```
GET /weather-report?lat={latitude}&lon={longitude}
```

- Fetches weather data for the past 2 days
- Stores data in SQLite database
- Returns operation status and record count

**Example:**

```bash
curl "http://localhost:5000/weather-report?lat=47.37&lon=8.55"
```

### 2. Excel Export

```
GET /export/excel
```

- Exports last 48 hours of weather data as Excel file
- Returns downloadable .xlsx file
- Columns: timestamp | latitude | longitude | temperature_2m | relative_humidity_2m

**Example:**

```bash
curl -O "http://localhost:5000/export/excel"
```

### 3. PDF Report

```
GET /export/pdf
```

- Generates PDF report with weather charts
- Includes metadata (location, date range, statistics)
- Returns downloadable .pdf file with temperature and humidity line charts

**Example:**

```bash
curl -O "http://localhost:5000/export/pdf"
```

### 4. Health Check

```
GET /health
```

- Simple health check endpoint
- Returns service status

## Installation & Setup

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

python app.py
```

The service will be available at `http://localhost:5000`

## Usage Examples

### 1. Fetch Weather Data

```bash
# Fetch data for Zurich, Switzerland
curl "http://localhost:5000/weather-report?lat=47.37&lon=8.55"
```

### 2. Download Excel Report

```bash
# Download Excel file
curl -O -J "http://localhost:5000/export/excel"
```

### 3. Download PDF Report

```bash
# Download PDF report
curl -O -J "http://localhost:5000/export/pdf"
```

## Technical Details

### Database Schema

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

### Technologies Used

- **Flask**: Web framework
- **SQLite**: Database
- **Requests**: HTTP client for API calls
- **Pandas**: Data manipulation
- **Matplotlib**: Chart generation
- **WeasyPrint**: PDF generation
- **OpenPyXL**: Excel file generation

### Code Organization

- **Clean separation of concerns**: Each module has a specific responsibility
- **Function-based architecture**: Business logic separated from route handlers
- **Error handling**: Comprehensive error handling with meaningful messages
- **Configuration management**: Centralized configuration
- **Database abstraction**: Clean database operations

## Example Output Files

The service generates:

- `weather_data.xlsx`: Excel file with timestamped weather data
- `weather_report.pdf`: PDF report with charts and metadata

## Development

### Code Style

- Clean, readable code with proper documentation
- Function-based approach for better testability
- Separation of API routes from business logic
- Proper error handling and logging

### Testing

```bash
# Test the endpoints
curl "http://localhost:5000/health"
curl "http://localhost:5000/weather-report?lat=47.37&lon=8.55"
curl -O "http://localhost:5000/export/excel"
curl -O "http://localhost:5000/export/pdf"
```

## Troubleshooting

### Testing

#### Automated Testing

```bash
# Run the comprehensive test script
python test_api.py
```

#### Manual Testing

```bash
# Test health endpoint
curl "http://localhost:5000/health"

# Test weather data fetching
curl "http://localhost:5000/weather-report?lat=47.37&lon=8.55"

# Test Excel export
curl -O "http://localhost:5000/export/excel"

# Test PDF export
curl -O "http://localhost:5000/export/pdf"
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure virtual environment is activated
2. **API timeouts**: Check internet connection and API availability
3. **PDF generation issues**: Ensure WeasyPrint dependencies are installed
4. **Database errors**: Check file permissions and disk space

### Logs

Check the Flask console output for detailed error messages and debugging information.

## Future Enhancements

- Add data validation and sanitization
- Implement caching for API responses
- Add authentication and rate limiting
- Support for multiple locations
- Real-time data updates
- Docker containerization

## WeasyPrint Setup (Windows)

For PDF generation, WeasyPrint requires additional dependencies on Windows:

1. Install Python from Microsoft Store
2. Install MSYS2, then run: `pacman -S mingw-w64-x86_64-pango`
3. Install WeasyPrint via pip in your virtual environment


For detailed setup instructions, see: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
