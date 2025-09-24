"""
Minimal Flask app to test basic functionality
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'message': 'Hello, World!',
        'status': 'success',
        'python_version': '3.13.4',
        'flask_version': '3.1.2'
    })

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, port=5001)
