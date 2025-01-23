def has_value(value: str) -> str:
  if len(value) > 0:
    return value
  raise ValueError("A field is empty")