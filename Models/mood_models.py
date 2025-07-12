from pydantic import BaseModel

class MoodRequest(BaseModel):
    user_mood: str

class MoodResponse(BaseModel):
    suggestion: str
    encouragement: str
    
    