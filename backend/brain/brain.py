# Brain module for FRIDAY assistant
# This module processes commands and returns appropriate responses

# Import any required libraries
from datetime import datetime
import requests
import re
import html
from urllib.parse import quote_plus
import urllib.parse  # Add explicit import for urllib.parse
import json
from bs4 import BeautifulSoup
import random
import webbrowser  # For opening web pages
import subprocess  # For launching applications
import os  # For file path operations
import concurrent.futures  # For parallel web searches
import time  # For timeout tracking
import wikipedia

# Import NAV predictor modules for stock and mutual fund analysis
from .nav_predictor.model import StockAnalyzer, MutualFundAnalyzer
from .nav_predictor.model import format_stock_analysis_response, format_mutual_fund_analysis_response

# For testing time-based greetings (simulated time)
_test_hour = None

# Initialize stock and mutual fund analyzers
stock_analyzer = StockAnalyzer()
mutual_fund_analyzer = MutualFundAnalyzer()

# List of user agents to rotate for avoiding detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
]

# Dictionary of common applications and their paths or commands
APPLICATIONS = {
    # Browsers
    "chrome": {
        "windows": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "windows_alt": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "command": "google-chrome"
    },
    "firefox": {
        "windows": r"C:\Program Files\Mozilla Firefox\firefox.exe",
        "windows_alt": r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        "command": "firefox"
    },
    "edge": {
        "windows": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "command": "msedge"
    },
    
    # Microsoft Office apps
    "word": {
        "windows": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "windows_alt": r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        "command": "winword"
    },
    "excel": {
        "windows": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "windows_alt": r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
        "command": "excel"
    },
    "powerpoint": {
        "windows": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "windows_alt": r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
        "command": "powerpnt"
    },
    
    # System utilities
    "notepad": {
        "windows": r"C:\Windows\System32\notepad.exe",
        "command": "notepad"
    },
    "calculator": {
        "windows": r"C:\Windows\System32\calc.exe",
        "command": "calc"
    },
    "settings": {
        "windows": "ms-settings:",
        "command": "start ms-settings:"
    },
    "control panel": {
        "windows": r"C:\Windows\System32\control.exe",
        "command": "control"
    },
    "file explorer": {
        "windows": r"C:\Windows\explorer.exe",
        "command": "explorer"
    },
    "task manager": {
        "windows": r"C:\Windows\System32\taskmgr.exe",
        "command": "taskmgr"
    },
    
    # Messaging apps
    "whatsapp": {
        "windows": r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe",
        "windows_alt": r"C:\Users\%USERNAME%\AppData\Local\Programs\WhatsApp\WhatsApp.exe",
        "command": "WhatsApp"
    },
    "telegram": {
        "windows": r"C:\Users\%USERNAME%\AppData\Roaming\Telegram Desktop\Telegram.exe",
        "command": "telegram"
    }
}

def set_test_hour(hour):
    """
    Set a test hour for testing time-based greetings
    
    Args:
        hour (int): Hour of the day (0-23)
    """
    global _test_hour
    if 0 <= hour <= 23:
        _test_hour = hour
    else:
        _test_hour = None

def get_time_greeting():
    """
    Return a greeting based on the current time of day
    
    Returns:
        str: Time-appropriate greeting
    """
    # Use test hour if set, otherwise use actual current hour
    if _test_hour is not None:
        current_hour = _test_hour
    else:
        current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        return "Good morning!"
    elif 12 <= current_hour < 17:
        return "Good afternoon!"
    elif 17 <= current_hour < 21:
        return "Good evening!"
    else:
        return "Good night!"

def open_application(app_name):
    """
    Open a specified application
    
    Args:
        app_name (str): The name of the application to open
        
    Returns:
        str: Success or error message
    """
    app_name = app_name.lower()
    
    # Check if the app is in our dictionary
    if app_name in APPLICATIONS:
        app_info = APPLICATIONS[app_name]
        
        try:
            # Check if we're on Windows
            if os.name == 'nt':
                # Try primary Windows path
                if "windows" in app_info and os.path.exists(app_info["windows"].replace("%USERNAME%", os.getenv("USERNAME"))):
                    path = app_info["windows"].replace("%USERNAME%", os.getenv("USERNAME"))
                    subprocess.Popen(path)
                    return f"Opening {app_name.capitalize()}."
                
                # Try alternative Windows path
                elif "windows_alt" in app_info and os.path.exists(app_info["windows_alt"].replace("%USERNAME%", os.getenv("USERNAME"))):
                    path = app_info["windows_alt"].replace("%USERNAME%", os.getenv("USERNAME"))
                    subprocess.Popen(path)
                    return f"Opening {app_name.capitalize()}."
                
                # For Windows-specific commands like 'ms-settings:'
                elif app_name == "settings":
                    os.system("start ms-settings:")
                    return f"Opening Windows Settings."
                
                # Try the command as a last resort
                else:
                    subprocess.Popen(app_info["command"], shell=True)
                    return f"Attempting to open {app_name.capitalize()}."
            
            # For other operating systems, use the command
            else:
                subprocess.Popen(app_info["command"], shell=True)
                return f"Attempting to open {app_name.capitalize()}."
                
        except Exception as e:
            return f"I couldn't open {app_name}. Error: {str(e)}"
    
    # For common Windows apps that might not be in our dictionary
    elif os.name == 'nt':
        try:
            # Try using the app name directly with the 'start' command
            os.system(f"start {app_name}")
            return f"Attempting to open {app_name.capitalize()}."
        except Exception as e:
            return f"I couldn't find {app_name}. Please make sure it's installed and try again."
    
    else:
        return f"I don't know how to open {app_name}. Please make sure it's installed and try again."

