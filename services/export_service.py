import os  # For file operations
from datetime import datetime  # For timestamp generation
from flask import send_file, jsonify  # For HTTP responses
from models.database import get_last_48_hours_data  # For fetching weather data
import pandas as pd  
import tempfile  # For temporary file handling
from config import Config  # Import configuration settings
from weasyprint import HTML, CSS  # For PDF generation
import base64  # For image encoding
from io import BytesIO  # For in-memory file operations
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for matplotlib to avoid threading issues
import matplotlib.pyplot as plt  # For chart generation
import matplotlib.dates as mdates  # For date formatting in charts

def excel_export_endpoint():
    # Endpoint function for Excel export - GET /export/excel
    # Validates data exists and returns Excel file for download
    try:
        file_path = generate_excel_export()  # Call Excel generation function
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'Failed to generate Excel file',
                'status': 'error'
            }), 500
            
        return send_file(  # Return file for download
            file_path, 
            as_attachment=True, 
            download_name='weather_data.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({
            'error': f'Excel export failed: {str(e)}',
            'status': 'error'
        }), 500

def pdf_export_endpoint():
    # Endpoint function for PDF export - GET /export/pdf
    # Validates data exists and returns PDF report for download
    try:
        file_path = generate_pdf_report()  # Call PDF generation function
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'Failed to generate PDF file',
                'status': 'error'
            }), 500
            
        return send_file(  # Return file for download
            file_path, 
            as_attachment=True, 
            download_name='weather_report.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'error': f'PDF export failed: {str(e)}',
            'status': 'error'
        }), 500

def generate_excel_export():
    # Generate Excel file with last 48 hours of weather data
    # Returns: Path to the generated Excel file
    
    try:
        # Get data from database
        data = get_last_48_hours_data()  # Call database function
        
        if not data:
            raise Exception("No weather data available for export")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)  # Create pandas DataFrame
        
        # Convert timestamp to datetime for better formatting
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Parse timestamps
        
        # Sort by timestamp
        df = df.sort_values('timestamp')  # Sort chronologically
        
        # Create Excel file
        excel_file_path = os.path.join('exports', 'weather_data.xlsx')
        os.makedirs('exports', exist_ok=True)  # Ensure export directory exists
        
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:  # Create Excel writer
            df.to_excel(writer, sheet_name='Weather Data', index=False)  # Write data to Excel
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Weather Data']
            
            # Auto-adjust column widths for better readability
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return excel_file_path
        
    except Exception as e:
        raise Exception(f"Failed to generate Excel export: {str(e)}")

def create_weather_chart():
    # Create a matplotlib chart showing temperature and humidity over time
    # Returns: Base64 encoded PNG image of the chart
    
    try:
        # Get data from database
        data = get_last_48_hours_data()  # Call database function
        
        if not data:
            raise Exception("No weather data available for chart")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)  # Create pandas DataFrame
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Parse timestamps
        df = df.sort_values('timestamp')  # Sort chronologically
        
        # Create the plot using config settings
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=Config.CHART_FIGURE_SIZE, sharex=True)  # Create 2 subplots
        
        # Temperature plot
        ax1.plot(df['timestamp'], df['temperature_2m'], color='red', linewidth=2, label='Temperature')
        ax1.set_ylabel('Temperature (°C)', color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.grid(True, alpha=0.3)
        ax1.set_title('Temperature over Time (Last 48 Hours)')
        
        # Humidity plot
        ax2.plot(df['timestamp'], df['relative_humidity_2m'], color='blue', linewidth=2, label='Humidity')
        ax2.set_ylabel('Relative Humidity (%)', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2.grid(True, alpha=0.3)
        ax2.set_title('Humidity over Time (Last 48 Hours)')
        ax2.set_xlabel('Time')
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Format dates
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))  # Show every 6 hours
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)  # Rotate labels
        
        plt.tight_layout()  # Adjust layout
        
        # Save to BytesIO and convert to base64
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='PNG', dpi=Config.CHART_DPI, bbox_inches='tight')  # Save chart as PNG
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()  # Encode as base64
        plt.close()  # Clean up matplotlib figure
        
        return img_base64
        
    except Exception as e:
        raise Exception(f"Failed to create weather chart: {str(e)}")

