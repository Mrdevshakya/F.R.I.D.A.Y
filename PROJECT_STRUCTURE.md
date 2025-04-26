# FRIDAY Project Structure

This document describes the organization of the FRIDAY project files.

## Core Files

- **main.py**: The main console application entry point with command-line arguments
- **chat_ui.py**: Graphical user interface with modern dark/light theme support
- **requirements.txt**: List of Python package dependencies
- **FRIDAY.bat**: Windows batch file for easy setup and execution with command-line options
- **Readme.md**: Project documentation
- **.gitignore**: Specifies intentionally untracked files to ignore

## Brain Module

The "brain" directory contains the core functionality:

- **brain/brain.py**: Command processing, web search, application control
- **brain/text.py**: Text-to-speech and input/output handling
- **brain/error_manager.py**: Centralized error handling and logging
- **brain/nav_predictor/**: Financial analysis module
  - **model.py**: Stock and mutual fund analyzer classes
  - **preprocess.py**: Data preprocessing tools
  - **utils.py**: Data fetching and utility functions
  - **__init__.py**: Package initialization

## Server Components

The "server" directory contains web server functionality:

- **server/server.py**: Main web server using Flask to interface with FRIDAY's brain
- **server/test_server.py**: Test server with simulated responses

## Frontend Components

The "frontend" directory contains web interface files:

- **frontend/index.html**: HTML structure for web interface
- **frontend/styles.css**: CSS styling for web interface
- **frontend/script.js**: JavaScript functionality for web interface

## Scripts

The "scripts" directory contains utility batch files:

- **scripts/FRIDAY.bat**: Main launcher with console/GUI options
- **scripts/start_web_server.bat**: Web server launcher
- **scripts/test_server.bat**: Test server launcher

## Directory Structure

```
FRIDAY/
├── assets/                 # Assets directory for icons and charts
│   └── charts/            # Generated financial analysis charts
├── backend/               # Core functionality
│   ├── __pycache__/        # Python bytecode cache
│   ├── brain/              # Brain modules
│   │   ├── __pycache__/    # Python bytecode cache
│   │   ├── __init__.py     # Package initialization
│   │   ├── brain.py        # Command processing and responses
│   │   ├── error_manager.py # Error handling and logging system
│   │   ├── text.py         # Text-to-speech handling
│   │   └── nav_predictor/  # Financial analysis module
│   │       ├── __pycache__/ # Python bytecode cache
│   │       ├── __init__.py  # Package initialization
│   │       ├── model.py     # Stock and mutual fund analyzers
│   │       ├── preprocess.py # Data preprocessing tools
│   │       └── utils.py     # Data fetching utilities
│   ├── main.py             # Console application with command-line arguments
│   └── chat_ui.py          # Graphical user interface with theme support
├── frontend/              # Web interface files
│   ├── index.html          # HTML structure
│   ├── styles.css          # CSS styling
│   └── script.js           # JavaScript functionality
├── logs/                  # Directory for log files
│   ├── friday_error.log    # Error log file
│   ├── friday_search.log   # Search history log
│   └── server.log          # Web server log
├── server/                # Web server components
│   ├── server.py           # Main web server
│   └── test_server.py      # Test server with simulated responses
├── scripts/               # Utility scripts
│   ├── FRIDAY.bat          # Windows batch file with command-line options
│   ├── start_web_server.bat # Web server launcher
│   └── test_server.bat     # Test server launcher
├── venv/                  # Virtual environment (created by FRIDAY.bat)
├── .gitignore             # Git ignore file for version control
├── KEY_FEATURES.md        # Detailed feature documentation
├── PROJECT_STRUCTURE.md   # This file
├── Readme.md              # Project documentation
└── requirements.txt       # Python dependencies
```

## Command-Line Arguments

### For main.py
```
python main.py [options]
  --no-voice   Disable voice responses
  --debug      Enable debug mode with verbose logging
  --version    Show version information
  --clean      Clean log files before starting
```

### For FRIDAY.bat
```
FRIDAY.bat [options]
  --no-voice   Disable voice responses
  --gui        Launch with graphical interface
  --clean      Clean log files before starting
  --debug      Enable debug mode with verbose logging
```

### For Web Servers
```
scripts/start_web_server.bat  # Start the main web server (uses full FRIDAY brain)
scripts/test_server.bat       # Start the test server (simulated responses)
```

## Files Generated During Runtime

- **logs/friday_error.log**: Log of errors and exceptions
- **logs/friday_search.log**: Log of search queries and results
- **logs/server.log**: Web server activity logs
- **assets/charts/**: Generated chart images for financial analysis
- **logs/friday_speech_log.txt**: Log of speech system activities (in temp directory)

## Development Files (Not Included in Repository)

- **__pycache__/** directories: Python bytecode cache (excluded via .gitignore)
- **.idea/** or **.vscode/**: IDE configuration files (excluded via .gitignore)
- **venv/**: Virtual environment (excluded via .gitignore)

## Version History

- **v1.1.0** (Current): Improved UI with theme support, enhanced error handling, added NAV predictor for financial analysis, web server integration
- **v1.0.0**: Initial release with basic functionality 