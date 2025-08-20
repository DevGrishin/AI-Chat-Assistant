# AI Reactbot

AI Reactbot is an interactive AI companion that can see your screen, listen to your voice, and respond naturally through speech. It's designed to feel more like chatting with a friend than interacting with a traditional AI assistant.

## 🌟 Features

- **Voice Interaction**: Press and hold the 'Clear' key to record your voice
- **Screen Awareness**: The AI can see your screen and naturally comment on what you're doing
- **Flexible AI Models**: 
  - Cloud options: OpenAI GPT-4, Groq LLama
  - Local option: Any Ollama model
- **Multiple Speech-to-Text Options**:
  - OpenAI Whisper (cloud)
  - Groq Whisper (cloud)
  - Local Whisper (various sizes: tiny to large)
- **Text-to-Speech Choices**:
  - ElevenLabs (high-quality cloud TTS)
  - Local Kokoro TTS

## 🚀 Getting Started

### Prerequisites

- Python 3.12.x
- eSpeak NG installed (Restart required)
- MPV.io installed (via Chocolatey on Windows)

### Required Python Packages

```bash
pip install ollama openai groq elevenlabs whisper sounddevice simpleaudio scipy numpy mss kokoro soundfile
```

### Installation

1. Clone the repository
2. Install the required packages
3. Run `main.py` for first-time setup
4. Follow the prompts to configure:
   - AI model selection
   - Speech-to-text service
   - Text-to-speech service
   - API keys (if using cloud services)

## 🛠️ Configuration

The app uses two configuration files:

### api.json
Stores your API keys for:
- OpenAI
- ElevenLabs
- Groq

### config.json
Stores your preferences for:
- AI model (OpenAI, Groq, or local Ollama model)
- Speech-to-text service (OpenAI, Groq, or local Whisper)
- Text-to-speech service (ElevenLabs or local Kokoro)

## 🎯 Usage

1. Run the program: `python main.py`
2. Hold the 'Clear' key (Numpad 5) to record your voice
3. Release to process and get AI response
4. The AI will respond both in text and speech

## 🤝 AI Personality

The AI is designed to be conversational and friendly, not just an assistant. It will:
- Maintain a casual, natural conversation style
- Comment on screen contents when relevant
- Express personality and emotions
- Keep responses concise and natural
- Avoid being overly formal or instructional

## ⚙️ Technical Details

- Uses sounddevice for audio recording
- Implements real-time screen capture with MSS
- Supports multiple AI model backends
- Handles audio in various formats (44.1kHz, 24kHz)
- Includes proper audio normalization
- Manages conversation history with context window

## � Troubleshooting

If the program crashes after audio playback, run the following command to fix the simpleaudio package:
```bash
pip install -U --force git+https://github.com/cexen/py-simple-audio.git
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.


## �🙏 Acknowledgments

- OpenAI for GPT and Whisper
- Groq for their API
- ElevenLabs for TTS
- Ollama for local AI models
- The creators of Kokoro TTS
