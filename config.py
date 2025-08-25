import os

class Config:
    """Application configuration"""
    
    # Flask settings
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Database settings
    DATABASE_NAME = 'weather_data.db'
    DATABASE_CONNECTION_RETRIES = 5
    DATABASE_RETRY_DELAY = 1
    
    # API settings - Open-Meteo Weather API
    OPEN_METEO_BASE_URL = 'https://api.open-meteo.com/v1/forecast'  # Using forecast endpoint
    API_TIMEOUT = 30
    DAYS_TO_FETCH = 2  # Number of days of historical data to fetch
    
    # Weather API parameters
    HOURLY_PARAMS = 'temperature_2m,relative_humidity_2m'
    TIMEZONE = 'auto'
    
    # Export settings
    EXPORT_DIR = 'exports'
    
    # Chart settings
    CHART_FIGURE_SIZE = (12, 8)
    CHART_DPI = 300
    CHART_STYLE = 'seaborn-v0_8'  # Matplotlib style
    
    # Template settings
    TEMPLATE_DIR = 'templates'
    STATIC_DIR = 'static'
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def get_api_params(cls, latitude, longitude, start_date, end_date):
        """Get standardized API parameters for Open-Meteo"""
        return {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': start_date,
            'end_date': end_date,
            'hourly': cls.HOURLY_PARAMS,
            'timezone': cls.TIMEZONE
        }
