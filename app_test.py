from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World! The Flask app is working!"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
