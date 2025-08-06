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
- Backend: Python 3.x, Flask
- Database: MongoDB
- AI: OpenAI API for chatbot functionality
- Authentication: Flask-Login
- Charts: Chart.js for data visualization

## Setup and Installation

1. Prerequisites:
   - Python 3.8 or higher
   - MongoDB
   - Git

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/unicare.git
   cd unicare
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with:
   ```
   FLASK_SECRET_KEY=your_secret_key_here
   MONGODB_URI=mongodb://localhost:27017/unicare
   ```

5. Start the application:
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
