# Standard library imports
import base64
import os
import tempfile
from datetime import datetime
from io import BytesIO

# Third-party imports
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid threading issues
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from flask import send_file, jsonify
from weasyprint import HTML, CSS

# Local imports
from config import Config
from models.database import get_weather_data_by_location, get_latest_location_data

# Excel export endpoint - returns downloadable Excel file for latest location data
def excel_export_endpoint():
    try:
        file_path = generate_excel_export()
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'Failed to generate Excel file',
                'status': 'error'
            }), 500
        
        # Get file size for better response info
        file_size = os.path.getsize(file_path)
        
        # print(f"Excel export successful: {file_path} ({file_size} bytes)")
        
        # Create response with custom headers
        response = send_file(
            file_path, 
            as_attachment=True, 
            download_name='weather_data.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Add custom headers for success message
        response.headers['X-Export-Status'] = 'success'
        response.headers['X-Export-Message'] = 'Excel file generated successfully'
        response.headers['X-File-Size'] = str(file_size)
        response.headers['X-Export-Type'] = 'excel'
        
        return response
        
    except Exception as e:
        # print(f"Excel export error: {str(e)}")
        return jsonify({
            'error': f'Excel export failed: {str(e)}',
            'status': 'error'
        }), 500

# PDF export endpoint - returns downloadable PDF report for latest location data
def pdf_export_endpoint():
    try:
        file_path = generate_pdf_report()
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'Failed to generate PDF file',
                'status': 'error'
            }), 500
        
        # Get file size for better response info
        file_size = os.path.getsize(file_path)
        
        # print(f"PDF export successful: {file_path} ({file_size} bytes)")
        
        # Create response with custom headers
        response = send_file(
            file_path, 
            as_attachment=True, 
            download_name='weather_report.pdf',
            mimetype='application/pdf'
        )
        
        # Add custom headers for success message
        response.headers['X-Export-Status'] = 'success'
        response.headers['X-Export-Message'] = 'PDF report generated successfully with charts'
        response.headers['X-File-Size'] = str(file_size)
        response.headers['X-Export-Type'] = 'pdf'
        
        return response
        
    except Exception as e:
        # print(f"PDF export error: {str(e)}")
        return jsonify({
            'error': f'PDF export failed: {str(e)}',
            'status': 'error'
        }), 500

def generate_excel_export(latitude=None, longitude=None):
    # Generate Excel file with weather data for latest location or specified coordinates
    try:
        # print("Starting Excel export generation...")
        
        # Get data from database - use latest location if no coordinates specified
        if latitude is not None and longitude is not None:
            data = get_weather_data_by_location(latitude, longitude, days=2)
            # print(f"Filtering data for location: lat={latitude}, lon={longitude}")
        else:
            data = get_latest_location_data()
            # print("Getting data for the most recently saved location")
        
        if not data:
            location_msg = f" for location ({latitude}, {longitude})" if latitude and longitude else " for the latest location"
            raise ValueError(f"No weather data available for export{location_msg}")
        
        # print(f"Found {len(data)} records for Excel export")
        
        # Convert to DataFrame and format data
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create Excel file with auto-adjusted columns
        excel_file_path = os.path.join('exports', 'weather_data.xlsx')
        os.makedirs('exports', exist_ok=True)
        
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Weather Data', index=False)
            
            # Auto-adjust column widths for readability
            workbook = writer.book
            worksheet = writer.sheets['Weather Data']
            
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
        
        # print(f"Excel file generated successfully: {excel_file_path}")
        return excel_file_path
        
    except ValueError as e:
        # print(f"Excel generation validation error: {str(e)}")
        raise
    except Exception as e:
        # print(f"Excel generation error: {str(e)}")
        raise Exception(f"Failed to generate Excel export: {str(e)}")

