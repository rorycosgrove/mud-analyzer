# MUD Analyzer GUI Applications

Two graphical interfaces for the MUD Analyzer client library.

## Overview

### 1. Desktop GUI (Tkinter)
- **File**: `gui.py`
- **Platform**: Cross-platform (Windows, Mac, Linux)
- **Technology**: Tkinter (built-in Python)
- **No additional dependencies** required
- Best for local use, offline functionality

### 2. Web GUI (Flask)
- **File**: `web_gui.py`
- **Platform**: Browser-based
- **Technology**: Flask + HTML/CSS/JavaScript
- **Responsive design** for mobile and desktop
- Best for remote access, sharing with others

---

## Desktop GUI (gui.py)

### Features
✅ Search objects and mobiles
✅ View zone information
✅ Get entity details
✅ Find item assemblies
✅ Results display and export
✅ Settings management
✅ Multi-threaded to prevent UI freezing

### Requirements
- Python 3.7+
- Tkinter (built-in with Python)
- `requests` library

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Start the desktop GUI
python gui.py
```

The GUI window will open with tabs for different features:
1. **Search** - Search for objects/mobiles
2. **Zone Info** - Get zone details
3. **Entity Details** - Get object/mobile details
4. **Assemblies** - Find item assemblies
5. **Results** - View and export results

### Features Explained

#### Search Tab
- Enter search query
- Select entity type (All/Objects/Mobiles)
- Set result limit
- Results appear in Results tab

#### Zone Info Tab
- Enter zone number
- Get all zone information
- View in formatted display

#### Entity Details Tab
- Enter VNUM (virtual number)
- Select entity type (Object/Mobile)
- View complete entity information

#### Assemblies Tab
- Enter object VNUM
- Find all assemblies containing that object
- View assembly details

#### Results Tab
- View query results
- Copy to clipboard
- Clear results
- Export to text file

#### Settings
- File > Settings
- Configure REST API URL
- Change server connection

### Keyboard Shortcuts
- `Enter` - Execute current search/query

---

## Web GUI (web_gui.py)

### Features
✅ Beautiful responsive design
✅ Mobile-friendly interface
✅ Real-time API status
✅ Search with multiple filter options
✅ Tab-based navigation
✅ Instant search results
✅ API connection verification

### Requirements
- Python 3.7+
- Flask
- `requests` library

### Installation

```bash
# Install dependencies
pip install flask requests
```

Or use the project requirements:
```bash
pip install -r requirements.txt
```

### Usage

```bash
# Start the web GUI
python web_gui.py
```

Then open your browser to:
```
http://localhost:5000
```

### Features Explained

#### Status Indicator
- Green dot = Connected to API
- Red dot = API unavailable
- Shows API URL

#### Search
- Enter search term
- Filter by entity type
- Adjust result limit
- Real-time results

#### Zone Info
- Enter zone number
- View all zone details
- Click "Get Zone Info" button

#### Object Details
- Enter object VNUM
- View complete object information
- See all attributes

#### Mobile Details
- Enter mobile VNUM
- View complete mobile information
- See all attributes

#### Assemblies
- Enter object VNUM
- Find related assemblies
- View assembly data

### Keyboard Shortcuts
- `Enter` - Execute current search/query

### API Endpoints (Web GUI)

```
GET  /                           - Main page
POST /api/search                 - Search for objects/mobiles
GET  /api/zone/<zone_num>        - Get zone information
GET  /api/object/<vnum>          - Get object details
GET  /api/mobile/<vnum>          - Get mobile details
POST /api/assemblies             - Find item assemblies
GET  /api/status                 - Check API status
```

---

## Configuration

### Desktop GUI
- Settings available via File > Settings menu
- Configure REST API URL
- Settings persist during session

### Web GUI
- API URL hardcoded in `web_gui.py`
- To change: edit `API_URL = "http://localhost:8000"` in the file

To use custom port:
```python
API_URL = "http://localhost:8001"  # Or your custom port
```

---

## Requirements

### Common Dependencies
```
requests>=2.31.0          # REST API client
```

### Desktop GUI Only
- Tkinter (built-in with Python 3)

### Web GUI Only
```
flask>=2.0.0              # Web framework
```

### Full Installation
```bash
pip install -r requirements.txt
```

---

## Troubleshooting

### Desktop GUI

**"No module named 'requests'"**
```bash
pip install requests
```

**GUI doesn't open**
- Check if Tkinter is installed
- On Linux: `sudo apt-get install python3-tk`
- On Mac: Tkinter should be included with Python

**Cannot connect to API**
- Ensure REST API server is running: `python ../mud_analyzer/launch_servers.py --rest`
- Check API URL in Settings
- Verify port 8000 is accessible

### Web GUI

**"No module named 'flask'"**
```bash
pip install flask
```

**"Address already in use"**
- Another instance is running on port 5000
- Kill the process: `lsof -ti:5000 | xargs kill -9` (Linux/Mac)
- Or use different port in code

**API shows as unavailable**
- Ensure REST API server is running
- Check firewall settings
- Verify API URL is correct in code

---

## Development

### Adding New Features

#### Desktop GUI
1. Add new method to `MUDAnalyzerGUI` class
2. Create UI tab in `_create_main_layout()`
3. Handle user input and display results

#### Web GUI
1. Add new API endpoint in `web_gui.py`
2. Add HTML form in `templates/index.html`
3. Add JavaScript handler function

### Project Structure
```
mud_analyzer_client/
├── gui.py                    # Desktop GUI (Tkinter)
├── web_gui.py                # Web GUI (Flask)
├── templates/
│   └── index.html            # Web GUI HTML
├── rest_client.py            # REST API client
├── mcp_client.py             # MCP client
└── requirements.txt          # Dependencies
```

---

## Comparison

| Feature | Desktop GUI | Web GUI |
|---------|------------|---------|
| Setup | One command | One command |
| Learning Curve | Easy | Easy |
| Dependencies | Tkinter (built-in) | Flask |
| Offline Use | Yes | Yes (needs API server) |
| Mobile Support | No | Yes |
| Remote Access | No | Yes (via network) |
| Performance | Instant | ~100ms per request |
| Customization | Moderate | High |
| Multi-user | No | Yes |

---

## Screenshots

### Desktop GUI
- Tabbed interface with search, zone info, entity details, assemblies
- Results displayed with formatting
- Settings dialog for configuration
- Cross-platform support

### Web GUI
- Modern responsive design
- Side navigation menu
- Real-time status indicator
- Mobile-friendly layout
- Professional styling

---

## Support

For issues:
1. Ensure REST API server is running
2. Check error messages in Results tab
3. Verify dependencies are installed
4. Check server logs for API errors
5. Try the other GUI (web or desktop)

---

## Next Steps

1. **Start API Server**
   ```bash
   cd ../mud_analyzer
   python launch_servers.py --rest
   ```

2. **Start GUI** (choose one)
   ```bash
   # Desktop
   python gui.py
   
   # Web
   python web_gui.py
   # Then open http://localhost:5000
   ```

3. **Use the Interface**
   - Search for items
   - View zone information
   - Get entity details
   - Find assemblies

---

## License

Same as parent MUD Analyzer project
