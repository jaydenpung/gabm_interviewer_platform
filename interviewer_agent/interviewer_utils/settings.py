import sys
import os
import random

def get_open_api_keyset(): 
  # Load API key from environment variable
  api_key = os.getenv('OPENAI_API_KEY')
  
  if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
  
  open_api_keyset = []
  open_api_keyset += [{"key": api_key,
                       "owner": "env_var",
                       "id": 1,
                       "weight": 12}]

  # Extracting weights
  weights = [api["weight"] for api in open_api_keyset]
  # Selecting one dictionary considering the weights
  selected_api_key = random.choices(open_api_keyset, weights=weights, k=1)[0]
  print (f"========== USING THE FOLLOWING: ", selected_api_key)
  return selected_api_key


# DEBUG = False
DEBUG = True

STORAGE_DIR = "storage"

GOOGLE_CRED_PATH = ""

INTERVIEW_AGENT_PATH = "interviewer_agent"



get_open_api_keyset()