from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated

from validator.has_value import has_value

class AudioFileInput(BaseModel):
  file_name: Annotated[str, AfterValidator(has_value)]
  encoded_audio: Annotated[str, AfterValidator(has_value)]