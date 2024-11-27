# AI Automation Readiness Scorecard

A web-based assessment tool to evaluate an organization's readiness for AI automation implementation.

## Features

- 10-question assessment covering key areas of AI readiness
- Dynamic scoring system
- Personalized recommendations based on score
- Email collection for follow-up
- Database storage of responses

## Score Categories

1. Transformation Aspirants (0-11 points)
2. Growth Seekers (12-22 points)
3. Tech-Savvy Optimizers (23-33 points)
4. Efficiency Champions (34-44 points)

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python init_db.py
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Deployment

This application is configured for deployment on Render.com:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables:
     - SECRET_KEY: [Generate a secure random key]
     - RENDER: true

## Technologies Used

- Flask (Python web framework)
- SQLAlchemy (Database ORM)
- Tailwind CSS (Styling)
- SQLite (Local development)
- PostgreSQL (Production)
"# AI-readiness-assessment" 
