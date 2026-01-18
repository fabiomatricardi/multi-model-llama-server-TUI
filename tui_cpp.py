"""TUI-CPP - LLaMA.cpp Server Manager

A Text User Interface (TUI) application for managing llama.cpp server on Windows.
Provides an interactive interface to start/stop the server, select GGUF models,
configure context window size, and monitor RAM usage in real-time.
"""

import os
import sys
import subprocess
import psutil
from pathlib import Path
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header,
    Footer,
    Static,
    Button,
    OptionList,
    Input,
    Label,
    Log,
)
from textual import events
from textual.binding import Binding
from textual.widgets.option_list import Option


class TUI_CPP(App):
    """Main application class for TUI-CPP.
    
    A Textual-based TUI application that provides an interface for managing
    llama.cpp server. Features include model selection, context window configuration,
    server start/stop control, and real-time RAM usage monitoring.
    
    Attributes:
        TITLE (str): Application title displayed in header.
        SUBTITLE (str): Application subtitle displayed in header.
        BINDINGS (list): Keyboard bindings for application commands.
        server_process (Optional[subprocess.Popen]): Active llama-server.exe process.
        _server_running (bool): Internal flag tracking server state.
    """
    
    TITLE = "TUI-CPP"
    SUBTITLE = "LLaMA.cpp Server Manager"
    
    BINDINGS = [
        Binding("ctrl+/", "show_command_palette", "Command Palette", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #main-container {
        height: 1fr;
    }
    
    #content-layout {
        height: 1fr;
    }
    
    #left-column, #right-column {
        padding: 1;
    }
    
    #left-column {
        width: 1fr;
    }
    
    #right-column {
        width: 1fr;
    }
    
    #status-bar {
        height: 3;
        background: $panel;
        padding: 0 1;
        text-align: center;
        margin: 0 1;
    }
    
    #status-text {
        text-style: bold;
        color: $success;
    }
    
    .section {
        margin: 1 0;
    }
    
    .section-title {
        text-style: bold;
        margin: 0 0 1 0;
    }
    
    #log-area {
        height: 8;
        background: $surface;
        border-top: solid $primary;
        margin: 0 1;
    }
    
    Button {
        margin: 0 1;
        min-width: 20;
    }
    
    Button.start {
        background: $success;
    }
    
    Button.stop {
        background: $error;
    }
    
    Button.refresh {
        background: $primary;
        width: 100%;
    }
    
    OptionList {
        height: 15;
        border: solid $primary;
    }
    
    Input {
        width: 20;
    }
    
    .disabled {
        opacity: 0.5;
    }
    
    .hint {
        color: $text-muted;
        text-style: italic;
        margin: 0 0 1 0;
    }
    """

    server_process: Optional[subprocess.Popen] = None
    _server_running: bool = False

    @staticmethod
    def get_app_directory() -> Path:
        """Get the application directory path.
        
        Handles both running from source and from PyInstaller executable.
        When running from PyInstaller exe, uses sys.executable to get the
        directory where the exe is located. Otherwise uses __file__.
        
        Returns:
            Path: The application directory path.
        """
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).parent.resolve()

    def on_mount(self) -> None:
        """Called when the application is mounted.
        
        Initializes periodic RAM usage updates and loads the initial model list.
        """
        self.set_interval(1.0, self.update_ram_usage)
        self.load_models()

    def compose(self) -> ComposeResult:
        """Compose the application UI.
        
        Yields all widgets and containers that make up the TUI interface.
        Layout: Header -> Status Bar -> Two-column content -> Log -> Footer.
        
        Yields:
            ComposeResult: Header, status bar, content container, log, and footer.
        """
        yield Header()
        yield Container(
            Static("RAM Usage: Calculating...", id="status-text"),
            id="status-bar",
        )
        yield Container(
            Horizontal(
                Vertical(
                    Static("Context Window (4096-65536, step 1024):", classes="section"),
                    Input(value="4096", placeholder="4096-65536", id="context-input"),
                    Static("Valid: 4096, 5120, 6144, 7168, 8192, ...", id="context-hint", classes="hint"),
                    Static("", classes="section"),
                    Horizontal(
                        Button("Start Server", id="start-btn", classes="start"),
                        Button("Stop Server", id="stop-btn", classes="stop", disabled=True),
                    ),
                    id="left-column",
                ),
                Vertical(
                    Static("Select Model:", classes="section"),
                    OptionList(id="model-list"),
                    Button("Refresh", id="refresh-btn", classes="refresh"),
                    id="right-column",
                ),
                id="content-layout",
            ),
            id="main-container",
        )
        yield Log(id="log-area")
        yield Footer()

    def load_models(self) -> None:
        """Load GGUF model files from the models directory.
        
        Scans the `./models/` subdirectory for GGUF files and populates
        the model OptionList. Displays a message indicating the number of
        models found or if no models were found.
        """
        models_dir = self.get_app_directory() / "models"
        gguf_files = []
        
        if models_dir.exists():
            gguf_files = sorted(models_dir.glob("*.gguf"))
        
        model_list = self.query_one("#model-list", OptionList)
        model_list.clear_options()
        
        if gguf_files:
            for gguf_file in gguf_files:
                model_list.add_option(Option(str(gguf_file.relative_to(models_dir)), id=str(gguf_file)))
            self.log_message(f"Found {len(gguf_files)} model(s) in /models")
        else:
            model_list.add_option(Option("No GGUF files found in /models", disabled=True))
            self.log_message("No GGUF models found in /models folder")
    
    def get_selected_model_path(self) -> Optional[str]:
        """Get the full path of the currently selected model.
        
        Retrieves the highlighted option from the model list and returns
        its full file path. Returns None if no model is selected or if the
        selected option is disabled.
        
        Returns:
            Optional[str]: Full path to the selected GGUF file, or None.
        """
        model_list = self.query_one("#model-list", OptionList)
        if not model_list.option_count:
            return None
        highlighted = model_list.highlighted
        if highlighted is None:
            return None
        option = model_list.get_option_at_index(highlighted)
        if option.disabled:
            return None
        return str(option.id)

    def update_ram_usage(self) -> None:
        """Update the RAM usage display in the status bar.
        
        Polls the llama-server process and calculates its RAM usage.
        Updates the status bar text with current usage and server status.
        Called automatically every second via a timer.
        """
        status_text = self.query_one("#status-text", Static)
        
        if self.server_process and self.server_process.poll() is None:
            try:
                process = psutil.Process(self.server_process.pid)
                ram_mb = process.memory_info().rss / (1024 * 1024)
                status_text.update(f"RAM Usage: {ram_mb:.2f} MB | Status: Running")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                status_text.update("RAM Usage: N/A | Status: Stopped")
                self._update_button_states(False)
        else:
            status_text.update("RAM Usage: 0 MB | Status: Stopped")
            self._update_button_states(False)

    def _update_button_states(self, running: bool) -> None:
        """Update the enabled/disabled state of start/stop buttons.
        
        Args:
            running (bool): True if server is running, False otherwise.
        """
        self._server_running = running
        start_btn = self.query_one("#start-btn", Button)
        stop_btn = self.query_one("#stop-btn", Button)
        
        start_btn.disabled = running
        stop_btn.disabled = not running

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.
        
        Routes button presses to appropriate handler methods based on button ID.
        
        Args:
            event (Button.Pressed): The button press event.
        """
        if event.button.id == "start-btn":
            self.start_server()
        elif event.button.id == "stop-btn":
            self.stop_server()
        elif event.button.id == "refresh-btn":
            self.load_models()
            self.log_message("Model list refreshed")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field change events.
        
        Updates the context window hint text when the context input changes.
        
        Args:
            event (Input.Changed): The input change event.
        """
        if event.input.id == "context-input":
            self.update_context_hint()
    
    def update_context_hint(self) -> None:
        """Update the context window validation hint.
        
        Validates the current context window input and displays appropriate
        feedback: green for valid values, yellow with suggestions for nearby
        valid values, red for invalid values.
        """
        context_input = self.query_one("#context-input", Input)
        context_hint = self.query_one("#context-hint", Static)
        
        try:
            value = int(context_input.value)
            
            if value < 4096 or value > 65536:
                context_hint.update("[red]Invalid: must be 4096-65536[/red]")
                return
            
            remainder = value % 1024
            if remainder == 0:
                context_hint.update(f"[green]Valid: {value}[/green]")
            else:
                lower = (value // 1024) * 1024
                upper = lower + 1024
                
                if upper > 65536:
                    context_hint.update(f"[yellow]Nearest valid: {lower}[/yellow]")
                elif lower < 4096:
                    context_hint.update(f"[yellow]Nearest valid: {upper}[/yellow]")
                else:
                    suggestion = lower if (value - lower) < (upper - value) else upper
                    context_hint.update(f"[yellow]Nearest valid: {lower} or {upper} (suggested: {suggestion})[/yellow]")
        except ValueError:
            context_hint.update("[red]Enter a number[/red]")

    def start_server(self) -> None:
        """Start the llama.cpp server with the selected model and context size.
        
        Validates the selected model and context window settings, then launches
        llama-server.exe as a subprocess. Displays success/error messages in the log.
        Invalid context sizes are automatically clamped to nearest valid value.
        """
        context_input = self.query_one("#context-input", Input)
        
        model_path = self.get_selected_model_path()
        if model_path is None:
            self.log_message("Error: No model selected")
            return
        
        try:
            context_size = int(context_input.value)
            if context_size < 4096 or context_size > 65536:
                self.log_message("Error: Context size must be between 4096 and 65536")
                return
            if context_size % 1024 != 0:
                lower = (context_size // 1024) * 1024
                upper = lower + 1024
                if upper > 65536:
                    context_size = lower
                elif lower < 4096:
                    context_size = upper
                else:
                    context_size = lower if (context_size - lower) < (upper - context_size) else upper
                self.log_message(f"Auto-adjusted context size to nearest valid value: {context_size}")
        except ValueError:
            self.log_message("Error: Invalid context size")
            return
        
        app_dir = self.get_app_directory()
        llama_server = app_dir / "llama-server.exe"
        
        if not llama_server.exists():
            self.log_message(f"Error: llama-server.exe not found in {app_dir}")
            return
        
        try:
            self.server_process = subprocess.Popen(
                [
                    str(llama_server),
                    "--model", model_path,
                    "--ctx-size", str(context_size),
                    "--port", "8080",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self._update_button_states(True)
            self.log_message(f"Server started (PID: {self.server_process.pid})")
            self.log_message(f"Model: {Path(model_path).name}")
            self.log_message(f"Context size: {context_size} tokens")
        except Exception as e:
            self.log_message(f"Error starting server: {str(e)}")

    def stop_server(self) -> None:
        """Stop the running llama.cpp server.
        
        Attempts to gracefully terminate the server process. If the process
        does not terminate within 5 seconds, it is forcefully killed.
        Displays status messages in the log.
        """
        if self.server_process and self.server_process.poll() is None:
            try:
                pid = self.server_process.pid
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                self.log_message(f"Server stopped (PID: {pid})")
                self.server_process = None
                self._update_button_states(False)
            except subprocess.TimeoutExpired:
                if self.server_process:
                    self.server_process.kill()
                self.log_message("Server forcefully stopped")
                self.server_process = None
                self._update_button_states(False)
            except Exception as e:
                self.log_message(f"Error stopping server: {str(e)}")
        else:
            self.log_message("Server is not running")

    def log_message(self, message: str) -> None:
        """Add a message to the log area.
        
        Appends a line of text to the bottom log widget.
        
        Args:
            message (str): The message to log.
        """
        log_widget = self.query_one("#log-area", Log)
        log_widget.write_line(message)

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard events.
        
        Processes keyboard input, specifically handling the 'q' key to quit.
        Stops the server if running before exiting.
        
        Args:
            event (events.Key): The keyboard event.
        """
        if event.key == "q":
            if self._server_running:
                self.stop_server()
            self.exit()


if __name__ == "__main__":
    app = TUI_CPP()
    app.run()
