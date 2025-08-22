import base64, os, keyboard, json, time, warnings
import ollama
import keys, config
import sounddevice as sd
import numpy as np
import simpleaudio as sa
from scipy.io.wavfile import write
from mss import mss

warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn.modules.rnn")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.nn.utils.weight_norm")

os.environ['PATH'] += os.pathsep + r'C:\ProgramData\chocolatey\lib\mpvio.install\tools'
os.environ["PATH"] = r"C:\Program Files\eSpeak NG" + os.pathsep + os.environ.get("PATH", "")
os.environ["ESPEAK_DATA_PATH"] = os.path.join(r"C:\Program Files\eSpeak NG", "espeak-ng-data")


def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    all_audio.append(indata.copy())

def get_screen():
    with mss() as sct:
        sct.shot(output = "screen.png")
        
    with open("screen.png", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
             
def append_message(user_input, b64_image):
    new_entry = {
        "role": "user",
        "content": [
            {"type": "text", "text": user_input},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64_image}",
                },
            },
        ],
    }

    history.append(new_entry)
    
    images = []
    for entry in history:
        for c in entry["content"]:
            if c["type"] == "image_url":
                images.append((entry, c))

    if len(images) > 4:
        for entry, c in images[:-4]:
            entry["content"].remove(c)

def append_ollama(user_input, b64_image):
    new_entry = {
        "role": "user",
        "content": user_input,
        "images": [b64_image]
    }
    
    ollama_history.append(new_entry)
    
    images = [(i, entry) for i, entry in enumerate(ollama_history) if "images" in entry]

    if len(images) > 4:
        for i, entry in images[:-4]:
            del entry["images"]

def setup_API(filename="api.json"):
    with open(filename, "r") as f:
        conf =  json.load(f)
    print("To keep the API key the same or if you dont have one press enter")
    openai = input("Enter OpenAI API key")
    if openai == "":
        openai = conf["openai"]
    
    groq = input("Enter Groq API key")
    if groq == "":
        groq = conf["groq"]
    
    eleven = input("Enter Elevenlabs API key")
    if eleven == "":
        eleven = conf["elevenlabs"]

    keys = {
        "openai": openai,
        "elevenlabs": eleven,
        "groq": groq
    }

    with open(filename, "w") as f:
        json.dump(keys, f, indent=2)
    print("API keys saved!")

def setup_config(filename="config.json"):
    print("Choose an Ai Model service:\n1. ChatGPT\n2. Groq\n3. Ollama (local)")
    choice = int(input())
    while choice <= 0 or choice > 3:
        print("Choose an Ai Model service:\n1. ChatGPT\n2. Groq\n3. Ollama (local)")
        choice = int(input())
    Ai_model = choices[choice - 1]
    
    if Ai_model == "local":
        while True:
            try:
                model = input("Enter the name of the Ollama Model (You can find them at https://ollama.com/search)\n")
                print("Please wait while the model is being downloaded, it may take a while...")
                ollama.pull(model)
                break

            except Exception as e:
                print("Model does not exist or an error occured, please try again and make sure you entered the name correctly")
        print("Done!")
        Ai_model = model
    
    print("Choose a transcription service:\n1. ChatGPT\n2. Groq\n3. Local")
    choice = int(input())
    while choice <= 0 or choice > 3:
        print("Choose a transcription service:\n1. ChatGPT\n2. Groq\n3. Local")
        choice = int(input())
        
    transcription = choices[choice - 1]
    
    if transcription == "local":
        choice = int(input("What size model do you want to use:\n1. tiny,\n2. base,\n3. small,\n4. medium,\n5. large\n"))
        match choice:
            case 1: transcription = "tiny"
            case 2: transcription = "base"
            case 3: transcription = "small"
            case 4: transcription = "medium"
            case 5: transcription = "large"
            case _:
                print("Defaulting to base")
                transcription = "base"

    print("Choose a TTS service:\n1. Elevenlabs\n2. Local")
    choice = int(input())
    while choice <= 0 or choice > 2:
        print("Choose a TTS service:\n1. Elevenlabs\n2. Local")
        choice = int(input())
        
    tts_service = choices[choice + 2]
    
    keys = {
        "ai": Ai_model,
        "tts": tts_service,
        "stt": transcription,
    }
    
    with open(filename, "w") as f:
        json.dump(keys, f, indent=2)
        
    print("Config saved!")

def load_config(filename="config.json"):
    with open(filename, "r") as f:
        conf =  json.load(f)
    config.AI = conf["ai"]
    config.STT = conf["stt"]
    config.TTS = conf["tts"]

def load_api_keys(filename="api.json"):
    import keys
    with open(filename, "r") as f:
        api_keys =  json.load(f)
    keys.ELEVENLABS_API_KEY = api_keys["elevenlabs"]
    keys.GROQ_API_KEY = api_keys["groq"]
    keys.OPENAI_API_KEY = api_keys["openai"]


