from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List,AsyncGenerator
from starlette.responses import StreamingResponse
from app.auth import security
from app.models import schemas
from app.services import chat as chat_service
from app.utils.database import get_db
from app.rag.generate_answer import generate_answer

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@router.post("/conversations", response_model=schemas.Conversation)
def create_conversation_for_user(
    current_user: schemas.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new conversation for the current logged-in user."""
    return chat_service.create_conversation(db=db, user_id=current_user.id)

@router.get("/conversations", response_model=List[schemas.Conversation])
def read_user_conversations(
    current_user: schemas.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all conversations for the current logged-in user."""
    return chat_service.get_conversations_by_user(db=db, user_id=current_user.id)

@router.get("/conversations/{conversation_id}", response_model=schemas.Conversation)
def get_conversation_by_id(
    conversation_id: int,
    current_user: schemas.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves a single conversation by its ID for the current user."""
    conversation = chat_service.get_conversation(db=db, conversation_id=conversation_id, user_id=current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.put("/conversations/{conversation_id}", response_model=schemas.Conversation)
def update_conversation(
    conversation_id: int,
    conversation_update: schemas.ConversationUpdate,
    current_user: schemas.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Updates a conversation's title."""
    updated_conv = chat_service.update_conversation_title(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        new_title=conversation_update.title
    )
    if not updated_conv:
        raise HTTPException(status_code=404, detail="Conversation not found or you don't have access")
    return updated_conv

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_route(
    conversation_id: int,
    current_user: schemas.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a conversation."""
    success = chat_service.delete_conversation(db=db, conversation_id=conversation_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found or you don't have access")
    return

@router.post("/conversations/{conversation_id}/messages")
async def post_message_to_conversation_stream(
    conversation_id: int,
    message: schemas.MessageCreate,
    current_user: schemas.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Posts a message, streams the RAG response back, and then saves the full response.
    """
    # 1. Ensure the user has access to this conversation
    conversation = chat_service.get_conversation(db=db, conversation_id=conversation_id, user_id=current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found or you don't have access")

    # 2. Save the user's message to the database immediately
    chat_service.add_message_to_conversation(db=db, conversation_id=conversation_id, message=message)

    # 3. Create an async generator to stream the response and save it at the end
    async def stream_and_save() -> AsyncGenerator[str, None]:
        full_response_content = ""
        async for chunk in generate_answer(query=message.content, thread_id=str(conversation_id)):
            full_response_content += chunk
            yield chunk
        
        # 4. After the stream is complete, save the full assistant message
        if full_response_content:
            assistant_message = schemas.MessageCreate(content=full_response_content, role="assistant")
            chat_service.add_message_to_conversation(db=db, conversation_id=conversation_id, message=assistant_message)

    # 5. Return the streaming response to the client
    return StreamingResponse(stream_and_save(), media_type="text/plain")


