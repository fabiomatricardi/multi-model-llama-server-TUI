# TUI-CPP - LLaMA.cpp Server Manager

<img src='https://github.com/fabiomatricardi/multi-model-llama-server-TUI/raw/main/interface.png' width=1000>

A Text User Interface (TUI) application for managing llama.cpp server on Windows.

built with <img src='https://opencode.ai/docs/_astro/logo-light.B0yzR0O5.svg' height=30>

Model: Zen GLM4.7 free
Prompt:
```markdown
create a python CLI app, to resemble the opencode text GUI. The app is called "TUI-CPP" and allows the user to start and stop
llama.cpp server (through popen command using the windows llama.cpp binaries, do that the porcess ID can be set to stop it
when the user request the server to be stopped). The user must be able to select the model from a list (all the GGUF files
present in the subfolder '/models'). The user shall be able to set  the context window
(min 4096, max 65536 tokens, with changes of 1024). A status bar at the top will display the RAM used by the loaded
model in Mb (the process ID is to be used for this feature). At the bottom another status message area will display the logs
(server started/stopped). I want to be able to create in the end a standalone executable of this python app, using pyinstaller.
Do not include '/models' and the llama-server.exe in the pyinstaller script. Make sure that the python app consider
llama-server.exe to be in current path of the app, and the 'models' subfolder as a relative path to the main app path.
```

## Features

- Start and stop llama.cpp server
- Select GGUF models from `/models` folder using an interactive list
- Configure context window size (4096-65536 tokens, in 1024 increments)
- Real-time RAM usage monitoring
- Status logging area
- Command palette (Ctrl+/)
- Two-column layout: settings on left, model selection on right
- Auto-clamp context window to nearest valid value
- Refresh model list without restarting app
- PyInstaller-compatible with proper path handling

## Requirements

- Windows OS
- `llama-server.exe` in the same directory as the executable
- GGUF model files in `./models/` subdirectory

## Installation

### Option 1: Run from source

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python tui_cpp.py
```

Or use the provided batch file:
```bash
run.bat
```

### Option 2: Build standalone executable

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller TUI-CPP.spec
```

Or use the provided batch file:
```bash
build.bat
```

The executable will be created in the `dist/` directory.

## Setup

1. Place `llama-server.exe` in the same directory as `TUI-CPP.exe` (or run `tui_cpp.py` from source directory)
2. Create a `models/` subdirectory next to the executable
3. Place your GGUF model files in the `models/` folder

**Directory structure:**
```
TUI-CPP/
├── TUI-CPP.exe          (or tui_cpp.py)
├── llama-server.exe      (required)
├── models/               (required)
│   ├── model1.gguf
│   ├── model2.gguf
│   └── ...
```

## Usage

### Navigation

- **Tab**: Navigate between widgets
- **Arrow keys**: Navigate model list
- **Enter**: Select model or press button
- **Ctrl+/**: Open command palette
- **q**: Quit application

### Starting the Server

1. Navigate to the model list on the right column
2. Select a model using arrow keys
3. Navigate to the context window input on the left column
4. Set the context window size (default: 4096)
   - The app automatically suggests nearest valid values
   - Invalid values are clamped to nearest valid multiple of 1024
5. Press "Start Server" to launch llama.cpp server
6. Monitor RAM usage in the status bar
7. View logs in the bottom panel

### Stopping the Server

1. Press "Stop Server" button
2. The server will be gracefully terminated
3. If the server doesn't stop within 5 seconds, it will be forcefully killed

### Refreshing Model List

1. Press "Refresh" button below the model list
2. The app scans the `/models` folder for GGUF files
3. New models appear in the list immediately

## UI Layout

```
+-------------------------------------------------------+
| Header: TUI-CPP - LLaMA.cpp Server Manager            |
+-------------------------------------------------------+
| RAM Usage: XXX.XX MB | Status: Running/Stopped        |
+-------------------------------------------------------+
| Left Column              |  Right Column              |
|                          |                            |
| Context Window           |  Select Model:             |
| (4096-65536, step 1024)  |  +----------------------+  |
| [Input: 4096]            |  | model1.gguf          |  |
| [Hint: Valid: 4096]      |  | model2.gguf          |  |
|                          |  | model3.gguf          |  |
|                          |  +----------------------+  |
| [Start Server] [Stop]    |  [Refresh Button]          |
+-------------------------------------------------------+
| Log: Server started (PID: 1234)                       |
| Log: Model: model1.gguf                               |
| Log: Context size: 4096 tokens                        |
+-------------------------------------------------------+
| Footer: Ctrl+/: Command Palette  |  q: Quit           |
+-------------------------------------------------------+
```

## Troubleshooting

### Model list shows "No GGUF files found in /models"

- Verify that the `models/` folder exists in the same directory as the executable
- Ensure you have GGUF files (`.gguf` extension) in the models folder
- If running from source, ensure you're in the correct directory
- Try clicking the "Refresh" button to reload the model list

### "llama-server.exe not found" error

- Make sure `llama-server.exe` is in the same directory as `TUI-CPP.exe`
- If running from source, ensure it's in the same folder as `tui_cpp.py`
- Check that the filename is exactly `llama-server.exe` (not `llama_server.exe`)

### PyInstaller build errors

**AttributeError: 'NoneType' object has no attribute 'fileno'**
- Ensure the spec file has `console=True` (Textual requires console mode)
- Make sure all hidden imports are included in the spec file

**Executable runs but doesn't show content properly**
- Make sure you're using the latest version of the code with proper path handling
- The app now correctly detects if running from PyInstaller and uses `sys.executable` for paths

**Models not found in executable version**
- This issue has been fixed in the latest version
- The app now uses `sys.executable` to determine the correct directory when running from PyInstaller
- Rebuild the executable using the updated code

### Server won't start

- Check that the selected model file exists and is valid
- Verify context window size is between 4096 and 65536
- Ensure llama-server.exe is compatible with your system architecture
- Check the log area for detailed error messages

### Server won't stop

- Wait a few seconds - the app attempts graceful shutdown first
- If it still doesn't stop, the app will forcefully kill the process after 5 seconds
- As a last resort, you can manually terminate `llama-server.exe` from Task Manager

## Notes

- The llama-server.exe and models folder are NOT included in the standalone executable
- Ensure both are present in the application directory before running
- The server runs on port 8080 by default
- Context window size must be between 4096 and 65536 tokens
- Context window size must be a multiple of 1024
- The app automatically clamps invalid context sizes to nearest valid value

<img src='https://github.com/fabiomatricardi/multi-model-llama-server-TUI/raw/main/interface-autoadjust.png' width=800>

- The application uses `sys.executable` to correctly resolve paths when running from PyInstaller
- An optional icon file (`llama.ico`) can be placed in the build directory for custom executable icon
