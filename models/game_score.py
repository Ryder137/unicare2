from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class GameScore:
    id: int
    client_id: str  # Changed from user_id to client_id
    game_name: str
    score: int
    level: Optional[int] = None
    time_spent: Optional[int] = None  # in seconds
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        # Handle both user_id and client_id for backward compatibility
        client_id = data.get('client_id')
        if client_id is None and 'user_id' in data:
            client_id = data.get('user_id')
            
        return cls(
            id=data.get('id'),
            client_id=client_id,
            game_name=data.get('game_name'),
            score=data.get('score'),
            level=data.get('level'),
            time_spent=data.get('time_spent'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None
        )
    
    def to_dict(self):
        return {
            'client_id': self.client_id,
            'game_name': self.game_name,
            'score': self.score,
            'level': self.level,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
