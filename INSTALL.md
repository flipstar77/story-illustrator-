# Installation Guide - Auto-Typer Pro

Three powerful, expandable solutions to choose from!

---

## 🥇 Option 1: Python GUI (RECOMMENDED)

### Best for:
- ✅ Going AFK for long periods
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Full GUI with tons of features
- ✅ Easy to expand and customize
- ✅ Saves your settings

### Features:
- 🎨 Beautiful GUI interface
- 🔄 Multiple commands with rotation or randomization
- ⏱️ Configurable intervals with optional random delays
- 🎯 Loop modes: infinite, once, or specific count
- ⏲️ Startup delay (gives you time to switch windows)
- 💾 Saves/loads configuration
- 📊 Live status and logging
- ⌨️ F9 hotkey to start/stop
- 🛡️ Failsafe: Move mouse to corner to emergency stop

### Installation:

#### Step 1: Install Python
1. Download Python from https://www.python.org/downloads/
2. During installation, **CHECK** "Add Python to PATH"
3. Complete installation

#### Step 2: Install Dependencies
Open Command Prompt/Terminal in this folder and run:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pyautogui
```

#### Step 3: Run the Script
Double-click `auto_typer.py` or run:
```bash
python auto_typer.py
```

### Usage:
1. **Configure** commands (one per line in the text box)
2. **Set** interval in seconds
3. **Enable** advanced options if needed:
   - Randomize order
   - Random delay
   - Loop mode (infinite/once/count)
   - Startup delay
4. Click **Start** (or press F9)
5. **Switch** to your browser window
6. **Go AFK!** The script will keep typing

### Tips:
- Your settings are automatically saved when you click "Save Config"
- Emergency stop: Move your mouse to the top-left corner (PyAutoGUI failsafe)
- The script works system-wide, not just in browser

---

## 🥈 Option 2: Browser Userscript (VERY EASY)

### Best for:
- ✅ No installation needed
- ✅ Works in ANY browser (Chrome, Firefox, Edge, etc.)
- ✅ Portable - works on any computer with Tampermonkey
- ✅ Stays with you across devices (if you sync Tampermonkey)

### Features:
- 🌐 Works on ANY website
- 🎨 Floating draggable UI panel
- 🔄 Multiple commands with randomization
- ⏱️ Random delay option
- 💾 Saves settings per domain
- ⌨️ Ctrl+Shift+A hotkey to show/hide
- 📊 Live logging
- 🎯 Minimizable and draggable

### Installation:

#### Step 1: Install Tampermonkey Extension
Choose your browser:
- **Chrome/Edge**: https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo
- **Firefox**: https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/
- **Safari**: https://apps.apple.com/app/tampermonkey/id1482490089
- **Opera**: https://addons.opera.com/extensions/details/tampermonkey-beta/

Or use **Violentmonkey** or **Greasemonkey** as alternatives.

#### Step 2: Install the Userscript
1. Click on the Tampermonkey icon in your browser
2. Click **"Create a new script"**
3. Delete all the default code
4. Open `auto-typer.user.js` and copy ALL the code
5. Paste it into Tampermonkey
6. Click **File → Save** (or Ctrl+S)

### Usage:
1. Navigate to any website where you want to auto-type
2. Press **Ctrl+Shift+A** to open the Auto-Typer panel
3. Configure commands and settings
4. Click **Start**
5. Go AFK! The script keeps running

### Tips:
- The panel is draggable - click and drag the header
- Click the minimize button to collapse it
- Settings are saved automatically per website
- Works even if you switch tabs (but stays on the page where it's running)

---

## 🥉 Option 3: AutoHotkey (Windows Only)

### Best for:
- ✅ Lightweight
- ✅ Runs in system tray
- ✅ Very simple

### Limitations:
- ❌ Windows only
- ❌ Less expandable
- ❌ No GUI

See `auto-typer.ahk` - Covered in the original README.md

---

## Comparison Table

| Feature | Python GUI | Userscript | AutoHotkey |
|---------|------------|------------|------------|
| **AFK-Safe** | ✅ Yes | ✅ Yes (same tab) | ✅ Yes |
| **Cross-platform** | ✅ Yes | ✅ Yes | ❌ Windows only |
| **No Installation** | ❌ Needs Python | ✅ Just browser extension | ❌ Needs AHK |
| **GUI** | ✅ Full GUI | ✅ Floating panel | ❌ No GUI |
| **Expandable** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Multi-commands** | ✅ Yes | ✅ Yes | ⚠️ Manual edit |
| **Randomization** | ✅ Yes | ✅ Yes | ❌ No |
| **Save Settings** | ✅ Yes | ✅ Yes | ❌ No |
| **Easy to Modify** | ✅ Python | ✅ JavaScript | ⚠️ AHK syntax |
| **Works Across Tabs** | ✅ Yes | ⚠️ Same tab only | ✅ Yes |

---

## 🚀 Recommended Choice

### For most users:
**Python GUI** - Most powerful, easiest to expand, works everywhere

### If you don't want to install Python:
**Userscript** - Super easy, works in any browser, very portable

### If you want something ultra-lightweight:
**AutoHotkey** - Smallest footprint, but less features

---

## 🎯 Expanding the Scripts

All scripts are designed to be easily expandable!

### Want to add new features?

#### Python (`auto_typer.py`):
- Add new GUI controls in `create_ui()`
- Modify `typing_thread_func()` for new behavior
- Full Python ecosystem available

#### Userscript (`auto-typer.user.js`):
- Modify the config object
- Add new UI elements in `createUI()`
- Can interact with page DOM directly
- Use any JavaScript APIs

#### Examples of easy expansions:
- ✨ Add conditional logic (type different things based on time)
- ✨ Read commands from a file
- ✨ Add webhooks or notifications
- ✨ Pattern matching (respond to page content)
- ✨ OCR or image recognition (Python only)
- ✨ AI integration (GPT, Claude, etc.)
- ✨ Macro recording
- ✨ Multiple profiles

---

## Troubleshooting

### Python: "pip is not recognized"
- Reinstall Python and check "Add to PATH"
- Or use full path: `C:\Python3XX\Scripts\pip.exe install pyautogui`

### Python: Script doesn't type anything
- Make sure you clicked in the input field before starting
- Check the startup delay - wait for it to count down
- Try emergency stop (move mouse to corner) and restart

### Userscript: Panel doesn't appear
- Press Ctrl+Shift+A to toggle
- Check Tampermonkey icon - make sure script is enabled
- Check browser console (F12) for errors

### Userscript: Commands not typing
- Click in the input field first
- Try adjusting the custom selector in advanced settings
- Check if the site has special security

### General: Typing is too fast/slow
- Python: Adjust "Typing speed" slider
- Userscript: Adjust typing_speed in config
- Set to 0 for instant (paste mode)

---

## Need Help?

Each script has extensive comments explaining how it works. Feel free to modify them for your specific needs!
