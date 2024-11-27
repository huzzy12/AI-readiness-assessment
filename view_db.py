from app import app, db, User, Response

def view_database():
    with app.app_context():
        print("\n=== Users ===")
        users = User.query.all()
        for user in users:
            print(f"\nUser ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Created at: {user.created_at}")
            
            print("\nResponses:")
            responses = Response.query.filter_by(user_id=user.id).all()
            for response in responses:
                print(f"  Question {response.question_number}: {response.answer} (Score: {response.score})")

if __name__ == "__main__":
    view_database()
