from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# ====================
# Message Schemas
# ====================
class MessageBase(BaseModel):
    content: str
    role: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ====================
# User Schemas
# ====================

# A simplified User schema for nesting inside Conversation to prevent recursion
class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_verified: bool

    class Config:
        from_attributes = True

# ====================
# Conversation Schemas
# ====================
class ConversationBase(BaseModel):
    title: str

class ConversationUpdate(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    messages: List[Message] = []
    user: UserInDB 

    class Config:
        from_attributes = True

# ====================
# Main User Schema
# ====================
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_verified: bool
    conversations: List[Conversation] = []

    class Config:
        from_attributes = True

# ====================
# Token Schemas
# ====================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# IMPORTANT: Rebuild models to resolve circular dependencies
User.model_rebuild()
Conversation.model_rebuild()

