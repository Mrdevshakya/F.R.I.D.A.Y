import tkinter as tk
from tkinter import scrolledtext, Entry, Button, END, messagebox, Frame, Label, StringVar, BooleanVar, Menu
import threading
import sys
import time
import os
from brain.brain import process_command, get_time_greeting
from brain.text import speak_text, speech_running
import re
import traceback

# Redirect standard output to prevent speech processing messages from appearing in the console
class OutputRedirector:
    def __init__(self):
        self.buffer = []
        self.old_stdout = sys.stdout
        
    def write(self, text):
        # Filter out speech processing messages
        if text.strip() and not any(msg in text for msg in [
            "[TTS]",               # Filter for TTS messages
            "Speaking:",           # Filter for "Speaking: " messages
            "Speech completed", 
            "Queuing for speech", 
            "Dequeued for speech",
            "Speaking with",
            "speech error",
            "speech worker",
            "pyttsx3"              # Filter any pyttsx3 messages
        ]):
            self.old_stdout.write(text)
            self.buffer.append(text)
            
    def flush(self):
        self.old_stdout.flush()
        
    def restore(self):
        sys.stdout = self.old_stdout

# Setup output redirection
output_redirector = OutputRedirector()
sys.stdout = output_redirector

class FridayChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FRIDAY - Personal AI Assistant")
        self.root.geometry("900x600")  # Larger default size
        self.root.minsize(600, 400)    # Set minimum window size
        self.root.resizable(True, True)
        
        # Theme settings
        self.is_dark_mode = BooleanVar(value=True)
        self.theme_colors = {
            "dark": {
                "bg": "#000000",          # Background
                "text": "#FFFFFF",        # Primary text
                "user_text": "#00ff00",   # User message color
                "ai_text": "#0091ff",     # AI response color
                "input_bg": "#111111",    # Input field background
                "status_online": "#2ecc71", # Online status color
                "status_busy": "#e74c3c",   # Busy status color
                "accent": "#505050"       # Accent color for borders
            },
            "light": {
                "bg": "#f5f5f5",          # Background
                "text": "#333333",        # Primary text
                "user_text": "#006600",   # User message color
                "ai_text": "#0066cc",     # AI response color
                "input_bg": "#ffffff",    # Input field background
                "status_online": "#27ae60", # Online status color
                "status_busy": "#c0392b",   # Busy status color
                "accent": "#dddddd"       # Accent color for borders
            }
        }
        
        # Set protocol for closing window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Handle Ctrl+C in the main window
        self.root.bind("<Control-c>", self.on_ctrl_c)
        
        # Create main container frame
        self.main_frame = Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a menu bar
        self.menu_bar = Menu(root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)
        
        # View menu
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_checkbutton(label="Dark Mode", variable=self.is_dark_mode, 
                                      command=self.toggle_theme)
        
        # Help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About FRIDAY", command=self.show_about)
        self.help_menu.add_command(label="Commands", command=self.show_commands)
        
        # Chat display area with custom tag configuration for different message types
        self.chat_area = scrolledtext.ScrolledText(
            self.main_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 11),
            padx=30,  
            pady=20,
            borderwidth=0,
            highlightthickness=0
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_area.config(state=tk.DISABLED)
        
        # Configure tags for different message types
        self.configure_chat_tags()
        
        # Status bar
        self.status_bar = Frame(self.main_frame)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bottom area for FRIDAY label and status
        self.bottom_frame = Frame(self.main_frame, height=40)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))
        
        # FRIDAY label in the bottom left
        self.friday_label = Label(
            self.bottom_frame, 
            text="F.R.I.D.A.Y",
            font=("Arial", 24, "bold")
        )
        self.friday_label.pack(side=tk.LEFT, padx=30, pady=5, anchor="sw")
        
        # Input frame with improved styling
        self.input_frame = Frame(self.main_frame)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=30, pady=(0, 60))
        
        # Hint text for input field
        self.hint_text = StringVar()
        self.hint_text.set("Type your message here...")
        
        # Input field with hint text
        self.input_field = Entry(
            self.input_frame, 
            font=("Consolas", 12),
            relief=tk.FLAT,
            bd=10,
            textvariable=self.hint_text
        )
        self.input_field.pack(fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self.send_message)
        self.input_field.bind("<FocusIn>", self.on_entry_click)
        self.input_field.bind("<FocusOut>", self.on_focus_out)
        
        # Status indicator in the bottom right
        self.status_text = StringVar()
        self.status_text.set("ONLINE")
        self.search_status = Label(
            self.bottom_frame, 
            textvariable=self.status_text,
            font=("Arial", 12)
        )
        self.search_status.pack(side=tk.RIGHT, padx=30, pady=5, anchor="se")
        
        # Apply initial theme
        self.toggle_theme()
        
        # Set focus to input field
        self.input_field.focus()
        
        # Variable to track last message sender
        self.last_sender = None
        
        # Add version info to status bar
        version_label = Label(self.status_bar, text="FRIDAY v1.1.0", font=("Arial", 8))
        version_label.pack(side=tk.RIGHT, padx=10, pady=2)
    
    def configure_chat_tags(self):
        """Configure tags for different message types"""
        # Tags will be properly colored in toggle_theme method
        self.chat_area.tag_configure("user", justify="left", font=("Consolas", 11))
        self.chat_area.tag_configure("ai", justify="left", font=("Consolas", 11))
        self.chat_area.tag_configure("system", justify="center", font=("Consolas", 10, "italic"))
        self.chat_area.tag_configure("user_label", font=("Consolas", 11, "bold"))
        self.chat_area.tag_configure("ai_label", font=("Consolas", 11, "bold"))
    
    def toggle_theme(self):
        """Switch between light and dark theme"""
        theme = "dark" if self.is_dark_mode.get() else "light"
        colors = self.theme_colors[theme]
        
        # Apply colors to main window
        self.root.configure(bg=colors["bg"])
        self.main_frame.configure(bg=colors["bg"])
        self.bottom_frame.configure(bg=colors["bg"])
        self.input_frame.configure(bg=colors["bg"])
        self.status_bar.configure(bg=colors["bg"])
        
        # Apply colors to chat area
        self.chat_area.configure(bg=colors["bg"], fg=colors["text"])
        
        # Configure tag colors
        self.chat_area.tag_configure("user", foreground=colors["user_text"])
        self.chat_area.tag_configure("user_label", foreground=colors["user_text"])
        self.chat_area.tag_configure("ai", foreground=colors["ai_text"])
        self.chat_area.tag_configure("ai_label", foreground=colors["ai_text"])
        self.chat_area.tag_configure("system", foreground=colors["ai_text"])
        
        # Apply colors to labels
        self.friday_label.configure(bg=colors["bg"], fg=colors["text"])
        self.search_status.configure(bg=colors["bg"])
        
        # Update status color
        if self.status_text.get() == "ONLINE":
            self.search_status.config(fg=colors["status_online"])
        else:
            self.search_status.config(fg=colors["status_busy"])
        
        # Apply colors to input field
        self.input_field.configure(
            bg=colors["input_bg"],
            fg=colors["user_text"],
            insertbackground=colors["user_text"]
        )
    
    def on_entry_click(self, event):
        """Clear hint text when input field is clicked"""
        if self.hint_text.get() == "Type your message here...":
            self.hint_text.set("")
    
    def on_focus_out(self, event):
        """Restore hint text if input field is empty"""
        if self.hint_text.get() == "":
            self.hint_text.set("Type your message here...")
    
    def clear_chat(self):
        """Clear the chat history"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.delete(1.0, tk.END)
            self.chat_area.config(state=tk.DISABLED)
            self.update_chat("FRIDAY", "Chat history cleared. How can I help you?")
    
    def show_about(self):
        """Show information about FRIDAY"""
        about_text = (
            "FRIDAY - Female Replacement Intelligent Digital Assistant Youth\n\n"
            "Version: 1.1.0\n"
            "Created by: Abhishek\n\n"
            "FRIDAY is a personal AI assistant designed to help you with daily tasks, "
            "provide information, and control your applications."
        )
        messagebox.showinfo("About FRIDAY", about_text)
    
    def show_commands(self):
        """Show available commands"""
        commands_text = (
            "Available Commands:\n\n"
            "Basic Commands:\n"
            "- hello, hi - Get a greeting\n"
            "- time, date - Get current time/date\n"
            "- exit, quit, bye - End session\n\n"
            "Web Search:\n"
            "- who is... - Get information about people\n"
            "- what is... - Get definitions and explanations\n"
            "- search... - Explicitly search for information\n\n"
            "Applications:\n"
            "- open [app] - Launch applications\n"
            "- close [app] - Close applications\n\n"
            "Email:\n"
            "- write email [type] - Generate email templates\n"
        )
        messagebox.showinfo("FRIDAY Commands", commands_text)
    
    def on_closing(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit FRIDAY?"):
            # Display and speak goodbye message
            self.update_chat("FRIDAY", "Goodbye! Have a great day!")
            
            # Give time for speech to complete
            self.root.after(2000, self.root.destroy)
    
    def on_ctrl_c(self, event):
        """Handle Ctrl+C event"""
        self.on_closing()
    
    def update_chat(self, sender, message):
        """Add a message to the chat area with different styling for user and AI"""
        try:
            # Skip any speech processing status messages that might have gotten through
            if any(msg in message for msg in [
                "[TTS]",               # Filter for TTS messages
                "Speaking:",           # Filter for "Speaking: " messages
                "Speech completed", 
                "Queuing for speech", 
                "Dequeued for speech",
                "Speaking with",
                "speech error",
                "speech worker",
                "pyttsx3"              # Filter any pyttsx3 messages
            ]):
                return
                
            self.chat_area.config(state=tk.NORMAL)
            
            # Add proper line spacing based on current state and sender
            current_index = self.chat_area.index('end-1c')
            
            if current_index != '1.0':  # Not the first message
                # Get the last line of text to check if we need spacing
                last_line = self.chat_area.get("end-2l", "end-1c").strip()
                
                # Add appropriate spacing
                if last_line and not last_line.isspace():
                    self.chat_area.insert(tk.END, "\n")  # Single line break for spacing
            
            if sender == "You":
                # Add user message with proper label
                self.chat_area.insert(tk.END, "You:", "user_label")
                self.chat_area.insert(tk.END, f" {message}", "user")
            elif sender == "FRIDAY":
                # Add FRIDAY message with proper label
                self.chat_area.insert(tk.END, "FRIDAY:", "ai_label")
                self.chat_area.insert(tk.END, f" {message}", "ai")
                
                # Speak the response
                self.speak_message(message)
            else:
                # System messages
                self.chat_area.insert(tk.END, f"{message}", "system")
            
            # Remember the last sender for spacing
            self.last_sender = sender
            
            self.chat_area.see(tk.END)
            self.chat_area.config(state=tk.DISABLED)
        except Exception as e:
            # Log error without printing to console
            os.makedirs("logs", exist_ok=True)
            with open("logs/friday_error.log", "a") as f:
                f.write(f"{time.ctime()}: Error updating chat: {e}\n")
    
    def set_search_status(self, is_searching):
        """Update the search status indicator"""
        theme = "dark" if self.is_dark_mode.get() else "light"
        colors = self.theme_colors[theme]
        
        if is_searching:
            self.status_text.set("SEARCHING")
            self.search_status.config(fg=colors["status_busy"])
        else:
            self.status_text.set("ONLINE")
            self.search_status.config(fg=colors["status_online"])
    
    def send_message(self, event=None):
        """Process user input and display response"""
        try:
            # Get user input and handle hint text
            input_text = self.input_field.get().strip()
            
            # Skip empty messages or hint text
            if not input_text or input_text == "Type your message here...":
                return
                
            # Store the actual message 
            user_input = input_text
            
            # Display user message
            self.update_chat("You", user_input)
            
            # Clear input field
            self.input_field.delete(0, tk.END)
            
            # Reset hint text if focus is lost
            if not self.input_field.focus_get() == self.input_field:
                self.hint_text.set("Type your message here...")
            
            # Update status to searching
            self.set_search_status(True)
            
            # Process in a separate thread to keep UI responsive
            threading.Thread(target=self.process_and_respond, args=(user_input,), daemon=True).start()
        except Exception as e:
            # Log error to logs directory
            os.makedirs("logs", exist_ok=True)
            with open("logs/friday_error.log", "a") as f:
                f.write(f"{time.ctime()}: Error sending message: {e}\n")
            messagebox.showerror("Error", f"An error occurred while sending message: {e}")
        
    def process_and_respond(self, user_input):
        """Process the user input in a separate thread and update UI with response"""
        try:
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                response = "Goodbye! Have a great day!"
                self.root.after(0, lambda: self.update_chat("FRIDAY", response))
                self.root.after(0, lambda: self.set_search_status(False))
                
                # Allow time for goodbye speech to complete
                self.root.after(2500, self.root.destroy)
                return
                
            # Get response from brain
            response = process_command(user_input.lower())
            
            # Extract the important parts of the response for cleaner speech
            # Clean up any "Looking up information..." or "Web search completed..." messages
            cleaned_response = response
            if "Web search completed in" in response:
                parts = response.split("Web search completed in")
                seconds_parts = parts[1].split("seconds")
                if len(seconds_parts) > 1:
                    cleaned_response = parts[0] + seconds_parts[1]
            
            # Ensure web search results are properly formatted for speech
            # Fix common formatting issues to improve speech quality
            cleaned_response = cleaned_response.replace("More atWikipedia", "More at Wikipedia")
            cleaned_response = cleaned_response.replace("..", ".")
            cleaned_response = cleaned_response.replace("  ", " ")
            
            # Update UI with original response (safely from main thread)
            self.root.after(0, lambda: self.update_chat("FRIDAY", cleaned_response))
            self.root.after(0, lambda: self.set_search_status(False))
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.root.after(0, lambda: self.update_chat("FRIDAY", error_msg))
            self.root.after(0, lambda: self.set_search_status(False))
            # Log error to logs directory
            os.makedirs("logs", exist_ok=True)
            with open("logs/friday_error.log", "a") as f:
                f.write(f"{time.ctime()}: Error processing command: {e}\n")
    
    def speak_message(self, message):
        """Speak the entire message, breaking it down if needed for better speech processing"""
        try:
            # Clean the message first to improve speech quality
            speech_message = message
            
            # Remove any duplicate sentences that often appear in web search results
            sentences = re.split(r'(?<=[.!?])\s+', speech_message)
            unique_sentences = []
            for sentence in sentences:
                # Strip and normalize the sentence for comparison
                clean_sentence = ' '.join(sentence.lower().split())
                # Only add if not a near-duplicate of previous sentence
                if not any(clean_sentence in ' '.join(prev.lower().split()) for prev in unique_sentences[-3:] if prev):
                    unique_sentences.append(sentence)
            
            speech_message = ' '.join(unique_sentences)
            
            # Special handling for web search results which can be long
            if "Here's what I found" in message or "Web search completed" in message:
                # Remove timing information
                if "Web search completed in" in speech_message:
                    parts = speech_message.split("Web search completed in")
                    if len(parts) > 1 and "seconds" in parts[1]:
                        seconds_parts = parts[1].split("seconds")
                        speech_message = parts[0] + (seconds_parts[1] if len(seconds_parts) > 1 else "")
                
                # Clean up formatting for better speech
                speech_message = speech_message.replace("Here's what I found online:", "Here's what I found:")
                speech_message = speech_message.replace("Here's what I found from Wikipedia:", "Here's what I found from Wikipedia.")
                speech_message = speech_message.replace("More atWikipedia", "More at Wikipedia")
                speech_message = speech_message.replace("..", ".")
                speech_message = speech_message.replace("  ", " ")
                
                # First speak the introduction
                intro_parts = ["Here's what I found", "I found this information"]
                intro_part = next((part for part in intro_parts if part in speech_message), "Here's what I found for you.")
                
                # Extract intro sentence
                intro_match = re.search(r"(Here's what I found[^.!?]*[.!?])", speech_message)
                if intro_match:
                    intro_sentence = intro_match.group(1)
                    speak_text(intro_sentence)
                    
                    # Remove intro from content to avoid duplication
                    content_part = speech_message.replace(intro_sentence, "", 1).strip()
                else:
                    speak_text(intro_part)
                    content_part = speech_message.replace("Here's what I found:", "", 1).strip()
                
                # Brief pause before continuing
                time.sleep(0.3)
                
                # If the content is very long, break it into sentences
                if len(content_part) > 200:
                    sentences = re.split(r'(?<=[.!?])\s+', content_part)
                    for sentence in sentences:
                        if sentence.strip():
                            speak_text(sentence.strip())
                            time.sleep(0.1)  # Small pause between sentences
                else:
                    speak_text(content_part)
            else:
                # For normal responses, just speak the full message
                speak_text(speech_message)
        except Exception as e:
            # Log error to logs directory
            os.makedirs("logs", exist_ok=True)
            with open("logs/friday_error.log", "a") as f:
                f.write(f"{time.ctime()}: Error speaking message: {e}\n")

def main():
    """Main function to run the FRIDAY chat UI"""
    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Create the main window
        root = tk.Tk()
        
        # Set icon if available
        try:
            if os.path.exists("assets/friday_icon.ico"):
                root.iconbitmap("assets/friday_icon.ico")
        except:
            pass  # Continue without icon if not available
            
        # Create the FRIDAY chat UI
        app = FridayChatUI(root)
        
        # Display welcome message after a short delay to ensure proper UI rendering
        time_greeting = get_time_greeting()
        welcome_message = f"{time_greeting} I'm FRIDAY, at your service. How can I help you today?"
        
        # Use after to ensure UI is fully loaded before showing the message
        root.after(100, lambda: app.update_chat("FRIDAY", welcome_message))
        
        # Start the Tkinter event loop
        root.mainloop()
        
    except Exception as e:
        # Log error to file and display message box
        error_msg = f"An unexpected error occurred: {str(e)}"
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/friday_error.log", "a") as f:
            f.write(f"{time.ctime()}: {error_msg}\n")
            f.write(f"Traceback: {traceback.format_exc()}\n")
        
        # Try to show error message in GUI if possible
        try:
            messagebox.showerror("FRIDAY Error", error_msg)
        except:
            print(error_msg)
    
    finally:
        # Restore original stdout before exiting
        output_redirector.restore()
        
        # Ensure we properly exit
        try:
            sys.exit(0)
        except:
            os._exit(0)

if __name__ == "__main__":
    main() 