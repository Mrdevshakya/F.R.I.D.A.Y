"""
FRIDAY Text-to-Speech Module
This module handles all text-to-speech functionality for FRIDAY.
It provides multiple fallback methods for speech.
"""

# Chat-based assistant functionality
import pyttsx3
import threading
import queue
import time
import os
import subprocess
import platform
import tempfile
import sys

# Create a separate file for logging speech messages instead of printing them
speech_log_file = None
try:
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    speech_log_path = os.path.join("logs", "friday_speech.log")
    speech_log_file = open(speech_log_path, "a", encoding="utf-8")
    speech_log_file.write(f"\n\n--- FRIDAY SPEECH LOG STARTED AT {time.ctime()} ---\n\n")
except Exception as e:
    print(f"Warning: Could not create speech log file: {e}")
    speech_log_file = None

# Function to log speech messages without printing to console
def log_speech(message):
    """Log speech-related messages to file instead of printing to console"""
    if speech_log_file:
        try:
            speech_log_file.write(f"{time.ctime()}: {message}\n")
            speech_log_file.flush()
        except:
            pass

# Print system information only to log file
log_speech(f"System platform: {platform.system()}")
log_speech(f"Python version: {platform.python_version()}")

# Create a lock for thread synchronization
speech_lock = threading.Lock()

# Create a queue for speech tasks
speech_queue = queue.Queue()

# Flag to control the speech worker thread
speech_running = True

# Flag to track if speech engine is working
speech_engine_working = False

# Flag to determine which speech method to use
use_direct_method = True  # Set to True to force using direct method

# Determine the best speech method based on previous success
best_speech_method = "simple_vbs"  # Default to simplest method that works most reliably

# Global engine - initialized once
engine = None
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1.0)  # Max volume for better audibility
    
    # Get available voices and set a better voice if available
    voices = engine.getProperty('voices')
    log_speech(f"Available voices: {len(voices)}")
    for voice in voices:
        log_speech(f"Voice ID: {voice.id}, Name: {voice.name}")
        # Prefer English voice
        if "english" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            log_speech(f"Using voice: {voice.name}")
            break
    
    # Test if engine works
    try:
        engine.say("test")
        engine.runAndWait()
        speech_engine_working = True
        best_speech_method = "pyttsx3"
        log_speech("Text-to-speech engine initialized and tested successfully")
    except Exception as test_error:
        log_speech(f"pyttsx3 engine failed to speak test message: {test_error}")
        speech_engine_working = False
except Exception as e:
    log_speech(f"Error initializing speech engine: {e}")
    engine = None

# Simple direct VBS method - most reliable and doesn't require admin rights
def speak_with_simple_vbs(text):
    """Use a simple VBS script to speak text without requiring admin rights"""
    if platform.system() != "Windows":
        return False  # VBS only works on Windows
        
    try:
        # Create a temporary VBS script file in the system temp directory
        temp_file = os.path.join(tempfile.gettempdir(), "friday_speak.vbs")
        
        # Handle special characters and quotes that can break VBS strings
        # Break text into smaller chunks of 150 characters each to avoid VBS string issues
        chunks = [text[i:i+150] for i in range(0, len(text), 150)]
        
        # Create VBS script with proper character handling and multiple speak commands
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write('Set speech = CreateObject("SAPI.SpVoice")\n')
            for chunk in chunks:
                # Double quotes need to be doubled in VBS
                safe_chunk = chunk.replace('"', '""')
                # Remove problematic characters that could break VBS strings
                safe_chunk = ''.join(c for c in safe_chunk if ord(c) < 128)
                f.write(f'speech.Speak "{safe_chunk}"\n')
        
        # Add redirect to hide console output
        os.system(f'cscript //nologo "{temp_file}" >nul 2>&1')
        
        # Clean up the temp file
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
            
        return True
    except Exception as e:
        log_speech(f"Simple VBS speech error: {e}")
        return False

# Alternative direct method using wscript instead of cscript
def speak_with_wscript(text):
    """Use wscript instead of cscript for silent operation"""
    if platform.system() != "Windows":
        return False  # VBS only works on Windows
        
    try:
        # Create a temporary VBS script file in the system temp directory
        temp_file = os.path.join(tempfile.gettempdir(), "friday_speak2.vbs")
        
        # Handle special characters and quotes that can break VBS strings
        # Break text into smaller chunks to avoid VBS string issues
        chunks = [text[i:i+150] for i in range(0, len(text), 150)]
        
        # Create VBS script with proper character handling and multiple speak commands
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write('Set speech = CreateObject("SAPI.SpVoice")\n')
            for chunk in chunks:
                # Double quotes need to be doubled in VBS
                safe_chunk = chunk.replace('"', '""')
                # Remove problematic characters that could break VBS strings
                safe_chunk = ''.join(c for c in safe_chunk if ord(c) < 128)
                f.write(f'speech.Speak "{safe_chunk}"\n')
        
        # Run the script with wscript for silent operation (won't show any output)
        os.system(f'wscript "{temp_file}" >nul 2>&1')
        
        # Clean up the temp file
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
            
        return True
    except Exception as e:
        log_speech(f"Wscript speech error: {e}")
        return False

