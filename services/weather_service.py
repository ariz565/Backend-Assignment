# Standard library imports
from datetime import datetime, timedelta

# Third-party imports
import requests
from flask import request, jsonify

# Local imports
from config import Config
from models.database import insert_weather_data  


# Endpoint function for weather report - GET /weather-report?lat={lat}&lon={lon}
def weather_report_endpoint():
    # Handles HTTP request validation and delegates business logic to service layer
    
    # Input validation and sanitization
    validation_result = _validate_coordinates_input()  # Call validation helper
    if validation_result:
        return validation_result
    
    lat = float(request.args.get('lat'))  # Extract validated latitude
    lon = float(request.args.get('lon'))  # Extract validated longitude
    
    try:
        result = fetch_and_store_weather_data(lat, lon)  # Call main business logic
        
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            # print(f"Weather data fetch failed: {result.get('message', 'Unknown error')}")  # Debug logging
            return jsonify(result), 500
            
    except Exception as e:
        # print(f"Internal server error in weather_report_endpoint: {str(e)}")  # Debug logging
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

def _validate_coordinates_input():
    # Private helper function to validate coordinate inputs
    
    lat = request.args.get('lat')  # Get latitude parameter
    lon = request.args.get('lon')  # Get longitude parameter
    
    if not lat or not lon:
        return jsonify({
            'error': 'Both lat and lon parameters are required',
            'status': 'error'
        }), 400
    
    try:
        lat_float = float(lat)  # Convert and validate latitude
        lon_float = float(lon)  # Convert and validate longitude
        
        # Validate coordinate ranges
        if not (-90 <= lat_float <= 90):
            return jsonify({
                'error': 'Latitude must be between -90 and 90',
                'status': 'error'
            }), 400
            
        if not (-180 <= lon_float <= 180):
            return jsonify({
                'error': 'Longitude must be between -180 and 180',
                'status': 'error'
            }), 400
            
    except ValueError:
        return jsonify({
            'error': 'Invalid latitude or longitude values - must be numbers',
            'status': 'error'
        }), 400
    
    return None

def fetch_weather_data(latitude, longitude):
    # Fetch weather data from Open-Meteo API for the past specified days
    
    # Calculate date range for past days
    end_date = datetime.now().date()  # Get current date
    start_date = end_date - timedelta(days=Config.DAYS_TO_FETCH)  # Calculate start date
    
    # Prepare API request parameters using config
    params = Config.get_api_params(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    try:
        response = requests.get(Config.OPEN_METEO_BASE_URL, params=params, timeout=Config.API_TIMEOUT)  # Make API call
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Return parsed JSON response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch weather data: {str(e)}")

def process_weather_data(api_response, latitude, longitude):
    # Process the API response and prepare data for database insertion
    
    hourly_data = api_response.get('hourly', {})  # Extract hourly data section
    timestamps = hourly_data.get('time', [])  # Get time array
    temperatures = hourly_data.get('temperature_2m', [])  # Get temperature array
    humidity = hourly_data.get('relative_humidity_2m', [])  # Get humidity array
    
    if not timestamps or not temperatures or not humidity:
        raise Exception("Invalid API response: Missing required data fields")
    
    # Prepare data for database insertion with null safety
    data_list = []
    for i in range(len(timestamps)):
        data_list.append((
            timestamps[i],
            latitude,
            longitude,
            temperatures[i] if temperatures[i] is not None else 0.0,  # Handle null temperatures
            humidity[i] if humidity[i] is not None else 0.0  # Handle null humidity
        ))
    
    return data_list

def fetch_and_store_weather_data(latitude, longitude):
    # Main orchestrator function to fetch weather data and store in database
    
    try:
        # Step 1: Fetch data from external API
        # print(f"Fetching weather data for lat={latitude}, lon={longitude}")  # Debug logging
        api_response = fetch_weather_data(latitude, longitude)  # Call API fetch function
        
        # Step 2: Transform data for storage
        # print(f"Processing API response data")  # Debug logging
        processed_data = process_weather_data(api_response, latitude, longitude)  # Call data processor
        
        # Step 3: Persist data
        # print(f"Storing {len(processed_data)} records in database")  # Debug logging
        insert_weather_data(processed_data)  # Call database insert function
        
        # print(f"Successfully completed weather data fetch and store")  # Debug logging
        return {
            'status': 'success',
            'message': f'Successfully stored {len(processed_data)} weather records',
            'records_count': len(processed_data),
            'latitude': latitude,
            'longitude': longitude,
            'date_range': f'{Config.DAYS_TO_FETCH} days'
        }
        
    except Exception as e:
        # print(f"Error in fetch_and_store_weather_data: {str(e)}")  # Debug logging
        return {
            'status': 'error',
            'message': str(e)
        }