def generate_pdf_report(latitude=None, longitude=None):
    # Generate PDF report with charts for latest location or specified coordinates
    try:
        # print("Starting PDF report generation...")
        
        # Get data from database - use latest location if no coordinates specified
        if latitude is not None and longitude is not None:
            data = get_weather_data_by_location(latitude, longitude, days=2)
            # print(f"Filtering data for location: lat={latitude}, lon={longitude}")
        else:
            data = get_latest_location_data()
            # print("Getting data for the most recently saved location")
        
        if not data:
            location_msg = f" for location ({latitude}, {longitude})" if latitude and longitude else " for the latest location"
            raise ValueError(f"No weather data available for PDF report{location_msg}")
        
        # print(f"Found {len(data)} records for PDF report")
        
        # Get location info from first record
        sample_record = data[0]
        report_lat = sample_record['latitude']
        report_lon = sample_record['longitude']
        # print(f"Generating report for location: {report_lat}, {report_lon}")
        
        # Convert to DataFrame and sort by timestamp
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Generate chart as base64 encoded image
        # print("Generating weather charts...")
        chart_base64 = generate_weather_chart(df)
        
        # Prepare metadata for template
        if not df.empty:
            lat = df.iloc[0]['latitude']
            lon = df.iloc[0]['longitude']
            date_range = f"{df['timestamp'].min().strftime('%Y-%m-%d %H:%M')} to {df['timestamp'].max().strftime('%Y-%m-%d %H:%M')}"
        else:
            lat, lon, date_range = 0, 0, "No data"
        
        # Create HTML content using template
        # print("Creating PDF from template...")
        html_content = create_pdf_html_template(chart_base64, lat, lon, date_range, len(df))
        
        # Generate PDF file
        pdf_file_path = os.path.join('exports', 'weather_report.pdf')
        os.makedirs('exports', exist_ok=True)
        
        # print("Converting HTML to PDF...")
        HTML(string=html_content).write_pdf(pdf_file_path)
        
        # print(f"PDF report generated successfully: {pdf_file_path}")
        return pdf_file_path
        
    except ValueError as e:
        # print(f"PDF generation validation error: {str(e)}")
        raise
    except Exception as e:
        # print(f"PDF generation error: {str(e)}")
        raise Exception(f"Failed to generate PDF report: {str(e)}")

def generate_weather_chart(df):
    # Generate matplotlib chart with temperature and humidity data, return as base64 image
    try:
        # print("Creating matplotlib charts...")
        
        plt.style.use('default')
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=Config.CHART_FIGURE_SIZE, dpi=Config.CHART_DPI)
        fig.suptitle('Weather Data Report - Last 48 Hours', fontsize=16, fontweight='bold')
        
        # Identify temperature and humidity columns
        temp_col = None
        humidity_col = None
        
        for col in df.columns:
            if 'temperature' in col.lower():
                temp_col = col
            elif 'humidity' in col.lower():
                humidity_col = col
        
        if not temp_col or not humidity_col:
            raise ValueError(f"Required columns not found. Available columns: {list(df.columns)}")
        
        # print(f"Using temperature column: {temp_col}")
        # print(f"Using humidity column: {humidity_col}")
        
        # Plot temperature data
        ax1.plot(df['timestamp'], df[temp_col], 
                color='#e74c3c', linewidth=2, marker='o', markersize=3, label='Temperature')
        ax1.set_ylabel('Temperature (°C)', fontsize=12)
        ax1.set_title('Temperature Over Time', fontsize=14)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Format temperature plot x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot humidity data
        ax2.plot(df['timestamp'], df[humidity_col], 
                color='#3498db', linewidth=2, marker='s', markersize=3, label='Humidity')
        ax2.set_ylabel('Relative Humidity (%)', fontsize=12)
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_title('Humidity Over Time', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Format humidity plot x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax2.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Convert chart to base64 encoded string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=Config.CHART_DPI, bbox_inches='tight')
        buffer.seek(0)
        
        chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Cleanup resources
        plt.close(fig)
        buffer.close()
        
        # print("Chart generated and encoded successfully")
        return chart_base64
        
    except ValueError as e:
        # print(f"Chart generation validation error: {str(e)}")
        raise
    except Exception as e:
        # print(f"Chart generation error: {str(e)}")
        raise Exception(f"Failed to generate weather chart: {str(e)}")

