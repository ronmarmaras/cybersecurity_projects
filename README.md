Convert Script into an Executable
$ pip install pyinstaller

Generate the Executable
$ pyinstaller --onefile --noconsole keylogger.py
--onefile: Packages everything into a single executable file.
--noconsole: Suppresses the console window (runs silently in the background).