def close_application(app_name):
    """
    Close a specified application
    
    Args:
        app_name (str): The name of the application to close
        
    Returns:
        str: Success or error message
    """
    app_name = app_name.lower()
    
    # Process name mappings (expand as needed)
    process_mappings = {
        # Browsers
        "chrome": ["chrome.exe"],
        "firefox": ["firefox.exe"],
        "edge": ["msedge.exe"],
        
        # Microsoft Office apps
        "word": ["winword.exe"],
        "excel": ["excel.exe"],
        "powerpoint": ["powerpnt.exe"],
        
        # System utilities
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "settings": ["SystemSettings.exe"],
        "control panel": ["control.exe"],
        "file explorer": ["explorer.exe"],
        "task manager": ["taskmgr.exe"],
        
        # Messaging apps
        "whatsapp": ["WhatsApp.exe"],
        "telegram": ["Telegram.exe"],
    }
    
    # Additional mappings for common apps
    if app_name in APPLICATIONS and app_name not in process_mappings:
        # Extract process name from the path
        for key in ["windows", "windows_alt"]:
            if key in APPLICATIONS[app_name]:
                path = APPLICATIONS[app_name][key]
                process_name = os.path.basename(path)
                process_mappings[app_name] = [process_name]
                break
    
    try:
        # Check if we're on Windows
        if os.name == 'nt':
            # If app is in our mapping
            if app_name in process_mappings:
                closed = False
                for process in process_mappings[app_name]:
                    try:
                        # Use PowerShell to check if the process is running and then kill it
                        # First check if process exists
                        check_process_cmd = f'powershell "Get-Process -Name \'{process.replace(".exe", "")}\' -ErrorAction SilentlyContinue"'
                        process_check = subprocess.run(check_process_cmd, shell=True, capture_output=True, text=True)
                        
                        if process_check.returncode == 0 and process_check.stdout.strip():
                            # Process exists, kill it
                            kill_cmd = f'powershell "Stop-Process -Name \'{process.replace(".exe", "")}\' -Force"'
                            kill_result = subprocess.run(kill_cmd, shell=True, capture_output=True, text=True)
                            if kill_result.returncode == 0:
                                closed = True
                        elif app_name == "calculator" and process == "calc.exe":
                            # Special handling for Calculator which might be running as ApplicationFrameHost
                            special_kill = 'powershell "Get-Process | Where-Object {$_.MainWindowTitle -like \'*Calculator*\'} | Stop-Process -Force"'
                            kill_result = subprocess.run(special_kill, shell=True, capture_output=True, text=True)
                            if kill_result.returncode == 0:
                                closed = True
                    except Exception as e:
                        print(f"Error closing {process}: {e}")
                
                if closed:
                    return f"Closed {app_name.capitalize()}."
                else:
                    return f"I couldn't find {app_name} running. Is it open?"
            
            # For apps not in our mapping, try using the app name as the process name
            else:
                # Try with process name (without .exe)
                process_name = app_name.replace(".exe", "")
                check_process_cmd = f'powershell "Get-Process -Name \'{process_name}\' -ErrorAction SilentlyContinue"'
                process_check = subprocess.run(check_process_cmd, shell=True, capture_output=True, text=True)
                
                if process_check.returncode == 0 and process_check.stdout.strip():
                    # Process exists, kill it
                    kill_cmd = f'powershell "Stop-Process -Name \'{process_name}\' -Force"'
                    kill_result = subprocess.run(kill_cmd, shell=True, capture_output=True, text=True)
                    if kill_result.returncode == 0:
                        return f"Closed {app_name.capitalize()}."
                
                # Try finding by window title as a last resort
                try:
                    fuzzy_cmd = f'powershell "Get-Process | Where-Object {{$_.MainWindowTitle -like \'*{app_name}*\'}} | Stop-Process -Force"'
                    fuzzy_result = subprocess.run(fuzzy_cmd, shell=True, capture_output=True, text=True)
                    if fuzzy_result.returncode == 0:
                        return f"Closed application with '{app_name}' in its title."
                except Exception as e:
                    print(f"Error in window title processing: {e}")
                
                return f"I couldn't find {app_name} running. Is it open?"
        else:
            # For other operating systems, use pkill
            result = subprocess.run(["pkill", "-f", app_name], 
                                   shell=True,  # Shell is needed for pkill on Linux/Mac
                                   capture_output=True, 
                                   text=True, 
                                   check=False)
            
            if result.returncode == 0:
                return f"Closed {app_name.capitalize()}."
            else:
                return f"I couldn't find {app_name} running. Is it open?"
                
    except Exception as e:
        return f"I couldn't close {app_name}. Error: {str(e)}"

def open_web_page(query):
    """
    Open a web browser with search results for the given query
    
    Args:
        query (str): The search query
        
    Returns:
        str: A message indicating that the browser was opened
    """
    try:
        # Encode the query for URL
        encoded_query = quote_plus(query)
        
        # Create search URLs for different search engines
        google_url = f"https://www.google.com/search?q={encoded_query}"
        wikipedia_url = f"https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}"
        
        # Try to open Wikipedia first for educational/informational queries
        if any(word in query.lower() for word in ["who", "what", "where", "when", "why", "how"]):
            webbrowser.open(wikipedia_url)
            return f"Opening Wikipedia search for '{query}' in your web browser."
        else:
            # Default to Google for general queries
            webbrowser.open(google_url)
            return f"Opening Google search for '{query}' in your web browser."
    
    except Exception as e:
        print(f"Error opening web browser: {e}")
        return f"I tried to open a web browser but encountered an error: {str(e)}"

