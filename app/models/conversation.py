"""
Pydantic models for conversations
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid


class Message(BaseModel):
    """Schema for a chat message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a conversation"""
    title: Optional[str] = "New Conversation"


class ConversationMetadata(BaseModel):
    """Schema for conversation metadata"""
    id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Conversation(BaseModel):
    """Schema for a conversation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Conversation"
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
    
    def add_message(self, role: Literal["user", "assistant"], content: str, sources: List[str] = None):
        """Add a message to the conversation"""
        message = Message(
            role=role,
            content=content,
            sources=sources or []
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_metadata(self) -> ConversationMetadata:
        """Get conversation metadata"""
        return ConversationMetadata(
            id=self.id,
            title=self.title,
            message_count=len(self.messages),
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class ConversationListResponse(BaseModel):
    """Schema for conversation list response"""
    conversations: List[ConversationMetadata]
    total: int
