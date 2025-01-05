from fastapi.testclient import TestClient
import json

from main import app

client = TestClient(app)

def test_success():
  response = client.post(
    "/process-audio", 
    json={
      "session_id": "12345", 
      "timestamp": "2025-01-05T16:00:00Z", 
      "audio_files": [{ 
        "file_name": "example_file_name", 
        "encoded_audio": "UklGRuYAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YaYAAABPZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm",
      },{ 
        "file_name": "example_file_name_2", 
        "encoded_audio": "UklGRuYAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YaYAAABPZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm",
      }]
    }
  )

  assert response.status_code == 200

  response_data = response.json()
  assert response_data["status"] == "success"
  assert response_data["processed_files"][0]["file_name"] == "example_file_name"
  assert response_data["processed_files"][0]["length_seconds"] == 0.01725 
  assert response_data["processed_files"][1]["file_name"] == "example_file_name_2"
  assert response_data["processed_files"][1]["length_seconds"] == 0.01725 

def test_missing_session_field():
  response = client.post(
    "/process-audio", 
    json={ 
      "timestamp": "2025-01-05T16:00:00Z", 
      "audio_files": [{ 
        "file_name": "example_file_name", 
        "encoded_audio": "UklGRuYAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YaYAAABPZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm",
      }]
    }
  )

  assert response.status_code == 422

  response_data = response.json()
  assert response_data["status"] == "error"
  assert response_data["message"] == "[{'type': 'missing', 'loc': ('body', 'session_id'), 'msg': 'Field required', 'input': {'timestamp': '2025-01-05T16:00:00Z', 'audio_files': [{'file_name': 'example_file_name', 'encoded_audio': 'UklGRuYAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YaYAAABPZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm'}]}}]"

def test_missing_file_name_field():
  response = client.post(
    "/process-audio", 
    json={ 
      "session_id": "12345",
      "timestamp": "2025-01-05T16:00:00Z", 
      "audio_files": [{ 
        "encoded_audio": "UklGRuYAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YaYAAABPZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm",
      }]
    }
  )

  assert response.status_code == 422

  response_data = response.json()
  assert response_data["status"] == "error"
  assert response_data["message"] == "[{'type': 'missing', 'loc': ('body', 'audio_files', 0, 'file_name'), 'msg': 'Field required', 'input': {'encoded_audio': 'UklGRuYAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YaYAAABPZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm'}}]"

def test_empty_array():
  response = client.post(
    "/process-audio", 
    json={ 
      "session_id": "12355",
      "timestamp": "2025-01-05T16:00:00Z", 
      "audio_files": []
    }
  )

  assert response.status_code == 422

  response_data = response.json()
  assert response_data["status"] == "error"
  assert response_data["message"] == "[{'type': 'value_error', 'loc': ('body', 'audio_files'), 'msg': 'Value error, List of audio files is empty', 'input': [], 'ctx': {'error': ValueError('List of audio files is empty')}}]"

def test_empty_string():
  response = client.post(
    "/process-audio", 
    json={ 
      "session_id": "",
      "timestamp": "2025-01-05T16:00:00Z", 
      "audio_files": [{ 
        "file_name": "", 
        "encoded_audio": "UklGRuYAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YaYAAABPZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm",
      }]
    }
  )

  assert response.status_code == 422

  response_data = response.json()
  assert response_data["status"] == "error"
  assert response_data["message"] == "[{'type': 'value_error', 'loc': ('body', 'session_id'), 'msg': 'Value error, A field is empty', 'input': '', 'ctx': {'error': ValueError('A field is empty')}}, {'type': 'value_error', 'loc': ('body', 'audio_files', 0, 'file_name'), 'msg': 'Value error, A field is empty', 'input': '', 'ctx': {'error': ValueError('A field is empty')}}]"

def test_bad_timestamp():
  response = client.post(
    "/process-audio", 
    json={ 
      "session_id": "7890",
      "timestamp": "invalid_time_stamp", 
      "audio_files": [{ 
        "file_name": "example_2", 
        "encoded_audio": "UklGRuYAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YaYAAABPZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm",
      }]
    }
  )

  assert response.status_code == 422

  response_data = response.json()
  assert response_data["status"] == "error"
  assert response_data["message"] == "[{'type': 'datetime_from_date_parsing', 'loc': ('body', 'timestamp'), 'msg': 'Input should be a valid datetime or date, invalid character in year', 'input': 'invalid_time_stamp', 'ctx': {'error': 'invalid character in year'}}]"

def test_invalid_base64():
  response = client.post(
    "/process-audio", 
    json={
      "session_id": "7358", 
      "timestamp": "2025-01-05T16:00:00Z", 
      "audio_files": [{ 
        "file_name": "example_file_name", 
        "encoded_audio": "InvalidBase64!",
      }]
    }
  )

  assert response.status_code == 422

  response_data = response.json()
  assert response_data["status"] == "error"
  assert response_data["message"] == "Invalid base64 encoded audio"


# Should include something like codecov to make sure all cases in the code are being tested
# Integration tests should cover their tracks, ex. delete new files added to the db
# Tests should be in a spec folder