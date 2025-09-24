"""
Minimal Flask test application.
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Minimal Flask app is working!"

if __name__ == '__main__':
    print("Starting minimal Flask app...")
    app.run(debug=True, port=5001)
