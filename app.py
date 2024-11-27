from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, User, Response
import os

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Database configuration
if os.environ.get('RENDER'):
    # Use PostgreSQL on Render
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
else:
    # Use SQLite locally
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_scorecard.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables before first request
@app.before_first_request
def create_tables():
    db.create_all()

# Quiz questions
QUESTIONS = [
    {
        "id": 1,
        "text": "How would you rate the speed of your current business processes?",
        "options": [
            {"text": "Very fast, No delays", "score": 5},
            {"text": "Fast, Minor delays", "score": 3},
            {"text": "Moderate, Noticeable delays", "score": 1},
            {"text": "Slow, Significant delays", "score": 0}
        ]
    },
    {
        "id": 2,
        "text": "How would you rate the efficiency of your current business processes?",
        "options": [
            {"text": "Very efficient, No waste", "score": 5},
            {"text": "Efficient, Minimal waste", "score": 3},
            {"text": "Moderately efficient, Some waste", "score": 1},
            {"text": "Inefficient, Significant waste", "score": 0}
        ]
    },
    {
        "id": 3,
        "text": "How much time do your employees spend on repetitive, manual tasks each week?",
        "options": [
            {"text": "Less than 5 hours", "score": 5},
            {"text": "5-10 hours", "score": 3},
            {"text": "10-20 hours", "score": 1},
            {"text": "20+ hours", "score": 0}
        ]
    },
    {
        "id": 4,
        "text": "Which of these areas do you find most challenging in your operations?",
        "options": [
            {"text": "Data management and analysis", "score": 3},
            {"text": "Customer support and communication", "score": 3},
            {"text": "Inventory and supply chain", "score": 3},
            {"text": "Workflow automation and task management", "score": 3}
        ]
    },
    {
        "id": 5,
        "text": "How comfortable are you with implementing new technologies in your business?",
        "options": [
            {"text": "Very comfortable, we regularly adopt new technologies.", "score": 5},
            {"text": "Open to new technologies but proceed with caution.", "score": 3},
            {"text": "Neutral, we only adopt if it's absolutely necessary.", "score": 1},
            {"text": "Uncomfortable, we prefer to stick with our current systems.", "score": 0}
        ]
    },
    {
        "id": 6,
        "text": "Do you currently use any AI-powered tools in your business?",
        "options": [
            {"text": "Yes, we use AI various tools.", "score": 5},
            {"text": "We are in the process of exploring AI tools.", "score": 3},
            {"text": "No, we have not explored AI tools yet.", "score": 0}
        ]
    },
    {
        "id": 7,
        "text": "What is your biggest concern regarding AI adoption?",
        "options": [
            {"text": "Implementation complexity and disruption of current operations", "score": 3},
            {"text": "Security and privacy concerns", "score": 3},
            {"text": "Costs justification and ROI", "score": 3},
            {"text": "Employee engagement and training", "score": 3}
        ]
    },
    {
        "id": 8,
        "text": "Do you find it difficult to maintain quality and customer satisfaction as your business grows?",
        "options": [
            {"text": "Not at all, we have scalable systems in place", "score": 5},
            {"text": "Occasionally, we face challenges in some areas", "score": 3},
            {"text": "Frequently, we struggle to keep up with demand", "score": 1},
            {"text": "Significantly, growth heavily impacts quality and satisfaction", "score": 0}
        ]
    },
    {
        "id": 9,
        "text": "How do you currently track and measure the key performance indicators (KPIs) of your business?",
        "options": [
            {"text": "We have robust data-driven systems to monitor KPIs", "score": 5},
            {"text": "We track KPIs but not consistently or comprehensively", "score": 3},
            {"text": "We have limited data tracking, but need more in-depth analysis", "score": 1},
            {"text": "We do not have a formal KPI tracking system in place", "score": 0}
        ]
    },
    {
        "id": 10,
        "text": "What are your primary growth objectives for the next 12 months?",
        "options": [
            {"text": "Increase revenue", "score": 3},
            {"text": "Reduce costs", "score": 3},
            {"text": "Build systems/Automate processes", "score": 3},
            {"text": "Improve customer/client retention", "score": 3}
        ]
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    if 'current_question' not in session:
        session['current_question'] = 1
        session['total_score'] = 0
        session['responses'] = []
    
    question_id = session['current_question']
    if question_id > len(QUESTIONS):
        return redirect(url_for('email'))
    
    question = QUESTIONS[question_id - 1]
    progress = ((question_id - 1) / len(QUESTIONS)) * 100
    return render_template('quiz.html', question=question, progress=progress)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if not request.is_json:
        return jsonify({"error": "Invalid request"}), 400

    data = request.get_json()
    question_id = session.get('current_question', 1)
    score = int(data.get('score', 0))
    
    # Get the selected answer text from the current question
    current_question = QUESTIONS[question_id - 1]
    selected_option = next(
        (option for option in current_question['options'] if option['score'] == score),
        None
    )
    
    if selected_option:
        answer_text = selected_option['text']
        session['responses'].append({
            'question': question_id,
            'answer': answer_text,
            'score': score
        })
        
        session['total_score'] = session.get('total_score', 0) + score
        session['current_question'] = question_id + 1
        
        if session['current_question'] > len(QUESTIONS):
            return jsonify({"redirect": url_for('email')})
        
        return jsonify({"redirect": url_for('quiz')})
    
    return jsonify({"error": "Invalid answer"}), 400

@app.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return redirect(url_for('email'))
            
        # Save user and responses
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
        
        for response in session.get('responses', []):
            new_response = Response(
                user_id=user.id,
                question_number=response['question'],
                answer=response['answer'],
                score=response['score']
            )
            db.session.add(new_response)
        db.session.commit()
        
        total_score = session.get('total_score', 0)
        session.clear()
        
        # Determine result page based on total score
        if total_score <= 11:
            return redirect(url_for('result_transformation_aspirant'))
        elif total_score <= 22:
            return redirect(url_for('result_growth_seeker'))
        elif total_score <= 33:
            return redirect(url_for('result_tech_savvy_optimizer'))
        else:
            return redirect(url_for('result_efficiency_champion'))
            
    return render_template('email.html')

@app.route('/result/transformation-aspirant')
def result_transformation_aspirant():
    return render_template('result_transformation_aspirant.html')

@app.route('/result/growth-seeker')
def result_growth_seeker():
    return render_template('result_growth_seeker.html')

@app.route('/result/tech-savvy-optimizer')
def result_tech_savvy_optimizer():
    return render_template('result_tech_savvy_optimizer.html')

@app.route('/result/efficiency-champion')
def result_efficiency_champion():
    return render_template('result_efficiency_champion.html')

if __name__ == '__main__':
    app.run(debug=True)
