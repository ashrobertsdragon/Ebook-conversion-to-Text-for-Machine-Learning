import json
import os
import re
import time
import traceback


token_conversion_factor = 0.7


def read_text_file(file_path):
  
  try:
    with open(file_path, "r") as f:
      read_file = f.read()


    return read_file

  except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
    exit()

def read_json_file(file_path):
  
  try:
    with open(file_path, "r") as f:
      read_file = json.load(f)

    
    return read_file
    
  except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
    exit()


def write_to_file(content, file_path):
  
  with open(file_path, "a") as f:
    f.write(content + "\n")


  return

def separate_into_chapters(text):

  
  return re.split("\s*\*\*\s*", text)

def write_json_file(content, file_path):
  with open(file_path, "w") as f:
    json.dump(content, f, indent=2)


  return

def check_continue():
  
  # Ask if ready to continue
  continue_program = ""

  while continue_program.upper() not in ["Y", "N"]:
    continue_program = input("If this looks right, type Y to continue the program. Type N to exit: ")

    if continue_program.upper() == "N":
      print("Exiting the program...")
      exit()
  
    elif continue_program.upper() != "Y":
      print("Invalid input. Please try again.")


  return

def remove_none_found(d):
  
  if isinstance(d, dict):
    new_dict = {}
    for key, value in d.items():
      cleaned_value = remove_none_found(value)
      if cleaned_value != "None found":
        new_dict[key] = cleaned_value

    
    return new_dict
    
  elif isinstance(d, list):


    return [remove_none_found(item) for item in d]
    
  else:


    return d
  