def create_pdf_html_template(chart_base64, latitude, longitude, date_range, record_count):
    """
    Create HTML template for PDF generation with embedded chart
    Returns: HTML string
    """
    
    try:
        print("🎨 Creating HTML template for PDF...")
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Weather Data Report</title>
            <style>
                @page {{
                    margin: 2cm;
                    size: A4;
                }}
                
                body {{
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    line-height: 1.5;
                    color: #2c3e50;
                    margin: 0;
                    background: #ffffff;
                }}
                
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #34495e;
                    padding-bottom: 25px;
                    margin-bottom: 35px;
                }}
                
                .header h1 {{
                    font-size: 32px;
                    font-weight: 300;
                    color: #2c3e50;
                    margin: 0 0 8px 0;
                    letter-spacing: -0.5px;
                }}
                
                .header .subtitle {{
                    font-size: 16px;
                    color: #7f8c8d;
                    font-weight: 400;
                    margin: 0;
                }}
                
                .report-info {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin-bottom: 35px;
                }}
                
                .info-section {{
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 20px;
                }}
                
                .info-section h3 {{
                    margin: 0 0 15px 0;
                    font-size: 16px;
                    font-weight: 600;
                    color: #2c3e50;
                    border-bottom: 1px solid #dee2e6;
                    padding-bottom: 8px;
                }}
                
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 6px 0;
                    border-bottom: 1px solid #f1f3f4;
                }}
                
                .info-row:last-child {{
                    border-bottom: none;
                }}
                
                .info-label {{
                    font-weight: 500;
                    color: #495057;
                    min-width: 120px;
                }}
                
                .info-value {{
                    color: #2c3e50;
                    text-align: right;
                    font-weight: 400;
                }}
                
                .summary {{
                    background: #f8f9fa;
                    border-left: 4px solid #6c757d;
                    padding: 20px;
                    margin: 35px 0;
                    border-radius: 0 6px 6px 0;
                }}
                
                .summary h3 {{
                    margin: 0 0 12px 0;
                    font-size: 18px;
                    font-weight: 500;
                    color: #2c3e50;
                }}
                
                .summary p {{
                    margin: 0;
                    color: #495057;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                
                .chart-section {{
                    margin: 40px 0;
                    text-align: center;
                }}
                
                .chart-section h3 {{
                    font-size: 20px;
                    font-weight: 500;
                    color: #2c3e50;
                    margin: 0 0 25px 0;
                    text-align: center;
                }}
                
                .chart-container {{
                    background: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    display: inline-block;
                    max-width: 100%;
                }}
                
                .chart-container img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                }}
                
                .footer {{
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
                
                .footer p {{
                    margin: 5px 0;
                }}
                
                .generated-time {{
                    font-style: italic;
                    font-size: 11px;
                    color: #adb5bd;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Weather Data Report</h1>
                <p class="subtitle">Meteorological Analysis and Trends</p>
            </div>
            
            <div class="report-info">
                <div class="info-section">
                    <h3>Location Details</h3>
                    <div class="info-row">
                        <span class="info-label">Latitude:</span>
                        <span class="info-value">{latitude}°</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Longitude:</span>
                        <span class="info-value">{longitude}°</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Data Points:</span>
                        <span class="info-value">{record_count} records</span>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>Report Information</h3>
                    <div class="info-row">
                        <span class="info-label">Time Period:</span>
                        <span class="info-value">48 hours</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Date Range:</span>
                        <span class="info-value">{date_range}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Data Source:</span>
                        <span class="info-value">Open-Meteo API</span>
                    </div>
                </div>
            </div>
            
            <div class="summary">
                <h3>Executive Summary</h3>
                <p>This report presents a comprehensive analysis of meteorological conditions for the specified coordinates over a 48-hour observation period. The data includes temperature variations and relative humidity measurements collected at hourly intervals, providing detailed insights into local weather patterns and environmental conditions.</p>
            </div>
            
            <div class="chart-section">
                <h3>Meteorological Trends</h3>
                <div class="chart-container">
                    <img src="data:image/png;base64,{chart_base64}" alt="Weather Data Analysis Chart" />
                </div>
            </div>
            
            <div class="footer">
                <p><strong>Weather Data Service API</strong> | Automated Report Generation</p>
                <p>Data provided by Open-Meteo Weather Service</p>
                <p class="generated-time">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
            </div>
        </body>
        </html>
        """
        
        print("✅ HTML template created successfully")
        return html_template
        
    except Exception as e:
        print(f"❌ HTML template creation error: {str(e)}")
        raise Exception(f"Failed to create PDF HTML template: {str(e)}")