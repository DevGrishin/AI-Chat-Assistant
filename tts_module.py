from elevenlabs import ElevenLabs, stream, save
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import keys, config
import simpleaudio as sa

if config.TTS == "eleven":
    eleven_client = ElevenLabs(api_key=keys.ELEVENLABS_API_KEY)
else:
    pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    generator = pipeline("warmup", voice='am_michael', speed=1.0)
    
    for (_, _, audio) in generator:
        sf.write("output.wav", audio, 24000)



def tts(prompt):
    if config.TTS == "eleven":
        eleven_tts(prompt)
    else:
        local_tts(prompt)
    

def eleven_tts(prompt):
    audio_stream = eleven_client.text_to_speech.stream(
        text=str(prompt),
        voice_id="nPczCjzI2devNBz1zQrb",
        model_id="eleven_multilingual_v2",
        output_format="pcm_24000"
    )
    raw_bytes = b"".join(audio_stream)

    if len(raw_bytes) % 2 != 0: 
        raw_bytes = raw_bytes[:-1]
    audio_array = np.frombuffer(raw_bytes, dtype=np.int16)


    sf.write("output.wav", audio_array, 24000)

def local_tts(prompt):
    generator = pipeline(prompt, voice='am_michael', speed=1.0)
    
    for (_, _, audio) in generator:
        sf.write("output.wav", audio, 24000)
  
  
