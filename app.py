# Third-party imports
from flask import Flask, request

# Local imports
from config import Config
from services.export_service import excel_export_endpoint, pdf_export_endpoint
from services.weather_service import weather_report_endpoint
from utils.database_utils import initialize_database

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database on startup
initialize_database()

# Root endpoint: Welcome message and API information
@app.route('/', methods=['GET'])
def home():
    return {
        'message': 'Weather API Backend Server is Running! 🌤️',
        'status': 'operational',
        'endpoints': {
            'health_check': '/health',
            'weather_report': '/weather-report?lat=LAT&lon=LON',
            'export_excel': '/export/excel (downloads Excel file)',
            'export_pdf': '/export/pdf (downloads PDF file)'
        },
        'description': 'Backend Assignment - Weather Data API with Export Functionality'
    }, 200

# Endpoint 1: Fetch weather data from Open-Meteo API and store in database
@app.route('/weather-report', methods=['GET'])
def weather_report():
    return weather_report_endpoint()

# Endpoint 2: Export last 48 hours of stored weather data as Excel file
@app.route('/export/excel', methods=['GET'])
def export_excel():
    return excel_export_endpoint()

# Endpoint 3: Generate PDF report with charts from stored weather data
@app.route('/export/pdf', methods=['GET'])
def export_pdf():
    return pdf_export_endpoint()

# Endpoint 4: Health check for service status
@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'weather-api'}, 200

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
