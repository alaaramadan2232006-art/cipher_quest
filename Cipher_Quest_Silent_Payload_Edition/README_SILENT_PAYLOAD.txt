CIPHER QUEST — SILENT PAYLOAD EDITION
====================================

WHAT CHANGED
- Background track renamed SILENT PAYLOAD.
- Original melancholic cyber-themed lyrics and a soft synthetic vocal are included.
- Backing is slow, mellow, and minor-key, with a light echo on the voice.
- The game still uses a green neon cybersecurity style, nine challenges, and optional Cloud Portal.
- Press M or use the song button to turn the song on/off.

FILES
  cipher_protocol_silent_payload.py
  assets/silent_payload.wav
  SILENT_PAYLOAD_LYRICS.txt
  cloud_config.example.json
  firebase_database_rules.json

RUN IN VS CODE (WINDOWS)
1. Extract this ZIP to a NEW folder first, or copy the files into G:\CipherQuest without deleting your existing version.
2. Ensure the assets folder is beside the Python file.
3. Open the folder in VS Code and select Terminal -> New Terminal.
4. Run:
   .\.venv\Scripts\python.exe cipher_protocol_silent_payload.py

The command above assumes G:\CipherQuest already has the .venv environment. If you extract elsewhere, adjust the path to that environment or run the Python interpreter you installed pygame-ce into.

ABOUT THE SONG
SILENT PAYLOAD is an original, melancholic cyber song created for this game. The vocal is computer-synthesized, not a human singer, and the track is not copied from an existing commercial recording.

CLOUD NOTE
The game works locally without Firebase. The Cloud Portal needs your own Firebase project configuration before online authentication and score saving can work. Do not share private account credentials.
