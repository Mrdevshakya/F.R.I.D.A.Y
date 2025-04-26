# FRIDAY - Your Personal AI Assistant

FRIDAY (Female Replacement Intelligent Digital Assistant Youth) is a powerful personal AI assistant designed to help you with daily tasks and provide information instantly. This assistant features both console and graphical user interfaces with voice output.

## Project Structure

```
FRIDAY/
├── assets/                   # Assets directory for icons and charts
│   └── charts/              # Generated financial analysis charts
│
├── backend/                  # Backend components
│   ├── brain/                # Core processing modules
│   │   ├── error_manager.py  # Error handling system
│   │   ├── text.py           # Text-to-speech system
│   │   ├── brain.py          # Main processing engine
│   │   ├── nav_predictor/    # Financial analysis module
│   │   │   ├── model.py      # Stock and mutual fund analyzers
│   │   │   ├── preprocess.py # Data preprocessing utilities
│   │   │   ├── utils.py      # Data fetching utilities
│   │   │   └── __init__.py   # Package initialization
│   │   └── __init__.py       # Brain package initialization
│   ├── main.py               # Console interface
│   └── chat_ui.py            # Graphical UI interface
│
├── frontend/                 # Web interface
│   ├── index.html            # HTML structure
│   ├── styles.css            # CSS styling
│   └── script.js             # JavaScript functionality
│
├── server/                   # Web server components
│   ├── server.py             # Main server (uses FRIDAY brain)
│   └── test_server.py        # Test server (simulated responses)
│
├── scripts/                  # Utility scripts
│   ├── FRIDAY.bat            # Main FRIDAY launcher
│   ├── start_web_server.bat  # Web server launcher
│   └── test_server.bat       # Test server launcher
│
├── logs/                     # Log files directory
│   ├── friday_error.log      # Error logs
│   ├── friday_search.log     # Search history logs
│   └── server.log            # Server logs
│
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## ✨ Features

### 🗣️ Interactive Communication
- **Dual Interface**: Choose between console and graphical user interfaces
- **Dark/Light Mode**: Toggle between themes in the GUI version
- **Voice Responses**: Natural voice responses with multiple fallback methods
- **Text Chat**: Type commands and receive detailed responses
- **Web Interface**: Modern web interface with sleek design

### 🔍 Information Retrieval
- **Multi-Source Web Search**: Get reliable information from Wikipedia, DuckDuckGo, and Bing
- **Knowledge Base**: Quick answers to common questions
- **Time and Date**: Current time and date information
- **Web Browser Integration**: Open web pages directly for deeper research

### 💻 System Control
- **Application Management**: Open and close applications like Chrome, Word, Excel and more
- **System Navigation**: Access utilities and tools through simple commands
- **Time-Based Awareness**: Context-aware greetings based on time of day

### 📝 Content Creation
- **Email Templates**: Generate professional email templates for various purposes
- **Formatted Text**: Well-formatted responses for easy reading

### 📊 Financial Analysis
- **Stock Analysis**: Analyze stock performance and get buy/sell recommendations
- **Mutual Fund Analysis**: Analyze mutual fund performance and get SIP recommendations
- **Visual Reports**: Charts and graphs for better financial data understanding

## 🔄 Recent Improvements

### Reliability Enhancements
- **Chart Loading Improvements**: Added 30-second timeout with retry functionality
- **Cross-Browser Compatibility**: Fixed issues for Safari and iOS devices
- **Improved Error Recovery**: Better handling of connection and data retrieval issues
- **Enhanced UI Responsiveness**: Optimized for various screen sizes, including very small devices

### Technical Improvements
- **Server-Side Path Handling**: Better chart file handling and permissions management
- **Optimized Asset Loading**: Improved chart generation and display
- **Logging Enhancements**: More detailed error tracking and reporting
- **Document Ready Checks**: Separate critical initialization from background elements
- **CSS Layout Refinements**: Better positioning for small screens and accessibility improvements

## 🚀 Getting Started

### System Requirements
- Python 3.8 or higher
- Windows OS (primary platform)
- 50MB free disk space
- Internet connection for web searches

### Installation Options

#### Option 1: Quick Start (Windows)
For Windows users, batch files are included for easy setup:
```
scripts/FRIDAY.bat [options]
  --no-voice   Disable voice responses
  --gui        Launch with graphical interface
  --clean      Clean log files before starting
  --debug      Enable debug mode with verbose logging
