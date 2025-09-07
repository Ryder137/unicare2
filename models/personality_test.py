from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class PersonalityTestResult:
    id: int
    client_id: str  # Changed from user_id to client_id
    test_date: datetime
    personality_type: str
    traits: Dict[str, float]
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict):
        # Handle both user_id and client_id for backward compatibility
        client_id = data.get('client_id')
        if client_id is None and 'user_id' in data:
            client_id = data.get('user_id')
            
        return cls(
            id=data.get('id'),
            client_id=client_id,
            test_date=datetime.fromisoformat(data.get('test_date')) if data.get('test_date') else None,
            personality_type=data.get('personality_type'),
            traits=data.get('traits', {}),
            insights=data.get('insights', []),
            recommendations=data.get('recommendations', [])
        )
    
    def to_dict(self):
        return {
            'client_id': self.client_id,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'personality_type': self.personality_type,
            'traits': self.traits,
            'insights': self.insights,
            'recommendations': self.recommendations
        }
