"""
Conversation Service - Conversation history management
"""
from pathlib import Path
from typing import List, Optional
import json
import logging
from datetime import datetime

from app.core.config import settings
from app.models.conversation import Conversation, ConversationMetadata, Message

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversation history"""
    
    @staticmethod
    def _get_conversation_file(conversation_id: str) -> Path:
        """Get path to conversation file"""
        return settings.conversations_dir / f"{conversation_id}.json"
    
    @staticmethod
    def create_conversation(title: str = "New Conversation") -> Conversation:
        """
        Tạo conversation mới
        
        Args:
            title: Conversation title
            
        Returns:
            Conversation object
        """
        conversation = Conversation(title=title)
        ConversationService.save_conversation(conversation)
        logger.info(f"Đã tạo conversation: {conversation.id}")
        return conversation
    
    @staticmethod
    def get_conversation(conversation_id: str) -> Optional[Conversation]:
        """
        Lấy conversation theo ID
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation or None
        """
        file_path = ConversationService._get_conversation_file(conversation_id)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse datetime strings
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
            for msg in data['messages']:
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
            
            return Conversation(**data)
            
        except Exception as e:
            logger.error(f"Lỗi khi load conversation {conversation_id}: {str(e)}")
            return None
    
    @staticmethod
    def save_conversation(conversation: Conversation):
        """
        Lưu conversation vào file
        
        Args:
            conversation: Conversation object
        """
        file_path = ConversationService._get_conversation_file(conversation.id)
        
        try:
            # Convert to dict and serialize datetime
            data = conversation.dict()
            data['created_at'] = data['created_at'].isoformat()
            data['updated_at'] = data['updated_at'].isoformat()
            
            for msg in data['messages']:
                msg['timestamp'] = msg['timestamp'].isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Đã lưu conversation: {conversation.id}")
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu conversation: {str(e)}")
            raise
    
    @staticmethod
    def list_conversations() -> List[ConversationMetadata]:
        """
        Lấy danh sách tất cả conversations
        
        Returns:
            List of ConversationMetadata
        """
        conversations = []
        
        for file_path in settings.conversations_dir.glob("*.json"):
            try:
                conversation_id = file_path.stem
                conversation = ConversationService.get_conversation(conversation_id)
                
                if conversation:
                    conversations.append(conversation.get_metadata())
                    
            except Exception as e:
                logger.error(f"Lỗi khi load conversation {file_path.name}: {str(e)}")
                continue
        
        # Sort by updated_at descending
        conversations.sort(key=lambda x: x.updated_at, reverse=True)
        
        return conversations
    
    @staticmethod
    def delete_conversation(conversation_id: str) -> bool:
        """
        Xóa conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful
        """
        file_path = ConversationService._get_conversation_file(conversation_id)
        
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            logger.info(f"Đã xóa conversation: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa conversation: {str(e)}")
            return False
    
    @staticmethod
    def add_message(
        conversation_id: str,
        role: str,
        content: str,
        sources: List[str] = None
    ) -> Optional[Message]:
        """
        Thêm message vào conversation
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant)
            content: Message content
            sources: Source documents
            
        Returns:
            Message object or None
        """
        conversation = ConversationService.get_conversation(conversation_id)
        
        if not conversation:
            return None
        
        message = conversation.add_message(role, content, sources or [])
        ConversationService.save_conversation(conversation)
        
        return message
    
    @staticmethod
    def export_conversation(conversation_id: str, format: str = "json") -> Optional[str]:
        """
        Export conversation to string
        
        Args:
            conversation_id: Conversation ID
            format: Export format (json/markdown)
            
        Returns:
            Exported string or None
        """
        conversation = ConversationService.get_conversation(conversation_id)
        
        if not conversation:
            return None
        
        if format == "json":
            return json.dumps(conversation.dict(), default=str, ensure_ascii=False, indent=2)
        
        elif format == "markdown":
            lines = [
                f"# {conversation.title}",
                f"\n**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Messages:** {len(conversation.messages)}\n",
                "---\n"
            ]
            
            for msg in conversation.messages:
                role_emoji = "👤" if msg.role == "user" else "🤖"
                lines.append(f"## {role_emoji} {msg.role.title()}")
                lines.append(f"\n{msg.content}\n")
                
                if msg.sources:
                    lines.append("\n**Sources:**")
                    for source in msg.sources:
                        lines.append(f"- {source}")
                
                lines.append(f"\n*{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*\n")
                lines.append("---\n")
            
            return "\n".join(lines)
        
        return None
    
    @staticmethod
    def auto_generate_title(conversation: Conversation) -> str:
        """
        Tự động tạo title từ first user message
        
        Args:
            conversation: Conversation object
            
        Returns:
            Generated title
        """
        if not conversation.messages:
            return "New Conversation"
        
        # Get first user message
        first_user_msg = next(
            (msg for msg in conversation.messages if msg.role == "user"),
            None
        )
        
        if not first_user_msg:
            return "New Conversation"
        
        # Use first 50 chars of message
        title = first_user_msg.content[:50]
        if len(first_user_msg.content) > 50:
            title += "..."
        
        return title
