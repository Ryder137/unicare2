from datetime import datetime
from . import db

class CDRISCAssessment(db.Model):
    """Model for CD-RISC 10-item resilience assessment results"""
    __tablename__ = 'cdrisc_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    assessment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_score = db.Column(db.Integer, nullable=False)
    
    # Individual question responses (0-4)
    q1_adapt_change = db.Column(db.Integer, nullable=False)
    q2_handle_anything = db.Column(db.Integer, nullable=False)
    q3_humor = db.Column(db.Integer, nullable=False)
    q4_achieve_goals = db.Column(db.Integer, nullable=False)
    q5_focus_under_pressure = db.Column(db.Integer, nullable=False)
    q6_persist_challenges = db.Column(db.Integer, nullable=False)
    q7_handle_unpleasant_feelings = db.Column(db.Integer, nullable=False)
    q8_bounce_back = db.Column(db.Integer, nullable=False)
    q9_think_clearly_stress = db.Column(db.Integer, nullable=False)
    q10_take_control = db.Column(db.Integer, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert the assessment to a dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'assessment_date': self.assessment_date.isoformat(),
            'total_score': self.total_score,
            'responses': {
                'q1_adapt_change': self.q1_adapt_change,
                'q2_handle_anything': self.q2_handle_anything,
                'q3_humor': self.q3_humor,
                'q4_achieve_goals': self.q4_achieve_goals,
                'q5_focus_under_pressure': self.q5_focus_under_pressure,
                'q6_persist_challenges': self.q6_persist_challenges,
                'q7_handle_unpleasant_feelings': self.q7_handle_unpleasant_feelings,
                'q8_bounce_back': self.q8_bounce_back,
                'q9_think_clearly_stress': self.q9_think_clearly_stress,
                'q10_take_control': self.q10_take_control
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
