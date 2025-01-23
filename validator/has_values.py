def has_values(values: list) -> list:
  if not values:
    raise ValueError("List of audio files is empty")
  return values