def log_to_file(message):
    """
    Log messages to a file instead of printing to console
    """
    try:
        with open("friday_search.log", "a", encoding="utf-8") as f:
            f.write(f"{time.ctime()}: {message}\n")
            f.flush()
    except:
        # If logging fails, just silently continue
        pass

def search_web(query):
    """
    Search the web for information on the given query using a combination of
    search engines and techniques to get reliable results.
    
    Args:
        query (str): The search query
        
    Returns:
        str: The search results or an error message, formatted for both display and speech
    """
    # Log the search to a file instead of printing to console
    log_to_file(f"Searching for information about '{query}'...")
    
    # Use concurrent execution to search multiple sources in parallel
    start_time = time.time()
    timeout = 5  # Maximum seconds to wait for all searches
    
    # Initialize results dictionary
    results = {"wikipedia": None, "duckduckgo": None, "bing": None}
    
    # Create a thread pool executor
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit search tasks to the executor
        futures = {
            executor.submit(search_wikipedia, query): "wikipedia",
            executor.submit(search_duckduckgo, query): "duckduckgo",
            executor.submit(search_bing, query): "bing"
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures, timeout=timeout):
            engine = futures[future]
            try:
                results[engine] = future.result()
            except Exception as e:
                log_to_file(f"{engine.capitalize()} search error: {e}")
    
    # Calculate elapsed time
    elapsed = time.time() - start_time
    log_to_file(f"Web search completed in {elapsed:.2f} seconds")
    
    # Format the result for better readability and speech
    def format_result(text, source):
        # Clean up the text
        cleaned_text = text
        
        # Remove redundant spaces and newlines
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Replace any URLs with a cleaner representation
        cleaned_text = re.sub(r'https?://\S+', '[link]', cleaned_text)
        
        # Format reference style sentences for better speech flow
        cleaned_text = re.sub(r'\[\d+\]', '', cleaned_text)
        
        # Format the message with the search completion time for display only
        result_message = f"Web search completed in {elapsed:.2f} seconds.\n\nHere's what I found from {source}:\n\n{cleaned_text}"
        
        return result_message
    
    # Return the first available result based on priority
    if results["wikipedia"] and len(results["wikipedia"]) > 50:
        return format_result(results['wikipedia'], "Wikipedia")
    
    if results["duckduckgo"] and len(results["duckduckgo"]) > 20:
        return format_result(results['duckduckgo'], "online")
    
    if results["bing"] and len(results["bing"]) > 20:
        return format_result(results['bing'], "Bing")
    
    # If all engines return something but shorter than our thresholds, use the longest
    all_results = [r for r in [results["wikipedia"], results["duckduckgo"], results["bing"]] if r]
    if all_results:
        best_result = max(all_results, key=len)
        source = "online"
        if best_result == results["wikipedia"]:
            source = "Wikipedia"
        elif best_result == results["bing"]:
            source = "Bing"
            
        return format_result(best_result, source)
    
    # If all else fails
    return "I'm sorry, I couldn't find reliable information for that query. Please try rewording your question or being more specific."

def search_wikipedia(query):
    """
    Search Wikipedia for information on the given query.
    
    Args:
        query (str): The search query
        
    Returns:
        str: The Wikipedia summary or an error message
    """
    try:
        # Configure Wikipedia
        wikipedia.set_lang("en")
        
        # Try to search for the query
        search_results = wikipedia.search(query)
        
        if not search_results:
            return f"No Wikipedia results found for '{query}'."
        
        # Get the page for the top result
        page_title = search_results[0]
        page = wikipedia.page(page_title, auto_suggest=False)
        
        # Get the summary and clean it for better speech output
        summary = page.summary
        
        # Clean up formatting for better speech synthesis
        # Remove parenthetical references like [1], [2], etc.
        summary = re.sub(r'\[\d+\]', '', summary)
        
        # Remove text in parentheses if it contains years or technical details
        summary = re.sub(r'\([^)]*\d+[^)]*\)', '', summary)
        
        # Replace complicated punctuation with simpler versions for better speech flow
        summary = summary.replace(';', '.').replace(':', '.')
        
        # Remove extra whitespace
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        # Format sentences for better speech
        sentences = summary.split('. ')
        if len(sentences) > 5:
            # Keep only the first 5 sentences for conciseness
            summary = '. '.join(sentences[:5]) + '.'
        
        # Add attribution
        result = f"{summary}\n\nSource: Wikipedia article on '{page_title}'."
        return result
        
    except wikipedia.exceptions.DisambiguationError as e:
        # If there are multiple matches, suggest the first few options
        options = e.options[:3]
        return f"There are multiple matches for '{query}' on Wikipedia. Did you mean: {', '.join(options)}?"
    
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{query}'."
    
    except Exception as e:
        log_to_file(f"Wikipedia search error: {e}")
        return None

