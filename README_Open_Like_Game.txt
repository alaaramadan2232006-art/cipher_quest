CIPHER QUEST — OPEN LIKE A NORMAL DESKTOP GAME

WHAT THIS DOES
This kit lets Windows build the game into a desktop application. You only run the builder once. After that, you can launch the game by double-clicking Cipher Quest.exe; you do not need to open VS Code or type commands each time.

IMPORTANT FOR YOUR COMPUTER
Your C: drive was almost full. This build keeps Python environment, temporary files, and build output in this project folder, so put the project on G: (or F:) where you have free space.

STEPS
1. Keep your existing G:\CipherQuest folder, including its .venv and assets folder.
2. Copy these two files into G:\CipherQuest:
   - cipher_quest_pink_cyber.py
   - BUILD_GAME_EXE.bat
   If Windows asks about replacing cipher_quest_pink_cyber.py, choose Replace. Do not delete the assets folder or cloud_config.json.
3. If you want the game to play your own song, put that audio file (.wav, .ogg, or .mp3) inside G:\CipherQuest\assets BEFORE building.
   The game will include the assets present during the build. It also checks for a newer song in the assets folder beside the EXE, so you can change it later without rebuilding.
4. Double-click BUILD_GAME_EXE.bat. The first build needs an internet connection to install PyInstaller and Pygame CE. Leave the black window open until it says BUILD COMPLETE.
5. The game should start after it builds. The EXE is saved at:
   G:\CipherQuest\dist\Cipher Quest\Cipher Quest.exe
6. Next time, simply double-click Cipher Quest.exe. To add a desktop shortcut: right-click the EXE > Send to > Desktop (create shortcut).

WHY THERE IS A FOLDER AROUND THE EXE
The build uses a folder-based app instead of a single-file EXE. This avoids extracting the full game to the Windows temporary folder on C: every time you launch it, which is important because C: was nearly full. Keep the whole "Cipher Quest" folder together; do not move only the EXE out of it.

CLOUD
The game code looks for cloud_config.json beside the app. Keep your existing cloud_config.json in G:\CipherQuest. The Cloud features still require a valid Firebase setup and an internet connection; packaging does not configure Firebase by itself.

If the builder stops on an error, take a screenshot of the black window and send it for troubleshooting. Don't delete files from Windows or your project to make space.
