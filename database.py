from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    content_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    attribution = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    llm_score = db.Column(db.Float, nullable=False)
    signals = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='classified')
    
    appeals = db.relationship('Appeal', backref='audit_log', lazy=True)

    def to_dict(self):
        return {
            'content_id': self.content_id,
            'creator_id': self.creator_id,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'attribution': self.attribution,
            'confidence': self.confidence,
            'llm_score': self.llm_score,
            'signals': self.signals,
            'status': self.status
        }

class Appeal(db.Model):
    __tablename__ = 'appeals'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.String(36), db.ForeignKey('audit_logs.content_id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