def search_duckduckgo(query):
    """
    Search DuckDuckGo for information on the given query.
    
    Args:
        query (str): The search query
        
    Returns:
        str: The search results or an error message
    """
    try:
        # Encode the query for URL
        encoded_query = quote_plus(query)
        
        # Build the URL
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        # Set a User-Agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract results
        results = soup.find_all('div', class_='result__body')
        
        if not results:
            return f"No DuckDuckGo results found for '{query}'."
        
        # Process the top 3 results
        processed_results = []
        
        for result in results[:3]:
            # Extract the title
            title_element = result.find('a', class_='result__a')
            if not title_element:
                continue
                
            title = title_element.get_text().strip()
            
            # Extract the snippet
            snippet_element = result.find('a', class_='result__snippet')
            if not snippet_element:
                continue
                
            snippet = snippet_element.get_text().strip()
            
            # Clean the snippet for better speech
            # Remove extra whitespace
            snippet = re.sub(r'\s+', ' ', snippet)
            
            # Remove ellipses often found in search results
            snippet = snippet.replace('...', '').replace('…', '')
            
            # Format for readability
            processed_result = f"{title}: {snippet}"
            processed_results.append(processed_result)
        
        if not processed_results:
            return f"No meaningful results found on DuckDuckGo for '{query}'."
        
        # Join the results with proper separation
        final_result = "\n\n".join(processed_results)
        
        return final_result
        
    except requests.exceptions.RequestException as e:
        log_to_file(f"DuckDuckGo search error: {e}")
        return None
    
    except Exception as e:
        log_to_file(f"DuckDuckGo search error: {e}")
        return None

def search_bing(query):
    """
    Search Bing for information on the given query.
    
    Args:
        query (str): The search query
        
    Returns:
        str: The search results or an error message
    """
    try:
        # Encode the query for URL
        encoded_query = quote_plus(query)
        
        # Build the URL
        url = f"https://www.bing.com/search?q={encoded_query}"
        
        # Set a User-Agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract main search results
        results = soup.find_all('li', class_='b_algo')
        
        if not results:
            return f"No Bing results found for '{query}'."
        
        # Process the top results
        processed_results = []
        
        for result in results[:3]:
            # Extract the title
            title_element = result.find('h2')
            if not title_element:
                continue
                
            title = title_element.get_text().strip()
            
            # Extract the snippet
            snippet_element = result.find('div', class_='b_caption')
            if not snippet_element:
                continue
                
            p_element = snippet_element.find('p')
            if not p_element:
                continue
                
            snippet = p_element.get_text().strip()
            
            # Clean the snippet for better speech
            # Remove extra whitespace
            snippet = re.sub(r'\s+', ' ', snippet)
            
            # Remove ellipses often found in search results
            snippet = snippet.replace('...', '').replace('…', '')
            
            # Format for readability and speech
            processed_result = f"{title}: {snippet}"
            processed_results.append(processed_result)
        
        # Special handling for featured snippets
        special_snippet = soup.find('div', class_='b_expansion_text')
        if special_snippet:
            special_text = special_snippet.get_text().strip()
            if special_text:
                processed_results.insert(0, f"Featured answer: {special_text}")
        
        if not processed_results:
            return f"No meaningful results found on Bing for '{query}'."
        
        # Join the results with proper separation
        final_result = "\n\n".join(processed_results)
        
        return final_result
        
    except requests.exceptions.RequestException as e:
        log_to_file(f"Bing search error: {e}")
        return None
    
    except Exception as e:
        log_to_file(f"Bing search error: {e}")
        return None

def is_general_knowledge_question(text):
    """
    Determine if the text is asking a general knowledge question
    
    Args:
        text (str): The text to check
        
    Returns:
        bool: True if the text is a general knowledge question, False otherwise
    """
    # Common question starters
    question_starters = [
        "who is", "what is", "where is", "when is", "why is", "how is",
        "who was", "what was", "where was", "when was", "why was", "how was",
        "who were", "what were", "where were", "when were", "why were", "how were",
        "define", "explain", "tell me about", "information on", "info on",
        "can you tell me", "do you know", "i want to know"
    ]
    
    # Check if the text starts with a question starter
    text_lower = text.lower()
    for starter in question_starters:
        if text_lower.startswith(starter) or f" {starter} " in f" {text_lower} ":
            return True
    
    # Check if the text contains a question mark
    if "?" in text:
        return True
    
    return False