# Fallback speech method using Windows PowerShell
def speak_with_powershell(text):
    """Use Windows PowerShell to speak text (Windows only)"""
    if platform.system() != "Windows":
        return False  # PowerShell only works on Windows
        
    try:
        # Break text into smaller chunks
        chunks = [text[i:i+150] for i in range(0, len(text), 150)]
        
        for chunk in chunks:
            # Escape quotes in the text
            escaped_text = chunk.replace('"', '\\"').replace("'", "\\'")
            # Remove problematic characters
            escaped_text = ''.join(c for c in escaped_text if ord(c) < 128)
            # Run PowerShell command to speak the text
            command = f'powershell -command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{escaped_text}\')" >nul 2>&1'
            os.system(command)  # Use os.system instead of subprocess
        
        return True
    except Exception as e:
        log_speech(f"PowerShell speech error: {e}")
        return False

# Worker thread function to process speech queue
def speech_worker():
    """Worker thread that processes the speech queue"""
    global speech_running, engine, speech_engine_working, best_speech_method
    
    log_speech("Speech worker thread started")
    log_speech(f"Best speech method: {best_speech_method}")
    
    while speech_running:
        try:
            # Get the next text to speak (with 0.5 second timeout)
            try:
                text = speech_queue.get(timeout=0.5)
            except queue.Empty:
                # Queue is empty, just continue waiting
                continue
            
            # Don't try to speak empty text
            if not text or text.strip() == "":
                speech_queue.task_done()
                continue
                
            log_speech(f"Dequeued for speech: {text[:30]}..." if len(text) > 30 else f"Dequeued for speech: {text}")
            
            # If we're on a non-Windows system or forcing direct methods, try different approaches
            success = False
            
            # Try the best method first based on previous success
            if best_speech_method == "pyttsx3" and engine is not None and speech_engine_working:
                try:
                    with speech_lock:
                        log_speech(f"Speaking with pyttsx3: {text[:30]}..." if len(text) > 30 else f"Speaking with pyttsx3: {text}")
                        engine.say(text)
                        engine.runAndWait()
                        log_speech("Speech completed with pyttsx3")
                        success = True
                except Exception as e:
                    log_speech(f"pyttsx3 speech error: {e}")
                    speech_engine_working = False
            
            # If pyttsx3 failed or wasn't the best method
            if not success and platform.system() == "Windows":
                # Try simple VBS (Windows only)
                if best_speech_method == "simple_vbs" or not success:
                    if speak_with_simple_vbs(text):
                        log_speech("Speech completed with simple VBS")
                        best_speech_method = "simple_vbs"
                        success = True
                
                # If simple VBS failed or wasn't the best method
                if best_speech_method == "wscript" or not success:
                    if speak_with_wscript(text):
                        log_speech("Speech completed with wscript")
                        best_speech_method = "wscript"
                        success = True
                
                # If wscript failed or wasn't the best method
                if best_speech_method == "powershell" or not success:
                    if speak_with_powershell(text):
                        log_speech("Speech completed with PowerShell")
                        best_speech_method = "powershell"
                        success = True
            
            # If we're on a non-Windows system and pyttsx3 failed, we don't have other options
            if not success and platform.system() != "Windows":
                log_speech("No speech methods available for this platform")
            
            # Mark the task as done
            speech_queue.task_done()
            
        except Exception as e:
            log_speech(f"Speech worker error: {e}")
            # If there was a text to speak, just mark it as done
            if 'text' in locals() and text:
                speech_queue.task_done()
    
    log_speech("Speech worker thread stopping")

# Start the speech worker thread
speech_thread = threading.Thread(target=speech_worker, name="FRIDAY-SpeechWorker")
speech_thread.daemon = True
speech_thread.start()

def speak_text(text):
    """
    Speak the given text using the available speech engine
    
    Args:
        text (str): The text to speak
        
    Returns:
        None
    """
    # Don't try to speak empty text
    if not text or text.strip() == "":
        return
        
    # Log to file instead of printing to console
    log_speech(f"Queuing for speech: {text}")
    
    # Add the text to the speech queue for the worker thread to process
    speech_queue.put(text)

def get_input():
    """
    Get input from the user
    
    Returns:
        str: The user's input
    """
    return input("You: ")

def respond(text):
    """
    Display and speak FRIDAY's response
    
    Args:
        text (str): The response to display and speak
        
    Returns:
        str: The response text (for convenience)
    """
    # Only log the response, don't print to console as it will be handled by UI
    log_speech(f"Response: {text}")
    
    # Queue the text for speech
    speak_text(text)
    
    # Return the text for convenience
    return text

# Update global flag to track if speech is running
speech_running = True

# Cleanup function to be called when the program exits
def cleanup():
    """Cleanup resources when the program exits"""
    global speech_running, speech_log_file
    
    # Stop the speech worker thread
    speech_running = False
    
    # Wait for the thread to finish (with timeout)
    if 'speech_thread' in globals() and speech_thread.is_alive():
        speech_thread.join(timeout=1.0)
    
    # Close the speech log file
    if speech_log_file:
        try:
            speech_log_file.write(f"\n--- FRIDAY SPEECH LOG ENDED AT {time.ctime()} ---\n\n")
            speech_log_file.close()
        except:
            pass
            
# Register cleanup function
import atexit
atexit.register(cleanup)
