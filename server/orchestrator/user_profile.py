"""
User Profile Management for Personalization
"""
from typing import Dict, Any

# In-memory user profile store (replace with DB in production)
user_profiles: Dict[str, Dict[str, Any]] = {}

def get_user_profile(user_id: str) -> Dict[str, Any]:
    return user_profiles.get(user_id, {
        "persona": "default",
        "preferred_style": "concise",
        "preferred_agent": None,
        "preferred_model": None,
        "language": "en"
    })

def set_user_profile(user_id: str, profile: Dict[str, Any]):
    user_profiles[user_id] = profile

# Update a single preference
def update_user_preference(user_id: str, key: str, value: Any):
    profile = get_user_profile(user_id)
    profile[key] = value
    user_profiles[user_id] = profile
