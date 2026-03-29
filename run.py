"""Application entry point."""
import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'default'))


@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print('Database initialized.')


@app.cli.command('seed-db')
def seed_db():
    """Seed the database with sample data."""
    from app.models import Participant
    from app.utils import generate_registration_id
    from datetime import datetime, timedelta
    import random

    sample_data = [
        ('Alice Johnson', 'alice@example.com', '+1-555-0101', 'MIT', 'AI & Machine Learning Fundamentals'),
        ('Bob Smith', 'bob@example.com', '+1-555-0102', 'Stanford University', 'Web Development with Python'),
        ('Carol White', 'carol@example.com', '+1-555-0103', 'Google Inc.', 'Data Science & Analytics'),
        ('David Brown', 'david@example.com', '+1-555-0104', 'Harvard University', 'Cloud Computing & DevOps'),
        ('Eva Martinez', 'eva@example.com', '+1-555-0105', 'Amazon', 'Cybersecurity Essentials'),
        ('Frank Lee', 'frank@example.com', '+1-555-0106', 'UC Berkeley', 'Blockchain Technology'),
        ('Grace Kim', 'grace@example.com', '+1-555-0107', 'Microsoft', 'AI & Machine Learning Fundamentals'),
        ('Henry Davis', 'henry@example.com', '+1-555-0108', 'UCLA', 'Web Development with Python'),
    ]

    with app.app_context():
        db.create_all()
        for name, email, phone, org, seminar in sample_data:
            if not Participant.query.filter_by(email=email).first():
                p = Participant(
                    registration_id=generate_registration_id(),
                    name=name,
                    email=email,
                    phone=phone,
                    organization=org,
                    seminar=seminar,
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                db.session.add(p)
        db.session.commit()
        print(f'Seeded {len(sample_data)} sample registrations.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8001)
