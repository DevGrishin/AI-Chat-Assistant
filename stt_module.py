import os, json
from groq import Groq
from openai import OpenAI
import whisper
import keys, config


if config.STT == "groq":
    groq_client = Groq(api_key=keys.GROQ_API_KEY)
elif config.STT == "openai":
    openai_client = OpenAI(api_key=keys.OPENAI_API_KEY)
else:
    model = whisper.load_model(config.STT)



def stt(filename):
    if config.STT == "groq":
        transcription = groq_transcribe(filename)
    elif config.STT == "openai":
        transcription = openai_transcribe(filename)
    else:
        transcription = local_transcribe(filename)
    return transcription

def groq_transcribe(filename):
    filename = os.path.dirname(__file__) + f"/{filename}"
    
    with open(filename, "rb") as file:
        transcription = groq_client.audio.transcriptions.create(
          file=file,
          model="whisper-large-v3-turbo",
          prompt="British spelling",
          language="en",  
          temperature=0.0  
        )
        userInput = json.dumps(transcription.text, indent=2, default=str)

        return userInput

def openai_transcribe(filename):
    with open(filename, "rb") as file:
        transcription = openai_client.audio.transcriptions.create(
          file=file,
          model="whisper-1",
          prompt="British spelling",
          language="en",  
          temperature=0.0  
        )
        userInput = json.dumps(transcription.text, indent=2, default=str)

        return userInput

def local_transcribe(filename):
    result = model.transcribe(filename)
    print(result["text"])

