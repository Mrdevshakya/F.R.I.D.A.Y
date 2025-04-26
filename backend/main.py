from brain.text import respond, get_input, speak_text
from brain.brain import process_command, get_time_greeting
import sys
import time
import os
import re
import argparse
import colorama
from colorama import Fore, Style, Back

# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)

# Version information
VERSION = "1.1.0"
BUILD_DATE = "2025-04-25"

# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="FRIDAY - Personal AI Assistant")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice responses")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with verbose logging")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--clean", action="store_true", help="Clean log files before starting")
    return parser.parse_args()

# Function to ensure the entire message is spoken, especially for web search results
def speak_full_message(text, no_voice=False):
    """Ensure the entire message is spoken, breaking down long messages if needed"""
    if no_voice:
        return  # Skip voice output if voice is disabled
        
    try:
        # Special handling for web search results which can be long
        if "Here's what I found" in text:
            # First speak the introduction
            intro_part = "Here's what I found for you."
            speak_text(intro_part)
            
            # Brief pause before continuing
            time.sleep(0.3)
            
            # Then speak the actual content with chunking for long responses
            content_part = text.replace("Here's what I found online:", "").replace("Here's what I found from Wikipedia:", "").strip()
            
            # Clean up content for better speech
            content_part = content_part.replace("More atWikipedia", "More at Wikipedia")
            content_part = content_part.replace("..", ".")
            content_part = content_part.replace("  ", " ")
            
            # If the content is very long, break it into sentences
            if len(content_part) > 300:
                sentences = re.split(r'(?<=[.!?])\s+', content_part)
                for sentence in sentences:
                    if sentence.strip():
                        speak_text(sentence.strip())
                        time.sleep(0.1)  # Small pause between sentences
            else:
                speak_text(content_part)
        else:
            # For normal responses, just speak the full message
            speak_text(text)
    except Exception as e:
        # Log error without printing to console
        with open("logs/friday_error.log", "a") as f:
            f.write(f"{time.ctime()}: Error speaking message: {e}\n")

# Custom functions to ensure proper formatting
def custom_respond(text, no_voice=False):
    """
    Display assistant's response with proper formatting and queue it for speech
    """
    # Clean the text for better speech
    cleaned_text = text
    
    # Clean up any "Looking up information..." or "Web search completed..." messages
    if "Web search completed in" in text:
        parts = text.split("Web search completed in")
        seconds_parts = parts[1].split("seconds")
        if len(seconds_parts) > 1:
            cleaned_text = parts[0] + seconds_parts[1]
            
    # Fix common formatting issues
    cleaned_text = cleaned_text.replace("More atWikipedia", "More at Wikipedia")
    cleaned_text = cleaned_text.replace("..", ".")
    cleaned_text = cleaned_text.replace("  ", " ")
    
    # Print FRIDAY's response with proper line break before it
    response_text = f"\n{Fore.CYAN}{Style.BRIGHT}FRIDAY:{Style.RESET_ALL} {Fore.LIGHTBLUE_EX}{cleaned_text}{Style.RESET_ALL}"
    print(response_text)
    
    # Force a small delay before speaking (helps with speech engine timing)
    time.sleep(0.1)
    
    # Use our custom function to speak the full message
    if not no_voice:
        speak_full_message(cleaned_text, no_voice)
    
    # Return the cleaned text for convenience
    return cleaned_text

def custom_get_input():
    """
    Get text input from the user with proper formatting
    """
    # Make sure to flush stdout before displaying prompt
    sys.stdout.flush()
    
    # Print the prompt with proper formatting and flush to ensure it's visible
    prompt = f"{Fore.GREEN}{Style.BRIGHT}\nYou:{Style.RESET_ALL} "
    sys.stdout.write(prompt)
    sys.stdout.flush()
    
    # Get user input
    try:
        user_input = input()
        return user_input
    except EOFError:
        # Handle EOF (Ctrl+D) gracefully
        print("\nDetected EOF. Exiting...")
        return "exit"
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nDetected keyboard interrupt. Exiting...")
        return "exit"

