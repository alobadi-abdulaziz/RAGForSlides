import sys
import os

# Add the project's root directory (Backend) to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # --- 1. Import CORS Middleware ---
from app.routes import users, chat
from app.utils.database import engine
from app.models import models

# This line creates the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG App API",
    description="Backend for the Retrieval-Augmented Generation web application.",
    version="1.0.0",
)

# --- 2. Add CORS Middleware Settings ---
# This allows your frontend (running on a different address) to communicate with the backend.
origins = [
    "*",  # Allows all origins, suitable for development.
          # For production, you should restrict this to your frontend's domain.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# --- End of CORS section ---


# Include the routers from the routes module
app.include_router(users.router)
app.include_router(chat.router)


@app.get("/", tags=["Root"])
def read_root():
    """A welcome message for the API root."""
    return {"message": "Welcome to the RAG App API!"}

