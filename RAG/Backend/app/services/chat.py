from sqlalchemy.orm import Session
from app.models import models, schemas

def get_conversations_by_user(db: Session, user_id: int):
    """Retrieves all conversations for a specific user."""
    return db.query(models.Conversation).filter(models.Conversation.user_id == user_id).all()

def get_conversation(db: Session, conversation_id: int, user_id: int):
    """Retrieves a single conversation by its ID, ensuring it belongs to the user."""
    return db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == user_id
    ).first()

def create_conversation(db: Session, user_id: int, title: str = "محادثة جديدة"):
    """Creates a new conversation for a user."""
    db_conversation = models.Conversation(user_id=user_id, title=title)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def add_message_to_conversation(db: Session, conversation_id: int, message: schemas.MessageCreate):
    """Adds a new message to a conversation."""
    db_message = models.Message(**message.model_dump(), conversation_id=conversation_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_conversation_title(db: Session, conversation_id: int, user_id: int, new_title: str):
    """Updates the title of a specific conversation for a user."""
    db_conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == user_id
    ).first()

    if db_conversation:
        db_conversation.title = new_title
        db.commit()
        db.refresh(db_conversation)
    return db_conversation

def delete_conversation(db: Session, conversation_id: int, user_id: int):
    """Deletes a specific conversation and its messages for a user."""
    db_conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == user_id
    ).first()

    if db_conversation:
        # SQLAlchemy with cascading delete will handle messages automatically
        db.delete(db_conversation)
        db.commit()
        return True
    return False