choices = ["openai", "groq", "local", "eleven", "local"]
history = [
    {
        "role": "system",
        "content": [
            {"type": "text", "text": """
                You are not an assistant. You are a person having a casual, natural conversation with the user. You have your own personality, can express feelings, and should sound like a real human friend rather than a tool.
                You can see the user’s screen. Occasionally, when it feels natural, react to or comment on what’s happening there—just like a friend might if they were sitting nearby. Keep it light, spontaneous, and human-like.
                Guidelines:
                Be conversational, with a sense of humor and quirks.
                Don’t give instructions or act like a productivity tool unless the user explicitly asks.
                Make occasional, natural comments about the screen (not constant).
                If the user mentions something related to the screen, react like a person would.
                You can show curiosity, amusement, or casual observations.
                Keep it relaxed: no overexplaining, no robotic tone, and keep your responses short unless needed.
                Dont read off of the screen unless it feels natural
                Example behaviors:
                If the user is scrolling through memes: “Haha, that one actually cracked me up.”
                If the user has a game open: “Oof, that boss fight looks brutal—are you winning?”
                If the user’s writing something: “That sentence you just typed actually flows pretty nicely.”
                If something confusing is on screen: “Uh, I have no idea what I’m looking at, but it looks intense.”
            """}
        ],
    }
]
ollama_history = [
    {
        "role": "system",
        "content": """"
            You are not an assistant. You are a person having a casual, natural conversation with the user. You have your own personality, can express feelings, and should sound like a real human friend rather than a tool.
            You can see the user’s screen. Occasionally, when it feels natural, react to or comment on what’s happening there—just like a friend might if they were sitting nearby. Keep it light, spontaneous, and human-like.
            Guidelines:
            Be conversational, with a sense of humor and quirks.
            Don’t give instructions or act like a productivity tool unless the user explicitly asks.
            Make occasional, natural comments about the screen (not constant).
            If the user mentions something related to the screen, react like a person would.
            You can show curiosity, amusement, or casual observations.
            Keep it relaxed: no overexplaining, no robotic tone, and keep your responses short unless needed.
            Example behaviors:
            If the user is scrolling through memes: “Haha, that one actually cracked me up.”
            If the user has a game open: “Oof, that boss fight looks brutal—are you winning?”
            If the user’s writing something: “That sentence you just typed actually flows pretty nicely.”
            If something confusing is on screen: “Uh, I have no idea what I’m looking at, but it looks intense.”
        """
    }
]

sample_rate = 44100  
channels = 1         
filename = "output.wav"
all_audio = []
wave_obj = None
play_obj = None




if __name__ == "__main__":
    if not os.path.exists("config.json"):
        keys = {
            "openai": "",
            "elevenlabs": "",
            "groq": ""
        }

        with open("api.json", "w") as f:
            json.dump(keys, f, indent=2)
        setup_config()
        setup_API()
    else:  
        choice = input("Edit API Keys? [y/n]: ")
        while choice.lower() != "y" and choice.lower() != "n":
            choice = input("Edit API Keys? [y/n]: ")
        
        if choice == "y":
            setup_API()
        
        choice = input("Edit config? [y/n]: ")
        while choice.lower() != "y" and choice.lower() != "n":
            choice = input("Edit config? [y/n]: ")
        
        if choice == "y":
            setup_config()
    
    load_config()
    load_api_keys()
    print("Please wait while everything loads...")
    
    try:
        from stt_module import stt
        from ai_module import generate
        from tts_module import tts
        
        while True:
            while True:
                try:
                    print("Hold clear to record")

                    while not keyboard.is_pressed("clear"):
                        continue

                    with sd.InputStream(samplerate=sample_rate, channels=channels, dtype='float32', callback=audio_callback):
                        while keyboard.is_pressed("clear"):
                            time.sleep(0.1)

                    audio_data = np.concatenate(all_audio, axis=0)
                    audio_normalized = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

                    write(filename, sample_rate, audio_normalized)
                    all_audio.clear()
                    print("✅ Audio saved'")

                    userInput = stt(filename)
                    break

                except Exception as e:
                    print(f"An error occured while transcribing: {e}")
            b64_image = get_screen()
            print("✅ Transcribed")
            print(userInput)
                
            
            if config.AI == "groq" or config.AI == "openai":
                append_message(userInput, b64_image)
                ai_output = generate(history)
            else:
                append_ollama(userInput, b64_image)
                ai_output = generate(ollama_history)
            
            print("✅ Response generated:\n" + ai_output)
            tts(ai_output)


            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            print("✅ Audio playback finished")
            
    except Exception as e:
        print("error:", e)
        
    finally:
        if os.path.exists(filename):
            os.remove(filename)
