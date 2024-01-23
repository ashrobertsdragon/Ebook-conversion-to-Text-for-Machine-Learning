def read_text_file(file_path: str) -> str:
  with open(file_path, "r") as f:
    read_file = f.read()
  return read_file

def write_to_file(content: str, file: str):
  with open(file, "w") as f:
    f.write(content)
