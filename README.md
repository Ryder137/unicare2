# UNICARE - A Gamified Support System for Mental Health and Emotional Resilience

UNICARE is a comprehensive digital support system designed to help students manage emotional stressors, improve resilience, and engage in consistent mental self-care through gamification and AI-powered support.

## Features

- Secure user authentication and progress tracking
- Emotional self-assessment module
- AI-powered chatbot for emotional support
- Personalized wellness recommendations
- Data visualization dashboard
- Optional peer-support community
- Gamification elements (badges, progress tracking)
- Admin dashboard for system management

## Tech Stack

- Frontend: HTML5, CSS3, JavaScript (Vanilla)
- Backend: Python 3.8+, Flask
- Database: MongoDB
- AI: OpenAI API for chatbot functionality
- Authentication: Flask-Login
- Charts: Chart.js for data visualization

## Project Structure

```
unicare/
├── __init__.py         # Application factory and extensions
├── run.py             # Development server entry point
├── wsgi.py           # Production WSGI entry point
├── config.py         # Configuration settings
├── requirements.txt  # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── .env.example     # Example environment variables
├── .gitignore
└── README.md
```

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB 4.4 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/unicare.git
cd unicate
```

### 2. Create and Activate Virtual Environment
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# For development, also install:
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables
Copy the example environment file and update the values:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```
FLASK_APP=wsgi.py
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb://localhost:27017/unicare
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5. Initialize the Database
```bash
# Create the database and collections
python -m scripts.init_db
```

### 6. Run the Application
```bash
# Development server
python run.py

# Or using Flask CLI
flask run
```

The application will be available at `http://localhost:5000`

### 7. Access Admin Interface
1. Open `http://localhost:5000/admin`
2. Login with the default admin credentials (or create a new admin user)

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
# Auto-format code
black .

# Check for style issues
flake8
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head
```

## Deployment

### Production with Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### Environment Variables for Production
Make sure to set these in your production environment:
- `FLASK_ENV=production`
- `FLASK_DEBUG=0`
- `SECRET_KEY` (a secure random string)
- `MONGODB_URI` (production MongoDB connection string)
- Other production-specific settings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
   ```bash
   python app.py
   ```

6. Access the application:
   Open your web browser and go to:
   http://localhost:5000

## Usage

1. Register a new account:
   - Click on "Register" in the navigation bar
   - Fill in your username, email, and password
   - Click "Register"

2. Login:
   - Click on "Login" in the navigation bar
   - Enter your credentials
   - Click "Login"

3. Dashboard Features:
   - Complete daily emotional assessments
   - Chat with the UNICARE support bot
   - View your mood progress and statistics
   - Access personalized recommendations
   - Track your streak and achievements

## Database Setup

1. Install MongoDB:
   - Download and install MongoDB Community Server from https://www.mongodb.com/try/download/community
   - Follow the installation instructions for your operating system

2. Start MongoDB:
   - On Windows: Start MongoDB service through Services
   - On Linux: Start MongoDB service with `sudo service mongod start`
   - On macOS: Start MongoDB with `brew services start mongodb-community`

3. Verify MongoDB connection:
   ```bash
   python -c "from flask_pymongo import PyMongo; import os; print('MongoDB connection successful!')"
   ```

## Project Structure

```
unicare/
├── backend/           # Node.js Express backend
├── frontend/          # React frontend
├── docs/             # Documentation
└── tests/            # Test files
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
