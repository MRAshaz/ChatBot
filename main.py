import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import customtkinter as ctk
import google.generativeai as genai
import sys, os, threading
import pyttsx3


class ChatBotApp:
    def __init__(self):
        # Initialize API
        genai.configure(api_key="Enter your api key") # --> Your gemini api key will go here.

        # Initialize instance variables
        self.model = None
        self.chat_session = None
        self.last_bot_response = ""
        self.engine = None
        self.history_window = None

        # Threading locks
        self.history_lock = threading.Lock()
        self.engine_lock = threading.Lock()

        # Available models
        self.models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]

        # Setup UI
        self._setup_ui()
        self._initialize_model()

    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def _setup_ui(self):
        """Initialize the user interface"""
        ctk.set_appearance_mode("system")

        # Main window
        self.win = ctk.CTk()
        self.WIDTH, self.HEIGHT = 900, 900
        self.win.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.win.title("Chad Bot")

        # Bottom frame for controls (pack this FIRST)
        self.round_frame = ctk.CTkFrame(self.win, corner_radius=15)
        self.round_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # Chat display (pack this AFTER the bottom frame)
        self.chat_font = ("Verdana", 12)
        self.chat = ScrolledText(self.win, wrap=tk.WORD, height=100, width=self.WIDTH)
        self.chat.configure(font=self.chat_font, state="normal")
        self.chat.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tags for styling messages
        self.chat.tag_configure("info_tag", foreground="green")
        self.chat.tag_configure("error_tag", foreground="red")

        # Model selection dropdown
        self.model_selection = ctk.CTkComboBox(
            self.round_frame,
            values=self.models,
            text_color="aquamarine2",
            fg_color="SlateBlue3",
            bg_color="LightBlue4",
            command=self._change_model_callback,
            width=150,
        )
        self.model_selection.pack(side="left", padx=(10, 5), pady=10)
        self.model_selection.set(self.models[0])

        # User input field
        self.user = ctk.CTkEntry(self.round_frame, border_width=0, height=30)
        self.user.pack(side="left", padx=5, pady=10, fill="x", expand=True)
        self.user.bind("<Return>", lambda event: self._send_message())

        # Send button
        self.send_button = ctk.CTkButton(
            self.round_frame, text="Send", command=self._send_message, width=80
        )
        self.send_button.pack(side="left", padx=5, pady=10)

        # Speak button
        self.speak_button = ctk.CTkButton(
            self.round_frame, text="Speak", command=self._text_to_speech, width=80
        )
        self.speak_button.pack(side="left", padx=5, pady=10)

        # Stop button
        self.stop_button = ctk.CTkButton(
            self.round_frame, text="Stop", command=self._kill_speech, width=80
        )
        self.stop_button.pack(side="left", padx=(5, 10), pady=10)

        # Menu bar
        self._setup_menu()

        # Keyboard shortcuts
        self.win.bind("<Command-p>", lambda x: self._text_to_speech())
        self.win.bind("<Command-s>", lambda x: self._kill_speech())

    def _setup_menu(self):
        """Setup the menu bar"""
        menubar = tk.Menu(self.win)
        history_menu = tk.Menu(menubar, tearoff=0)
        history_menu.add_command(label="Show history", command=self._show_history)
        menubar.add_cascade(label="History", menu=history_menu)
        self.win.config(menu=menubar)

    def _initialize_model(self):
        """Initialize the AI model and chat session"""
        initial_model = self.models[0]
        self.model = genai.GenerativeModel(initial_model)
        self.chat_session = self.model.start_chat(history=[])

    def _get_bot_response(self, user_turn: str) -> str:
        """Get response from the AI model"""
        try:
            with self.history_lock:
                if self.chat_session:
                    response = self.chat_session.send_message(user_turn)
                    # Save to file
                    with open(self.resource_path("data.txt"), "a") as file:
                        file.write(f"Bot: {response.text}\n")
                    return response.text
                else:
                    return "Error: Chat session not initialized."
        except Exception as e:
            print(f"Error getting bot response: {e}")
            return f"Error: {str(e)}"

    def _send_message(self):
        """Handle sending user message"""
        user_input = self.user.get()

        # Save user input to file
        with open(self.resource_path("data.txt"), "a") as file:
            file.write(f"You: {user_input}\n")

        if not user_input.strip():  # Don't send empty messages
            return

        # Display user message
        self.chat.insert(tk.END, f"You: {str(user_input)}\n")
        self.user.delete(0, tk.END)

        # Handle response in background thread
        threading.Thread(
            target=self._handle_response, args=(user_input,), daemon=True
        ).start()

    def _handle_response(self, prompt):
        """Handle AI response in background thread"""
        try:
            response = self._get_bot_response(prompt)
            safe_response = "Bot: " + str(response) + "\n"
            self.last_bot_response = str(response)

            # Update UI in main thread
            self.chat.after(0, lambda: self.chat.insert(tk.END, safe_response))
        except Exception as e:
            print("Exception in thread:", e)
            error_msg = "Bot: [Error] " + str(e) + "\n"
            self.chat.after(0, lambda: self.chat.insert(tk.END, error_msg))

    def _speak(self):
        """Handle text-to-speech functionality"""
        with self.engine_lock:
            if not self.last_bot_response.strip():
                self.chat.after(
                    0,
                    lambda: self.chat.insert(
                        tk.END, "Error! No bot response to speak\n"
                    ),
                )
                return

            if self.engine is None:
                self.engine = pyttsx3.init()

            voices = self.engine.getProperty("voices")
            if len(voices) > 14:
                self.engine.setProperty("voice", voices[14].id)
            self.engine.setProperty("rate", 180)
            self.engine.setProperty("volume", 1.0)

            self.engine.say(self.last_bot_response)
            self.engine.runAndWait()

    def _text_to_speech(self):
        """Start text-to-speech in background thread"""
        threading.Thread(target=self._speak, daemon=True).start()

    def _kill_speech(self):
        """Stop current speech"""
        with self.engine_lock:
            if self.engine is not None:
                self.engine.stop()
                self.engine = None

    def _change_model_callback(self, selected_model_name):
        """Handle model change from dropdown"""
        try:
            # Re-initialize the model
            self.model = genai.GenerativeModel(selected_model_name)
            # Start a new chat session with empty history
            self.chat_session = self.model.start_chat(history=[])

            # Clear previous conversation from display
            self.chat.delete("1.0", tk.END)
            self.chat.insert(
                tk.END,
                f"--- Switched to model: {selected_model_name} ---\n",
                "info_tag",
            )
        except Exception as e:
            self.chat.insert(
                tk.END, f"--- Error changing model: {str(e)} ---\n", "error_tag"
            )
            print(f"Error changing model: {e}")

    def _show_history(self):
        """Show chat history in a new window"""
        if self.history_window is not None and self.history_window.winfo_exists():
            # If already open, bring it to front
            self.history_window.deiconify()
            self.history_window.lift()
            self.history_window.focus_force()
            return

        self.win.withdraw()

        def on_close():
            self.history_window.destroy()
            self.history_window = None
            self.win.deiconify()  # Show main window again

        self.history_window = ctk.CTkToplevel()
        self.history_window.geometry(f"{self.HEIGHT}x{self.WIDTH}")
        self.history_window.title("History")

        file_content_textbox = ctk.CTkTextbox(self.history_window, wrap="word")
        file_content_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Load history file
        self._open_file(self.resource_path("data.txt"), file_content_textbox)

        button = ctk.CTkButton(self.history_window, text="Close", command=on_close)
        button.pack(pady=50)

        self.history_window.protocol("WM_DELETE_WINDOW", on_close)

    def _open_file(self, file_path, text_widget):
        """Open and display file content in text widget"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                text_widget.delete("1.0", "end")
                text_widget.insert("1.0", content)
        except FileNotFoundError:
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", f"Error: File not found at {file_path}")
        except Exception as e:
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", f"An error occurred: {e}")

    def run(self):
        """Start the application"""
        self.win.mainloop()


def main():
    """Main function to run the application"""
    app = ChatBotApp()
    app.run()


if __name__ == "__main__":
    main()