def write_email(topic):
    """
    Generate an email draft based on the given topic
    
    Args:
        topic (str): The topic or purpose of the email
        
    Returns:
        str: A complete email draft with subject and body
    """
    # Lowercase topic for easier pattern matching
    topic_lower = topic.lower()
    
    # Initialize variables for email parts
    greeting = ""
    subject = ""
    introduction = ""
    body = ""
    closing = ""
    signature = "Regards,\n[Your Name]"
    
    # Determine email tone and style based on the topic
    if any(word in topic_lower for word in ["job", "application", "resume", "interview", "position", "employment", "career", "vacancy"]):
        # Professional job application email
        email_type = "job_application"
        subject = "Application for [Position] - [Your Name]"
        greeting = "Dear Hiring Manager,"
        introduction = "I am writing to express my interest in the [Position] role advertised on your website. With my background in [relevant field] and experience in [relevant skills], I believe I would be a strong candidate for this position."
        body = "Throughout my career, I have developed expertise in [skill 1], [skill 2], and [skill 3]. In my previous role at [Company], I successfully [achievement 1] and [achievement 2], which resulted in [positive outcome].\n\nI am particularly drawn to [Company Name] because of its [something specific about the company]. I am impressed by the company's [mention something about their products/services/culture], and I am excited about the possibility of contributing to your team.\n\nAttached is my resume that details my experience and qualifications. I would welcome the opportunity to discuss how my skills align with your needs in an interview."
        closing = "Thank you for considering my application. I look forward to the possibility of working with your team."
    
    elif any(word in topic_lower for word in ["inquiry", "question", "information", "details", "query"]):
        # General inquiry email
        email_type = "inquiry"
        subject = "Inquiry: [Specific Topic]"
        greeting = "Hello,"
        introduction = "I am writing to inquire about [specific subject of inquiry]. I would appreciate if you could provide me with some information regarding this matter."
        body = "Specifically, I would like to know the following:\n\n1. [Question 1]\n2. [Question 2]\n3. [Question 3]\n\nThe reason for my inquiry is [explain why you need this information]. Any information you can provide would be greatly appreciated."
        closing = "Thank you for your time and assistance. I look forward to your response."
    
    elif any(word in topic_lower for word in ["thank", "appreciation", "grateful", "gratitude"]):
        # Thank you email
        email_type = "thank_you"
        subject = "Thank You for [Reason]"
        greeting = "Dear [Recipient],"
        introduction = "I wanted to express my sincere gratitude for [what you're thanking them for]."
        body = "Your [help/support/generosity/kindness] has made a significant difference in [how it affected you or the situation]. I truly appreciate the time and effort you dedicated to [specific action they took].\n\n[Add a specific example or detail about how their actions helped you]."
        closing = "Thank you once again for your [support/help/kindness]. It means a great deal to me."
    
    elif any(word in topic_lower for word in ["complaint", "dissatisfied", "disappointed", "issue", "problem", "concern"]):
        # Complaint email
        email_type = "complaint"
        subject = "Complaint Regarding [Issue/Product/Service]"
        greeting = "Dear Customer Service Team,"
        introduction = "I am writing to express my dissatisfaction with [product/service] that I [purchased/used] on [date]."
        body = "The specific issues I encountered include:\n\n1. [Issue 1]\n2. [Issue 2]\n3. [Issue 3]\n\nI have already attempted to resolve this matter by [mention previous attempts at resolution]. Unfortunately, these attempts have not resulted in a satisfactory solution.\n\nAs a loyal customer of [Company Name], I expected a higher quality of [product/service]. I would appreciate if you could [specify the desired resolution, such as replacement, refund, etc.]."
        closing = "I look forward to your prompt attention to this matter and a satisfactory resolution."
    
    elif any(word in topic_lower for word in ["invite", "invitation", "event", "meeting", "celebration", "party"]):
        # Invitation email
        email_type = "invitation"
        subject = "Invitation: [Event Name] - [Date]"
        greeting = "Dear [Recipient],"
        introduction = "I would like to cordially invite you to [event name] on [date] at [time] at [location]."
        body = "The occasion is [purpose of event], and your presence would make it even more special. The event will include [describe what will happen at the event, such as dinner, activities, etc.].\n\n[Additional details about the event, such as dress code, what to bring, etc.]\n\nPlease RSVP by [deadline] by [how to RSVP]."
        closing = "I hope you can join us for this special occasion. Looking forward to seeing you there!"
    
    elif any(word in topic_lower for word in ["apology", "sorry", "regret", "apologize"]):
        # Apology email
        email_type = "apology"
        subject = "Apology for [Incident/Situation]"
        greeting = "Dear [Recipient],"
        introduction = "I am writing to sincerely apologize for [describe the incident or situation that requires an apology]."
        body = "I understand that my [actions/behavior/mistake] has caused [describe the impact it had on the recipient]. I take full responsibility for this error and deeply regret any inconvenience or distress it may have caused you.\n\nThe situation occurred because [brief explanation, not an excuse], but I understand this does not justify the outcome. To address this, I am taking steps to [describe how you're fixing the situation or preventing it from happening again]."
        closing = "I value our [relationship/partnership] and hope that you can accept my sincere apology. I am committed to ensuring this does not happen again."
    
    elif any(word in topic_lower for word in ["request", "favor", "assistance", "help"]):
        # Request email
        email_type = "request"
        subject = "Request for [What You're Requesting]"
        greeting = "Dear [Recipient],"
        introduction = "I hope this email finds you well. I am writing to request your assistance with [briefly describe what you need]."
        body = "Specifically, I am hoping that you could [provide detailed information about your request]. This would greatly help me with [explain why you need this].\n\n[Provide any relevant background information or context for your request].\n\nI understand that you are busy, and I appreciate any time you can spare for this matter. If there's any additional information you need from me to fulfill this request, please let me know."
        closing = "Thank you for considering my request. I look forward to your response."
    
    else:
        # General/professional email for any other topic
        email_type = "general"
        subject = f"Regarding: {topic.capitalize()}"
        greeting = "Hello,"
        introduction = f"I am writing to you regarding {topic}."
        body = f"I wanted to discuss the matter of {topic} with you. This is an important topic that requires attention because [reason why the topic is important].\n\n[Main point 1 about the topic]\n\n[Main point 2 about the topic]\n\n[Main point 3 about the topic]\n\nBased on the above points, I believe that [conclusion or suggestion related to the topic]."
        closing = "I hope this information is helpful. Please let me know if you have any questions or if there's anything else I can assist you with."
    
    # Compile the email
    complete_email = f"Subject: {subject}\n\n{greeting}\n\n{introduction}\n\n{body}\n\n{closing}\n\n{signature}"
    
    # Add a note for the user
    note_to_user = f"\nNOTE: This is a generated email draft about '{topic}'. Please review and personalize it before sending."
    
    return complete_email + note_to_user

