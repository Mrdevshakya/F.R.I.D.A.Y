"""
Test script for FRIDAY web server
This is a simplified version of server.py that doesn't require the full FRIDAY backend.
It responds with simple predefined answers for testing the web interface.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import logging
import random

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('friday_test_server')

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable CORS for all routes

# Sample responses
FRIDAY_RESPONSES = [
    "I'm processing that information now.",
    "According to my analysis, that would be correct.",
    "I've searched my database and found relevant information.",
    "That's an interesting question. Let me provide some insights.",
    "Based on my knowledge, I can confirm that's accurate.",
    "I've analyzed multiple sources for this information.",
    "My systems indicate that's a valid query.",
    "I'm cross-referencing this with my knowledge base.",
    "My calculations show that to be precise.",
    "Based on available data, that appears to be correct."
]

SPECIAL_RESPONSES = {
    "hello": "Hello! I'm FRIDAY, your personal AI assistant. How can I help you today?",
    "hi": "Hi there! How may I assist you?",
    "who are you": "I am FRIDAY - Female Replacement Intelligent Digital Assistant Youth. I'm designed to assist with information and tasks.",
    "what can you do": "I can answer questions, provide information, assist with tasks, and engage in conversation to the best of my abilities.",
    "thank you": "You're welcome! Is there anything else I can help you with?",
    "thanks": "Happy to help! Let me know if you need anything else.",
    "bye": "Goodbye! Have a great day.",
    "help": "I'm here to assist you. You can ask me questions, request information, or just chat. What would you like to know?"
}

@app.route('/api/friday', methods=['POST'])
def friday_endpoint():
    """Handle API requests to FRIDAY"""
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        user_message = data['message']
        logger.info(f"Received message: {user_message}")
        
        # Add a small delay to simulate processing
        time.sleep(random.uniform(0.5, 2.0))
        
        # Check for special responses
        for key, response in SPECIAL_RESPONSES.items():
            if key in user_message.lower():
                return jsonify({
                    'response': response,
                    'processing_time': random.uniform(0.5, 2.0)
                })
        
        # For other messages, return a random response
        response = random.choice(FRIDAY_RESPONSES)
        
        logger.info(f"Response: {response}")
        
        # Return the response as JSON
        return jsonify({
            'response': response,
            'processing_time': random.uniform(0.5, 2.0)
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

if __name__ == '__main__':
    try:
        # Configure and start the server
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting FRIDAY TEST server on port {port}")
        
        print(f"""
=========================================================
FRIDAY TEST SERVER
=========================================================
This is a test server that simulates FRIDAY's responses.
It does not require the full FRIDAY backend to run.

Server is running at: http://localhost:{port}
Press Ctrl+C to stop the server.
=========================================================
        """)
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}") 