import threading
import queue
import io
import openai

from pydub import AudioSegment
from google.cloud import speech

from global_methods import *
from interviewer_agent.interviewer_utils.settings import * 

openai.api_key = get_open_api_keyset()["key"]


def jsp_log(message): 
  from datetime import datetime
  formatted_time = datetime.now().strftime("%H:%M:%S")
  print (f'[transcribe.py] {formatted_time} -- {message}')


def transcribe_voice(audio_buffer, optional_key_phrases=["my name is Joon"]):
  """
  Transcribes voice from an audio buffer using OpenAI's Whisper.

  The function converts the audio buffer to determine its duration and then
  uses OpenAI's Whisper model for transcription. The model is provided with 
  the language setting and optional key phrases to assist in the transcription 
  process.

  Args:
    audio_buffer (BytesIO): A buffer containing the audio data.
    optional_key_phrases (list of str, optional): A list of key phrases that
      may be present in the audio. Useful for improving the accuracy of 
      transcription in case of specific or hard-to-spell words. 
      Defaults to ["my name is Joon"].

  Returns:
      str: The transcribed text.
  """
  duration_seconds = len(AudioSegment.from_file(audio_buffer)) / 1000.0  
  jsp_log("Starting to actually transcribe user's voice")
  jsp_log(f"Audio duration: {duration_seconds} seconds")

  # Skip Google Speech API since GOOGLE_CRED_PATH is not configured
  # Use OpenAI Whisper directly for all audio transcription
  
  # For capturing hard to spell words, like names
  optional_key_phrases = ', '.join(optional_key_phrases)
  audio_buffer.name = "file.wav"
  
  try:
    whisper_completion = openai.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_buffer,
      language="en",
      prompt=optional_key_phrases)
    user_speech = whisper_completion.text

    jsp_log(f"Whisper API keyword: {optional_key_phrases}")
    jsp_log(f"From Whisper API: {user_speech}")
    return user_speech
  except Exception as e:
    jsp_log(f"Error in Whisper transcription: {e}")
    return "..."


def threaded_transcribe_voice(audio_buffer, 
                              optional_key_phrases=["my name is Joon"], 
                              timeout=60, 
                              max_retries=3):
  """
  Transcribes voice from an audio buffer using a threaded approach with 
  retries and timeout handling.

  This function creates a thread to handle the transcription process. It 
  retries the transcription up to a specified number of times if it fails or 
  times out. The function uses the `transcribe_voice` function for the actual 
  transcription.

  Args:
    audio_buffer (BytesIO): A buffer containing the audio data.
    optional_key_phrases (list of str, optional): A list of key phrases 
      that may be present in the audio. Useful for improving the accuracy 
      of transcription in case of specific or hard-to-spell words.
      Defaults to ["my name is Joon"].
    timeout (int, optional): The maximum number of seconds to wait for a 
      transcription to complete before timing out. Defaults to 8 seconds.
    max_retries (int, optional): The maximum number of times to retry the 
      transcription in case of failure or timeout. Defaults to 3 retries.

  Returns:
    str: The transcribed text, or a placeholder string "..." if 
      transcription fails after maximum retries.
  """
  # Function to be executed in a thread
  def transcribe_thread(queue, audio_buffer, optional_key_phrases):
    try:
      transcription = transcribe_voice(audio_buffer, optional_key_phrases)
      queue.put(transcription)
    except Exception as e:
      queue.put(e)

  jsp_log("Threading: Starting the thread for transcribing voice")
  jsp_log(f"Threading: Timeout: {timeout}, max retries: {max_retries}")

  # Initialize a queue to hold the transcription result
  q = queue.Queue()

  # Retry mechanism
  for count in range(max_retries):
    # Start a thread for transcription
    thread = threading.Thread(target=transcribe_thread, 
                              args=(q, audio_buffer, optional_key_phrases))
    thread.start()
    jsp_log(f"Threading: Starting the current thread: {count}")

    try:
      # Wait for the thread to complete with timeout
      result = q.get(block=True, timeout=timeout)
      # Check if the result is an exception and raise it
      if isinstance(result, Exception):
          raise result
      # If successful, return the transcription
      return result
    except queue.Empty:
      # Handle timeout, log if necessary
      jsp_log(f"Threading: Timed out after {timeout} seconds.")
    except Exception as e:
      # Handle other exceptions, log if necessary
      jsp_log(f"Threading: Error during transcription: {e}")
    finally:
      # Ensure the thread is terminated
      thread.join()

  # Return a placeholder if transcription fails after maximum retries
  return "..."



