```

#### Option 2: Web Interface
To use the web interface:
```
scripts/start_web_server.bat     # Connects to the full FRIDAY backend
scripts/test_server.bat          # For testing without the backend
```
Then open your browser to: http://localhost:5000

#### Option 3: Manual Installation
1. Clone or download this repository
2. Navigate to the project directory in your terminal
3. Install dependencies: `pip install -r requirements.txt`
4. Run FRIDAY in console mode: `python backend/main.py [options]`
5. Or with graphical interface: `python backend/chat_ui.py`

Console mode options:
```
python backend/main.py [options]
  --no-voice   Disable voice responses
  --debug      Enable debug mode with verbose logging
  --version    Show version information
  --clean      Clean log files before starting
```

## 💬 Using FRIDAY

### Basic Commands
| Command Type | Examples | What It Does |
|--------------|----------|--------------|
| **Greetings** | `hello`, `hi`, `hey` | Get a personalized greeting |
| **Time & Date** | `what time is it`, `today's date` | Current time and date information |
| **Assistant Info** | `who are you`, `what can you do` | Learn about FRIDAY's capabilities |
| **Exit** | `exit`, `quit`, `bye` | End your session |

### Web Search Commands
| Command Type | Examples | What It Does |
|--------------|----------|--------------|
| **General Knowledge** | `who is Albert Einstein`, `what is quantum physics` | Get information from reliable sources |
| **Explicit Search** | `search Python programming`, `look up climate change` | Perform a targeted web search |
| **Web Navigation** | `open page about Mars`, `show me Delhi` | Open web pages in your browser |

### Application Control
| Command Type | Examples | What It Does |
|--------------|----------|--------------|
| **Launch Apps** | `open chrome`, `launch word`, `start calculator` | Open various applications |
| **Close Apps** | `close chrome`, `exit notepad`, `terminate calculator` | Close running applications |

### Email Assistant
| Command Type | Examples | What It Does |
|--------------|----------|--------------|
| **Draft Emails** | `write email job application`, `compose thank you email` | Generate professional email templates |
| **Email Types** | Job applications, thank you notes, complaints, inquiries, invitations, apologies | Multiple email formats available |

### Financial Analysis
| Command Type | Examples | What It Does |
|--------------|----------|--------------|
| **Stock Analysis** | `analyze stock AAPL`, `check TSLA stock` | Get stock price trend analysis and recommendations |
| **Mutual Fund Analysis** | `analyze mutual fund XYZ`, `check MF performance` | Get mutual fund performance analysis and SIP recommendations |

### Theme Control (GUI Version)
| Command | What It Does |
|---------|--------------|
| View → Dark Mode | Toggle between dark and light themes |
| File → Clear Chat | Clear the chat history |
| Help → Commands | View a list of available commands |
| Help → About FRIDAY | View information about FRIDAY |

### Time-Based Testing
| Command | What It Does |
|---------|--------------|
| `test time 9` | Test morning greeting (9 AM) |
| `test time 14` | Test afternoon greeting (2 PM) |
| `test time 19` | Test evening greeting (7 PM) |
| `reset time` | Reset to system time |

## 🔧 Technical Architecture

### Core Components
- **brain/brain.py**: Command processing engine, web search capabilities, and application control
- **brain/text.py**: Advanced text-to-speech system with multiple fallback methods
- **brain/error_manager.py**: Centralized error handling and logging system
- **brain/nav_predictor/**: Financial analysis module with stock and mutual fund analyzers
- **main.py**: Console interface application with command-line arguments
- **chat_ui.py**: Modern graphical user interface with theme support
- **server/server.py**: Web server for the browser-based interface

### System Design
- **Multi-source Search**: Information retrieval from Wikipedia, DuckDuckGo, and Bing
- **Speech System**: Layered text-to-speech with pyttsx3, VBScript and PowerShell fallbacks
- **Error Handling**: Comprehensive logging and graceful error recovery
- **Modular Design**: Separated core functionality for easy maintenance and extension
- **Financial Analysis**: Data-driven stock and mutual fund analysis with visualizations

## 🔜 Upcoming Features

### Planned Enhancements
- **Voice Input**: Interact with FRIDAY using natural voice commands
- **Calendar Integration**: Manage appointments and set reminders
- **Task Management**: Create and track to-do lists
- **Weather Information**: Get current and forecasted weather conditions
- **Custom Commands**: Create your own shortcuts and automated routines

### Planned System Controls
- **Display Management**: Control brightness and screen settings
- **Audio Control**: Adjust volume, mute/unmute system
- **Network Management**: Control Wi-Fi and Bluetooth connections
- **Power Options**: Manage sleep, hibernate, and shutdown functions

## 📝 Contributing
Contributions are welcome! If you'd like to improve FRIDAY:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License
This project is available as open source under the terms of the MIT License.

## 📞 Support
For assistance or questions, please open an issue on the GitHub repository. 