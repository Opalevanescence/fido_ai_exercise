# Decided this file was short enough to leave everything here, but I've added notes about how I would break a larger backend up into particular folders
import base64
import json
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from pydantic import AfterValidator, BaseModel, ValidationError
from typing_extensions import Annotated
from sqlalchemy import create_engine, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import declarative_base, joinedload, mapped_column, Mapped, relationship, sessionmaker, Session


app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./audio.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create validation checks
# Place in a helper folder
def has_value(value: str) -> str:
  if len(value) > 0:
    return value
  raise ValueError("A field is empty")

def has_values(values: list) -> list:
  if not values:
    raise ValueError("List of audio files is empty")
  return values

# Define Classes
# Decided to give File and Session a one to many relationship
# Place in models folder
class CustomException(Exception):
  def __init__(self, status_code: int, message: str):
    self.status_code = status_code
    self.message = message

class AudioFileInput(BaseModel):
  file_name: Annotated[str, AfterValidator(has_value)]
  encoded_audio: Annotated[str, AfterValidator(has_value)]
class AudioSessionInput(BaseModel):
  session_id: Annotated[str, AfterValidator(has_value)]
  timestamp: datetime
  audio_files: Annotated[List[AudioFileInput], AfterValidator(has_values)]

class AudioFile(Base):
  __tablename__ = "audio_file_table"
  id: Mapped[int] = mapped_column(primary_key = True, autoincrement=True)
  audio_session_id: Mapped[str] = mapped_column(ForeignKey("audio_session_table.id"))
  audio_session: Mapped["AudioSession"] = relationship(back_populates="audio_files")
  file_name = Column(String, nullable=False)
  file_length = Column(Float, nullable=False)

class AudioSession(Base):
  __tablename__ = "audio_session_table"
  id: Mapped[str] = mapped_column(primary_key = True)
  timestamp = Column(DateTime, nullable=False)
  audio_files: Mapped[List["AudioFile"]] = relationship(back_populates="audio_session")

# Create DB with defined classes
Base.metadata.drop_all(bind=engine) # Included for testing purposes. improvement would be to add a flag based on test env
Base.metadata.create_all(bind=engine)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


# Customize exception handlers
# Makes validation handler return the error format expected by the exercise prompt
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
  return JSONResponse(
    status_code=422,
    # Keep the detailed message response if this is for internal use, but limit the message if endpoint available to people outside the company
    content=jsonable_encoder({"status": "error", "message": str(exc)}) 
  )
# Makes explicitely added handlers also match excerise prompt format
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
  return JSONResponse(
    status_code=exc.status_code,
    content=jsonable_encoder({"status": "error", "message": exc.message}) 
  )

@app.get("/")
async def root():
  return {"message": "Hello World"}

# Created as a sanity check that DB was working as expected
@app.get("/processed_audio")
async def processed_audio(db: Session = Depends(get_db)):
  try:
    processed_files = db.query(AudioFile).options(joinedload(AudioFile.audio_session)).all()
    result = [{"file_name": file.file_name, "file_length": file.file_length, "session_id": file.audio_session.id, "timestamp": file.audio_session.timestamp } for file in processed_files]
    return { 
      "status": "success", 
      "processed_files": result
    }
  except ValueError as e:
    raise error("Failed to get audio files")


# - Place route handling in a routes folder that directs to controllers etc.
# - Add a response model
@app.post("/process-audio/")
async def process_audio(input: AudioSessionInput, db: Session = Depends(get_db)):
  try:
    audio_files = input.audio_files

    # Store session metadata
    # improvement: check if audio session id already exists. throw an error if it does.
    audio_session = AudioSession(
      id = input.session_id,
      timestamp = input.timestamp
    )
    db.add(audio_session)

    processed_files = []
    for file in input.audio_files:
      # Decode audio files
      try:
        print("HELLO")
        audio = base64.b64decode(file.encoded_audio)
      except:
        print("EXCEPTION")
        raise CustomException(
          status_code=422,
          message="Invalid base64 encoded audio"
        )
      
      # Store audio metadata with relation to session
      # NOTE: I assumed for the purpose of this exercise that the audio data was Base64-encoded, since that's specified multiple times in the prompt.
      # Would decode differently if numpy arrays of int16 dtype were the audio data passed through
      # Also assumed length in seconds should be calculated based on decoded data
      length_seconds = len(audio) / 4000
      audio_file_data = AudioFile(
        audio_session_id = audio_session.id,
        file_name = file.file_name,
        file_length = len(audio) / 4000
      )
      db.add(audio_file_data)

      processed_files.append({"file_name": file.file_name, "length_seconds": length_seconds})
    db.commit()
    return { 
      "status": "success", 
      "processed_files": processed_files
    }
  except ValueError as e:
    db.rollback()
    raise CustomException(
      status_code=400,
      message="Generic error processing audio. Try again."
    )
    
