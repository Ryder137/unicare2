"""
A simple Flask application to test the basic setup.
"""
from flask import Flask, jsonify

# Create a simple Flask application
app = Flask(__name__)

# Configure the application
app.config.update(
    SECRET_KEY='test-secret-key',
    DEBUG=True
)

# Add a simple route
@app.route('/')
def hello():
    return jsonify({
        'message': 'Hello, UNICARE!',
        'status': 'success',
        'version': '1.0.0'
    })

# Run the application
if __name__ == '__main__':
    print("Starting test Flask application...")
    print("Visit http://localhost:5001 in your browser")
    app.run(debug=True, port=5001)
