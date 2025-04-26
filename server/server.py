from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import re

# Add backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.brain.brain import process_command

import time
import logging

# Configure logging first, before using the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('friday_server')

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)
# Create charts directory if it doesn't exist
charts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'charts'))
os.makedirs(charts_dir, exist_ok=True)

# Ensure the directory is writable - log and attempt to fix if not
try:
    test_file_path = os.path.join(charts_dir, 'test_write.txt')
    with open(test_file_path, 'w') as f:
        f.write('test')
    os.remove(test_file_path)
    logger.info(f"Charts directory is writable: {charts_dir}")
except Exception as e:
    logger.error(f"Charts directory may not be writable: {charts_dir}, Error: {str(e)}")
    # Log directory permissions
    if os.name == 'posix':  # Unix-like systems
        logger.info(f"Attempting to set directory permissions for {charts_dir}")
        try:
            import stat
            os.chmod(charts_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            logger.info("Permissions updated for charts directory")
        except Exception as e:
            logger.error(f"Failed to set permissions: {str(e)}")

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable CORS for all routes

@app.route('/api/friday', methods=['POST'])
def friday_endpoint():
    """Handle API requests to FRIDAY"""
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        user_message = data['message']
        logger.info(f"Received message: {user_message}")
        
        # Process the message using FRIDAY's brain
        start_time = time.time()
        response = process_command(user_message)
        processing_time = time.time() - start_time
        
        logger.info(f"Processing time: {processing_time:.2f} seconds")
        logger.info(f"Response: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
        
        # Check if response contains chart path - look for both stock and mutual fund charts
        chart_path = None
        
        # Debug: Log the first 200 chars of response to check for the chart marker
        logger.debug(f"Response first 200 chars: {response[:200]}")
        
        # Improved regex patterns with more flexible matching
        stock_chart_pattern = r'📊 STOCK CHART: (assets/charts/[^\s\n]+)'
        mf_chart_pattern = r'📊 MUTUAL FUND CHART: (assets/charts/[^\s\n]+)'
        
        stock_chart_match = re.search(stock_chart_pattern, response)
        mf_chart_match = re.search(mf_chart_pattern, response)
        
        if stock_chart_match:
            chart_path = stock_chart_match.group(1)
            logger.info(f"Found stock chart path: {chart_path}")
            # Remove the chart path line from the response
            response = re.sub(r'📊 STOCK CHART: assets/charts/[^\n]+\n\n', '', response)
        elif mf_chart_match:
            chart_path = mf_chart_match.group(1)
            logger.info(f"Found mutual fund chart path: {chart_path}")
            # Remove the chart path line from the response
            response = re.sub(r'📊 MUTUAL FUND CHART: assets/charts/[^\n]+\n\n', '', response)
        else:
            logger.info("No chart path found in response")
            
        # Check if the chart file actually exists
        if chart_path and not os.path.exists(chart_path):
            logger.error(f"Chart file not found: {chart_path}")
            # Set to None if file doesn't exist
            chart_path = None
            
        # Return the response as JSON
        return jsonify({
            'response': response,
            'processing_time': processing_time,
            'chart_path': chart_path
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred while processing your request',
            'details': str(e)
        }), 500

@app.route('/')
def index():
    """Serve the FRIDAY web interface"""
    return send_from_directory('../frontend', 'index.html')

# Add static file serving for the frontend
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../frontend', path)

# Add route for serving chart images
@app.route('/assets/charts/<path:filename>')
def serve_chart(filename):
    """Serve chart images from the assets/charts directory"""
    logger.info(f"Serving chart: {filename}")
    
    try:
        # Use correct absolute path instead of relative path
        chart_path = os.path.join(charts_dir, filename)
        
        # Check if file exists
        if not os.path.exists(chart_path):
            logger.error(f"Chart file not found: {chart_path}")
            return jsonify({
                'error': 'Chart not found'
            }), 404
            
        # Get the directory and filename separately for send_from_directory
        directory = os.path.dirname(chart_path)
        file = os.path.basename(chart_path)
        
        # Set caching headers for better performance
        response = send_from_directory(directory, file)
        
        # Cache for 1 hour, but allow revalidation
        response.headers['Cache-Control'] = 'public, max-age=3600'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response
    except Exception as e:
        logger.error(f"Error serving chart: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error serving chart',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    try:
        # Configure and start the server
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting FRIDAY server on port {port}")
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        sys.exit(1) 