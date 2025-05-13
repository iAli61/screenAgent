# ScreenAgent

A flexible screen monitoring tool that captures and tracks changes in user-defined regions of interest (ROI) on your screen.

## Features

- **Region of Interest Monitoring**: Define specific areas of your screen to monitor for changes
- **Change Detection**: Automatically captures new screenshots when significant changes are detected
- **Cross-Platform Compatibility**: Works on Linux, Windows, and WSL environments
- **Web Interface**: Access and control the tool via a browser-based interface
- **Keyboard Shortcuts**: Take manual screenshots with a keyboard shortcut (F12 by default)
- **Configurable Settings**: Adjust sensitivity, monitoring intervals, and other parameters
- **Screenshot History**: View and access previously captured screenshots

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```
   git clone [your-repo-url]
   cd screenAgent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Additional dependencies based on your environment:
   - For WSL: No additional setup needed, uses PowerShell
   - For Linux with root: `pip install mss`
   - For standard environments: `pip install pyautogui` (recommended)
   - Alternative: `pip install pillow-xcb` (for PIL/Pillow with XCB)

## Usage

### Starting the Server

Run the screenshot server:

```
python screenshot_server.py
```

The server will start on port 8000 by default (or another available port if 8000 is in use).

### Using the Web Interface

1. Open a browser and navigate to `http://localhost:8000`
2. Use the "Select New ROI" button to choose a region of interest
3. Monitor the selected region with automatic change detection
4. Use "Take Screenshot Now" for manual captures

### Keyboard Shortcuts

- Press `F12` to take a manual screenshot (requires root permissions on Linux)
- Keyboard shortcuts are not available in WSL mode

## Configuration

Edit `screen_agent_config.json` or use the web interface to configure:

- ROI coordinates (left, top, right, bottom)
- Change detection threshold
- Screenshot check interval
- Server port settings

## Project Structure

- `screenshot_server.py`: Main server script
- `screenshot.py`: Screenshot capture functionality
- `config.py`: Configuration management
- `keyboard_handler.py`: Keyboard shortcut handling
- `platform_detection.py`: Platform-specific adjustments
- `server_handler.py`: HTTP request handling
- `screenshot_script.ps1`: PowerShell script for WSL screenshots

## How It Works

ScreenAgent works by:

1. Capturing a specified region of your screen
2. Comparing new screenshots with previous ones to detect changes
3. Storing screenshots when changes exceed the threshold
4. Providing access to the screenshot history through a web interface

The tool automatically selects the best screenshot method based on your environment:
- PowerShell commands for WSL
- MSS library for root access on Linux
- PyAutoGUI for most standard environments
- PIL/Pillow ImageGrab as a fallback

## Troubleshooting

- **No screenshots captured**: Ensure proper permissions (may need to run with sudo on Linux)
- **Black screenshots in WSL**: Check WSL integration and PowerShell execution policy
- **Web interface not accessible**: Verify the port is not blocked by firewall
- **Keyboard shortcuts not working**: Run with root/admin privileges

## License

[Your License]

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.