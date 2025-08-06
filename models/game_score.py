from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class GameScore:
    id: int
    user_id: str
    game_name: str
    score: int
    level: Optional[int] = None
    time_spent: Optional[int] = None  # in seconds
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            game_name=data.get('game_name'),
            score=data.get('score'),
            level=data.get('level'),
            time_spent=data.get('time_spent'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None
        )
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'game_name': self.game_name,
            'score': self.score,
            'level': self.level,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
