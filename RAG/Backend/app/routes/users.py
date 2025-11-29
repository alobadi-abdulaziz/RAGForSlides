from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import security
from app.models import schemas
from app.services import users as user_service
# REMOVED: from app.services.email import send_verification_email  <-- لم نعد نحتاجه
from app.auth.security import create_verification_token, verify_token_and_get_email
from app.utils.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# --- MODIFIED: Registration Endpoint (Direct Activation) ---
@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db), request: Request = None):
    db_user_by_username = user_service.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user_by_email = user_service.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 1. Create the user
    new_user = user_service.create_user(db=db, user=user)
    
    # 2. Activate IMMEDIATELY (Skip Email)
    user_service.activate_user(db, user=new_user)
    
    # --- Email Logic Commented Out ---
    # token = create_verification_token(email=new_user.email)
    # verification_link = request.url_for("verify_user_email", token=token)
    # await send_verification_email([new_user.email], str(verification_link))

    return new_user

@router.get("/verify-email/{token}", response_model=schemas.User, name="verify_user_email")
def verify_user_email(token: str, db: Session = Depends(get_db)):
    email = verify_token_and_get_email(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user = user_service.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return user 

    return user_service.activate_user(db, user=user)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        # This shouldn't happen with direct activation, but kept for safety
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified."
        )

    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(security.get_current_user)):
    """Fetches the current logged-in user's details."""
    return current_user