def generate_pdf_report():
    # Generate PDF report with weather charts and metadata
    # Returns: Path to the generated PDF file
    
    try:
        # Get data for metadata
        data = get_last_48_hours_data()  # Call database function
        
        if not data:
            raise Exception("No weather data available for PDF report")
        
        # Get chart image
        chart_base64 = create_weather_chart()  # Call chart generation function
        
        # Calculate metadata
        df = pd.DataFrame(data)  # Create pandas DataFrame
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Parse timestamps
        date_range = f"{df['timestamp'].min().strftime('%Y-%m-%d %H:%M')} to {df['timestamp'].max().strftime('%Y-%m-%d %H:%M')}"
        
        # Enhanced location display with coordinates
        lat = df['latitude'].iloc[0]
        lon = df['longitude'].iloc[0]
        location = f"Location: {lat:.4f}°N, {lon:.4f}°E"
        if lat < 0:
            location = location.replace('°N', '°S')
        if lon < 0:
            location = location.replace('°E', '°W')
            
        avg_temp = df['temperature_2m'].mean()
        avg_humidity = df['relative_humidity_2m'].mean()
        
        # Load HTML template from file
        template_path = os.path.join('templates', 'weather_report.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as file:  # Read HTML template
                html_template = file.read()
        except FileNotFoundError:
            # Fallback to inline template if file not found
            html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Weather Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }}
        .metadata {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .chart {{ text-align: center; margin: 30px 0; }}
        .chart img {{ max-width: 100%; height: auto; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ text-align: center; padding: 15px; background-color: #e9e9e9; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Weather Report</h1>
        <h2>Past 48 Hours Analysis</h2>
    </div>
    <div class="metadata">
        <h3>Report Metadata</h3>
        <p><strong>Location:</strong> {location}</p>
        <p><strong>Date Range:</strong> {date_range}</p>
        <p><strong>Generated:</strong> {generated_time}</p>
        <p><strong>Total Records:</strong> {total_records}</p>
    </div>
    <div class="stats">
        <div class="stat-box">
            <h4>Average Temperature</h4>
            <p>{avg_temp}°C</p>
        </div>
        <div class="stat-box">
            <h4>Average Humidity</h4>
            <p>{avg_humidity}%</p>
        </div>
    </div>
    <div class="chart">
        <h3>Weather Trends</h3>
        <img src="data:image/png;base64,{chart_base64}" alt="Weather Chart">
    </div>
</body>
</html>"""
        
        # Format HTML template with data
        try:
            print(f"🔍 DEBUG: Attempting to format template...")
            print(f"🔍 DEBUG: Template placeholders expected: location, date_range, generated_time, total_records, avg_temp, avg_humidity, chart_base64")
            
            html_content = html_template.format(  # Fill template placeholders
                location=location,
                date_range=date_range,
                generated_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total_records=len(data),
                avg_temp=f"{avg_temp:.1f}",
                avg_humidity=f"{avg_humidity:.1f}",
                chart_base64=chart_base64
            )
            print(f"✅ DEBUG: Template formatting successful")
            
        except KeyError as ke:
            print(f"❌ DEBUG: Missing template placeholder: {ke}")
            raise Exception(f"Template formatting error - missing placeholder: {ke}")
        except Exception as fe:
            print(f"❌ DEBUG: Template formatting error: {fe}")
            print(f"❌ DEBUG: Error type: {type(fe).__name__}")
            raise Exception(f"Template formatting error: {fe}")
        
        # Generate PDF
        pdf_file_path = os.path.join('exports', 'weather_report.pdf')
        os.makedirs('exports', exist_ok=True)  # Ensure export directory exists
        
        HTML(string=html_content).write_pdf(pdf_file_path)  # Generate PDF using WeasyPrint
        
        return pdf_file_path
        
    except Exception as e:
        raise Exception(f"Failed to generate PDF report: {str(e)}")
