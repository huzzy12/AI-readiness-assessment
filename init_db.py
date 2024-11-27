from app import app, db

with app.app_context():
    # Drop all existing tables
    db.drop_all()
    # Create new tables
    db.create_all()
    
print("Database initialized successfully!")