def process_command(command):
    """
    Process the user's command and return a response
    
    Args:
        command (str): The user's command in lowercase
        
    Returns:
        str: The assistant's response
    """
    # Empty command
    if not command:
        return "I didn't catch that. Could you please repeat?"
    
    # Test time command
    if command.startswith("test time "):
        try:
            # Extract hour from command
            parts = command.split()
            if len(parts) >= 3:
                hour = int(parts[2])
                if 0 <= hour <= 23:
                    set_test_hour(hour)
                    time_greeting = get_time_greeting()
                    return f"Test mode: Time set to {hour}:00. {time_greeting}"
                else:
                    return "Please specify a valid hour between 0 and 23."
            else:
                return "Please specify a valid hour, e.g., 'test time 9' for 9 AM."
        except ValueError:
            return "Please specify a valid hour, e.g., 'test time 9' for 9 AM."
    
    # Stock analysis commands
    if command.startswith("analyze stock ") or command.startswith("check stock ") or command.startswith("stock info ") or "stock information" in command:
        if command.startswith("analyze stock "):
            query = command[14:].strip()
        elif command.startswith("check stock "):
            query = command[12:].strip()
        elif command.startswith("stock info "):
            query = command[11:].strip()
        elif "stock information" in command:
            # Extract stock name after "stock information"
            match = re.search(r"stock information (?:for|about|on)?\s+(.*?)(?:\s+on nse|\s+on bse|$)", command, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
            else:
                # Try a more general pattern
                match = re.search(r"stock information\s+(.*?)$", command, re.IGNORECASE)
                if match:
                    query = match.group(1).strip()
                else:
                    query = ""
        else:
            query = ""
            
        if query:
            log_to_file(f"Analyzing stock for '{query}'...")
            # Determine exchange (default to auto-detection)
            exchange = "NSE"  # Default for backward compatibility
            
            # Check if exchange is explicitly specified
            if " on bse" in query.lower():
                exchange = "BSE"
                query = query.lower().replace(" on bse", "").strip()
            elif " on nse" in query.lower():
                exchange = "NSE"
                query = query.lower().replace(" on nse", "").strip()
            
            # The get_stock_info method will auto-detect the exchange
            analysis = stock_analyzer.get_stock_info(query, exchange)
            
            # Include the detected exchange in the log
            if "stock_info" in analysis and "exchange" in analysis["stock_info"]:
                detected_exchange = analysis["stock_info"]["exchange"]
                log_to_file(f"Stock detected on {detected_exchange} exchange")
            
            return format_stock_analysis_response(analysis)
        else:
            return "Please specify a stock name or symbol to analyze."
    
    # Mutual fund analysis commands
    if command.startswith("analyze fund ") or command.startswith("check fund ") or command.startswith("fund info ") or command.startswith("mutual fund "):
        if command.startswith("analyze fund "):
            query = command[13:].strip()
        elif command.startswith("check fund "):
            query = command[11:].strip()
        elif command.startswith("fund info "):
            query = command[10:].strip()
        else:  # mutual fund
            query = command[12:].strip()
            
        if query:
            log_to_file(f"Analyzing mutual fund for '{query}'...")
            # Get mutual fund analysis
            analysis = mutual_fund_analyzer.get_fund_info(query)
            return format_mutual_fund_analysis_response(analysis)
        else:
            return "Please specify a mutual fund name to analyze."
    
    # Generic stock market advice for "should I buy shares" without specifying which ones
    if re.search(r"should i buy (shares|stocks)$", command.lower()) or command.lower() == "should i buy shares" or command.lower() == "should i buy stocks":
        # Provide general investment advice along with stock suggestions
        popular_stocks = ["HDFC Bank", "Reliance Industries", "TCS", "Infosys", "Tata Motors", "SBI", "ICICI Bank", "Adani Enterprises", "Axis Bank", "Wipro"]
        suggested_stocks = random.sample(popular_stocks, 5)
        
        return (f"When it comes to buying shares, it's important to research individual stocks rather than making general decisions. "
                f"The stock market offers opportunities, but each stock has different prospects.\n\n"
                f"Here are 5 popular stocks you might want to analyze:\n"
                f"• {suggested_stocks[0]}\n"
                f"• {suggested_stocks[1]}\n"
                f"• {suggested_stocks[2]}\n"
                f"• {suggested_stocks[3]}\n"
                f"• {suggested_stocks[4]}\n\n"
                f"To get my analysis on any of these, simply ask: 'Should I buy {random.choice(suggested_stocks)}?'")
    
    # Simplified English stock query handler
    if "should i buy" in command.lower():
        # Try multiple patterns to extract the stock name
        patterns = [
            r"should i buy ([\w\s&]+?)(?:\s+share|\s+shares|\s+stock|\s+stocks)?(?:\s+|$|\?)",  # With or without "share/shares/stock/stocks"
            r"should i buy ([\w\s&]+?)(?:\s+|$|\?)"  # Most general pattern - everything after "should i buy"
        ]
        
        found_match = False
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                stock_name = match.group(1).strip()
                if stock_name and len(stock_name) > 1:  # Ensure we have a meaningful stock name
                    found_match = True
                    # Map common stock references to proper stock names
                    stock_mapping = {
                        "hdfc": "HDFC Bank",
                        "hdfc bank": "HDFC Bank",
                        "tata": "Tata Motors",
                        "wipro": "Wipro",
                        "infosys": "Infosys",
                        "reliance": "Reliance Industries",
                        "sbi": "State Bank of India",
                        "icici": "ICICI Bank",
                        "bajaj": "Bajaj Finance",
                        "airtel": "Bharti Airtel",
                        "itc": "ITC Limited",
                        "tcs": "Tata Consultancy Services",
                        "hul": "Hindustan Unilever",
                        "l&t": "Larsen & Toubro",
                        "ongc": "Oil and Natural Gas Corporation",
                        "sun pharma": "Sun Pharmaceutical",
                        "axis bank": "Axis Bank",
                        "kotak": "Kotak Mahindra Bank",
                        "mahindra": "Mahindra & Mahindra",
                        "adani": "Adani Enterprises",
                        "maruti": "Maruti Suzuki",
                        "titan": "Titan Company",
                        "nestle": "Nestle India",
                        "hindalco": "Hindalco Industries",
                        "jsw": "JSW Steel"
                    }
                    
                    # Get the standardized stock name if available
                    stock_query = stock_mapping.get(stock_name.lower(), stock_name)
                    
                    log_to_file(f"Processing buy recommendation for {stock_query}...")
                    exchange = "NSE"  # Default, but will auto-detect
                    
                    if "on bse" in command.lower() or "bse" in command.lower():
                        exchange = "BSE"
                    elif "on nse" in command.lower() or "nse" in command.lower():
                        exchange = "NSE"
                        
                    analysis = stock_analyzer.get_stock_info(stock_query, exchange)
                    return format_stock_analysis_response(analysis)
        
        # If no stock name was found in the command, recommend popular stocks
        if not found_match:
            popular_stocks = ["HDFC Bank", "Reliance Industries", "TCS", "Infosys", "Tata Motors"]
            return (f"I need to know which stock you're interested in buying. "
                   f"Please ask me about specific stocks like: 'Should I buy {random.choice(popular_stocks)}?'\n\n"
                   f"Some popular stocks you might want to consider analyzing: {', '.join(popular_stocks)}")
    
    # Should I buy/sell stock command
    if "should i buy" in command or "should i sell" in command or "should i invest in" in command:
        # Extract the stock/fund name after the phrases - more permissive pattern for English
        stock_pattern = r"(should i buy|should i sell|should i invest in)\s+(.*?)(\s+stock|\s+shares|\s+fund|\s+mutual fund|\s+on nse|\s+on bse|$)"
        match = re.search(stock_pattern, command, re.IGNORECASE)
        
        if match:
            action = match.group(1).lower()
            query = match.group(2).strip()
            context = match.group(3).strip() if match.group(3) else ""
            
            log_to_file(f"Investment advice requested for '{query}'...")
            
            # Determine if it's a stock or mutual fund
            if "fund" in context.lower() or "mutual fund" in command or "sip" in command.lower():
                # Mutual fund analysis
                analysis = mutual_fund_analyzer.get_fund_info(query)
                return format_mutual_fund_analysis_response(analysis)
            else:
                # Stock analysis - determine exchange
                exchange = "NSE"  # Default, but will auto-detect
                
                if "on bse" in command.lower() or "bse" in command.lower():
                    exchange = "BSE"
                elif "on nse" in command.lower() or "nse" in command.lower():
                    exchange = "NSE"
                
                # Map common stock references to proper stock names
                stock_mapping = {
                    "hdfc": "HDFC Bank",
                    "hdfc bank": "HDFC Bank",
                    "tata": "Tata Motors",
                    "wipro": "Wipro",
                    "infosys": "Infosys",
                    "reliance": "Reliance Industries",
                    "sbi": "State Bank of India",
                    "icici": "ICICI Bank",
                    "bajaj": "Bajaj Finance",
                    "airtel": "Bharti Airtel",
                    "itc": "ITC Limited",
                    "tcs": "Tata Consultancy Services",
                    "hul": "Hindustan Unilever",
                    "l&t": "Larsen & Toubro",
                    "ongc": "Oil and Natural Gas Corporation",
                    "sun pharma": "Sun Pharmaceutical",
                    "axis bank": "Axis Bank",
                    "kotak": "Kotak Mahindra Bank",
                    "mahindra": "Mahindra & Mahindra",
                    "adani": "Adani Enterprises",
                    "maruti": "Maruti Suzuki",
                    "titan": "Titan Company",
                    "nestle": "Nestle India",
                    "hindalco": "Hindalco Industries",
                    "jsw": "JSW Steel"
                }
                
                # Get the standardized stock name if available
                stock_query = stock_mapping.get(query.lower(), query)
                
                analysis = stock_analyzer.get_stock_info(stock_query, exchange)
                return format_stock_analysis_response(analysis)
        else:
            # If we reached here without finding anything, recommend popular stocks
            popular_stocks = ["HDFC Bank", "Reliance Industries", "TCS", "Infosys", "Tata Motors", "SBI", "ICICI Bank", "Adani Enterprises", "Axis Bank", "Wipro"]
            return (f"To analyze a stock, I need the name or symbol. "
                    f"Please ask me about specific stocks like: 'Should I buy {random.choice(popular_stocks)}?'\n\n"
                    f"Popular stocks you might want to consider: {', '.join(random.sample(popular_stocks, 5))}")
    
    # SIP recommendation for mutual funds
    if "sip" in command and ("recommend" in command or "should i start" in command or "advice" in command):
        # Extract the fund name
        fund_pattern = r"(sip|systematic investment plan)(?:.*?)(for|in|on)\s+([a-zA-Z0-9\s]+?)(\s+fund|\s+mutual fund|$)"
        match = re.search(fund_pattern, command, re.IGNORECASE)
        
        if match:
            query = match.group(3).strip()
            
            log_to_file(f"SIP advice requested for '{query}'...")
            
            # Get mutual fund analysis with focus on SIP recommendation
            analysis = mutual_fund_analyzer.get_fund_info(query)
            return format_mutual_fund_analysis_response(analysis)
        else:
            return "Please specify a mutual fund name for SIP recommendation."
    
    # Email writing command
    if command.startswith("write email ") or command.startswith("draft email ") or command.startswith("compose email "):
        if command.startswith("write email "):
            topic = command[12:].strip()
        elif command.startswith("draft email "):
            topic = command[12:].strip()
        else:  # compose email
            topic = command[14:].strip()
            
        if topic:
            return write_email(topic)
        else:
            return "Please specify a topic for the email. For example, 'write email job application'"
    
    # Reset test time command
    if command == "reset time":
        set_test_hour(None)
        return "Reset to current system time."
    
    # Greetings
    if any(word in command for word in ["hello", "hi", "hey"]):
        time_greeting = get_time_greeting()
        return f"{time_greeting} How can I assist you today?"
    
    # Farewell
    if any(word in command for word in ["bye", "goodbye", "exit", "quit"]):
        return "Goodbye! Have a great day!"
    
    # Status inquiry
    if "how are you" in command:
        return "I'm functioning perfectly! Thanks for asking."
    
    # Time inquiry
    if "time" in command and not is_general_knowledge_question(command):
        current_time = datetime.now().strftime("%H:%M:%S")
        return f"The current time is {current_time}"
    
    # Date inquiry
    if "date" in command and not is_general_knowledge_question(command):
        current_date = datetime.now().strftime("%Y-%m-%d")
        return f"Today's date is {current_date}"
    
    # Name inquiry
    if "your name" in command or "who are you" in command:
        return "I am FRIDAY, your personal chat assistant."
    
    # Open application command
    if command.startswith("open "):
        app_name = command[5:].strip()
        if app_name:
            return open_application(app_name)
        else:
            return "Please specify which application you want me to open."
    
    # Close application command
    if command.startswith("close "):
        app_name = command[6:].strip()
        if app_name:
            return close_application(app_name)
        else:
            return "Please specify which application you want me to close."
    
    # Close/Exit application command - alternative phrasing
    if command.startswith("exit ") or command.startswith("quit ") or command.startswith("terminate "):
        if command.startswith("exit "):
            app_name = command[5:].strip()
        elif command.startswith("quit "):
            app_name = command[5:].strip()
        else:  # terminate
            app_name = command[10:].strip()
            
        if app_name:
            return close_application(app_name)
        else:
            return "Please specify which application you want me to close."
    
    # Launch application command - alternative phrasing
    if command.startswith("launch ") or command.startswith("start ") or command.startswith("run "):
        if command.startswith("launch "):
            app_name = command[7:].strip()
        elif command.startswith("start "):
            app_name = command[6:].strip()
        else:  # run
            app_name = command[4:].strip()
            
        if app_name:
            return open_application(app_name)
        else:
            return "Please specify which application you want me to launch."
    
    # Help command
    if "help" in command:
        return ("I can help you with various tasks. Try asking me about:\n"
                "- The time or date\n"
                "- Ask who I am\n"
                "- Say hello or goodbye\n"
                "- Open applications with 'open [app name]'\n"
                "- Close applications with 'close [app name]'\n"
                "- Test time greetings with 'test time [hour]'\n"
                "- Reset to system time with 'reset time'\n"
                "- Ask general knowledge questions like 'Who is SRK?' or 'What is a chemical reaction?'\n"
                "- Open web pages with 'open page [query]' or 'show me [query]'\n"
                "- Write emails with 'write email [topic]' or 'compose email [topic]'\n"
                "- Analyze stocks with 'analyze stock [name/symbol]' or 'stock info [name/symbol]', which now includes recommendations for similar stocks to invest in from both NSE and BSE\n"
                "- Specify stock exchange with 'analyze stock [name] on NSE' or 'analyze stock [name] on BSE', or let me auto-detect the exchange\n"
                "- Analyze mutual funds with 'analyze fund [name]' or 'mutual fund [name]'\n"
                "- Get investment advice with simple English commands like 'Should I buy [stock name]' or 'Should I buy [stock name] shares'\n"
                "- Get SIP recommendations with 'SIP recommendation for [fund name]'")
    
    # Command to open a web page
    if command.startswith("open page ") or command.startswith("show me "):
        if command.startswith("open page "):
            query = command[10:].strip()
        else:  # show me
            query = command[8:].strip()
            
        if query:
            return open_web_page(query)
        else:
            return "Please specify what you'd like me to search for."
    
    # Explicit search command
    if command.startswith("search "):
        query = command[7:].strip()
        if query:
            log_to_file(f"Searching for information about '{query}'...")
            return search_web(query)
        else:
            return "Please specify what you'd like me to search for."
            
    # General knowledge question check
    if is_general_knowledge_question(command):
        # Check if the query contains keywords indicating the user wants to open a page
        if any(word in command for word in ["show", "open", "browser", "website", "page"]):
            # Extract the actual query by removing the opening keywords
            query = re.sub(r'^(can you )?(show|open|display|find)( me)?( a)?( the)?( page)?( about)?( on)?', '', command)
            query = query.strip()
            if query:
                return open_web_page(query)
        
        # Otherwise, just search as usual
        log_to_file(f"Looking up information about '{command}'...")
        return search_web(command)
    
    # Default response for unrecognized commands
    return "I'm still learning to understand different queries. Could you try asking something else?"
