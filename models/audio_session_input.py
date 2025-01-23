from datetime import datetime
from typing import List
from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated

from models.audio_file_input import AudioFileInput
from validator.has_value import has_value
from validator.has_values import has_values

class AudioSessionInput(BaseModel):
  session_id: Annotated[str, AfterValidator(has_value)]
  timestamp: datetime
  audio_files: Annotated[List[AudioFileInput], AfterValidator(has_values)]