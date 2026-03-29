"""Database models."""
from datetime import datetime

from app import db


class Participant(db.Model):
    """Participant registration model."""
    __tablename__ = 'participants'

    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    organization = db.Column(db.String(150), nullable=False)
    seminar = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    qr_code_path = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Participant {self.registration_id}: {self.name}>'

    def to_dict(self):
        """Serialize participant to dictionary."""
        return {
            'id': self.id,
            'registration_id': self.registration_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'organization': self.organization,
            'seminar': self.seminar,
            'registered_at': self.timestamp.isoformat(),
        }
