from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class GuidanceCounselor:
    """Represents a guidance counselor in the system."""
    user_id: str
    license_number: str
    specialization: str = ""
    bio: str = ""
    years_of_experience: Optional[int] = None
    education: str = ""
    languages_spoken: List[str] = field(default_factory=list)
    is_available: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GuidanceCounselor':
        """Create a GuidanceCounselor instance from a dictionary."""
        return cls(
            id=str(data.get('id')),
            user_id=str(data['user_id']),
            license_number=data['license_number'],
            specialization=data.get('specialization', ''),
            bio=data.get('bio', ''),
            years_of_experience=data.get('years_of_experience'),
            education=data.get('education', ''),
            languages_spoken=data.get('languages_spoken', []),
            is_available=bool(data.get('is_available', True)),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the GuidanceCounselor instance to a dictionary."""
        return {
            'id': str(self.id) if self.id else None,
            'user_id': str(self.user_id),
            'license_number': self.license_number,
            'specialization': self.specialization,
            'bio': self.bio,
            'years_of_experience': self.years_of_experience,
            'education': self.education,
            'languages_spoken': self.languages_spoken,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