def display_banner():
    """Display an ASCII art banner for FRIDAY"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
    ███████╗██████╗ ██╗██████╗  █████╗ ██╗   ██╗
    ██╔════╝██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝
    █████╗  ██████╔╝██║██║  ██║███████║ ╚████╔╝ 
    ██╔══╝  ██╔══██╗██║██║  ██║██╔══██║  ╚██╔╝  
    ██║     ██║  ██║██║██████╔╝██║  ██║   ██║   
    ╚═╝     ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   
                                  
{Style.RESET_ALL}{Fore.LIGHTBLUE_EX}Female Replacement Intelligent Digital Assistant Youth{Style.RESET_ALL}
{Fore.WHITE}Version {VERSION} | Type 'help' for commands | Type 'exit' to quit{Style.RESET_ALL}
"""
    print(banner)

def clean_log_files():
    """Clean log files to start fresh"""
    log_files = [
        "logs/friday_error.log",
        "logs/friday_search.log",
        "logs/friday_speech.log"
    ]
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    for log_file in log_files:
        try:
            if os.path.exists(log_file):
                # Backup the old log with timestamp
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                backup_file = f"{log_file}.{timestamp}.bak"
                os.rename(log_file, backup_file)
                
            # Create a new empty log file
            with open(log_file, "w") as f:
                f.write(f"Log file created at {time.ctime()}\n")
                
            print(f"{Fore.GREEN}Cleaned log file: {log_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error cleaning log file {log_file}: {e}{Style.RESET_ALL}")

def main():
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Show version info and exit if requested
        if args.version:
            print(f"FRIDAY Assistant v{VERSION}")
            print(f"Build date: {BUILD_DATE}")
            sys.exit(0)
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Clean log files if requested
        if args.clean:
            clean_log_files()
        
        # Clear the console screen for better appearance
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display banner
        display_banner()
        
        # Greet the user with time-appropriate greeting
        time_greeting = get_time_greeting()
        custom_respond(f"{time_greeting} I'm FRIDAY, at your service sir.", args.no_voice)
        
        # Main conversation loop
        running = True
        while running:
            try:
                # Get user input - this will display the "You: " prompt
                user_input = custom_get_input()
                
                # Exit condition - check before processing to avoid unnecessary computation
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    custom_respond("Goodbye! Have a great day!", args.no_voice)
                    running = False
                    continue
                    
                # Skip empty inputs
                if not user_input.strip():
                    continue
                    
                # Process user input using the brain module
                response = process_command(user_input)
                
                # Respond to the user
                custom_respond(response, args.no_voice)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Keyboard interrupt detected. Exiting...{Style.RESET_ALL}")
                custom_respond("Goodbye! Have a great day!", args.no_voice)
                running = False
            except Exception as e:
                error_msg = f"Oops! I encountered an error: {str(e)}"
                custom_respond(error_msg, args.no_voice)
                # Log error to file
                with open("logs/friday_error.log", "a") as f:
                    f.write(f"{time.ctime()}: Error details: {e}\n")
                
                # Show more details in debug mode
                if args.debug:
                    import traceback
                    traceback_str = traceback.format_exc()
                    print(f"{Fore.RED}Debug traceback: {traceback_str}{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program interrupted. Exiting...{Style.RESET_ALL}")
    except Exception as e:
        # Log error to file
        error_msg = f"An unexpected error occurred: {e}"
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/friday_error.log", "a") as f:
                f.write(f"{time.ctime()}: {error_msg}\n")
                
            # Show more details in debug mode
            if 'args' in locals() and args.debug:
                import traceback
                traceback_str = traceback.format_exc()
                print(f"{Fore.RED}Debug traceback: {traceback_str}{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}Critical error: {str(e)}{Style.RESET_ALL}")
    finally:
        print(f"\n{Fore.CYAN}FRIDAY has shut down.{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    main()
