import os
import subprocess
import logging
import sys
import asyncio
from fuzzywuzzy import process

try:
    from livekit.agents import function_tool
except ImportError:
    def function_tool(func): 
        return func

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Setup encoding and logger
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App command map
APP_MAPPINGS = {
    "notepad": "notepad",
    "calculator": "calc",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "browser": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "file": "explorer",
    "command prompt": "cmd",
    "control panel": "control",
    "excel": "excel",
    "paint": "mspaint",
    "screenshot": "snippingtool",
    "setting": "ms-settings:",
}

# -------------------------
# Global focus utility
# -------------------------
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow not available")
        return False

    await asyncio.sleep(2.0)  # Give more time for window to appear
    title_keyword = title_keyword.lower().strip()
    
    # Special case for chrome
    if "chrome" in title_keyword or "browser" in title_keyword:
        title_keyword = "google chrome"

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            try:
                if window.isMinimized:
                    window.restore()
                # Use a small delay before activation
                await asyncio.sleep(0.5)
                window.activate()
                return True
            except Exception as e:
                logger.error(f"Focus error: {e}")
    return False

# Index files/folders
async def index_items(base_dirs):
    item_index = []
    for base_dir in base_dirs:
        for root, dirs, files in os.walk(base_dir):
            for d in dirs:
                item_index.append({"name": d, "path": os.path.join(root, d), "type": "folder"})
            for f in files:
                item_index.append({"name": f, "path": os.path.join(root, f), "type": "file"})
    logger.info(f"✅ Indexed {len(item_index)} items.")
    return item_index

async def search_item(query, index, item_type):
    filtered = [item for item in index if item["type"] == item_type]
    choices = [item["name"] for item in filtered]
    if not choices:
        return None
    best_match, score = process.extractOne(query, choices)
    logger.info(f"🔍 Matched '{query}' to '{best_match}' with score {score}")
    if score > 70:
        for item in filtered:
            if item["name"] == best_match:
                return item
    return None

# File/folder actions
async def open_folder(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ फ़ाइल open करने में error आया। {e}")

async def play_file(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ फ़ाइल open करने में error आया।: {e}")

async def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Folder create हो गया।: {path}"
    except Exception as e:
        return f"❌ फ़ाइल create करने में error आया।: {e}"

async def rename_item(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        return f"✅ नाम बदलकर {new_path} कर दिया गया।"
    except Exception as e:
        return f"❌ नाम बदलना fail हो गया: {e}"

async def delete_item(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return f"🗑️ Deleted: {path}"
    except Exception as e:
        return f"❌ Delete नहीं हुआ।: {e}"

# App control
@function_tool
async def open(app_title: str) -> str:
    app_title = app_title.lower().strip()
    app_command = APP_MAPPINGS.get(app_title, app_title)
    
    try:
        # If it's a direct path with spaces, we need start "" "path"
        # If it's an alias or command, start "alias" works too
        if ":" in app_command and "\\" in app_command:
            cmd = f'start "" "{app_command}"'
        else:
            cmd = f'start {app_command}'
            
        await asyncio.create_subprocess_shell(cmd, shell=True)
        
        focused = await focus_window(app_title)
        if focused:
            return f"🚀 App '{app_title}' launched and focused."
        else:
            return f"🚀 {app_title} launched, but could not focus window."
    except Exception as e:
        return f"❌ Failed to launch {app_title}: {e}"

@function_tool
async def close(window_title: str) -> str:
    if not win32gui:
        return "❌ win32gui library not found (Windows only)"

    found_windows = []

    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            text = win32gui.GetWindowText(hwnd)
            if window_title.lower() in text.lower():
                try:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    found_windows.append(text)
                except Exception:
                    pass

    win32gui.EnumWindows(enumHandler, None)
    
    if found_windows:
        return f"✅ Window(s) closed: {', '.join(found_windows)}"
    else:
        return f"❌ No open window found matching '{window_title}'"

# Jarvis command logic
@function_tool
async def folder_file(command: str) -> str:
    folders_to_index = ["D:/"]
    index = await index_items(folders_to_index)
    command_lower = command.lower()

    if "create folder" in command_lower:
        folder_name = command.replace("create folder", "").strip()
        path = os.path.join("D:/", folder_name)
        return await create_folder(path)

    if "rename" in command_lower:
        parts = command_lower.replace("rename", "").strip().split("to")
        if len(parts) == 2:
            old_name = parts[0].strip()
            new_name = parts[1].strip()
            item = await search_item(old_name, index, "folder")
            if item:
                new_path = os.path.join(os.path.dirname(item["path"]), new_name)
                return await rename_item(item["path"], new_path)
        return "❌ rename command valid नहीं है।"

    if "delete" in command_lower:
        item = await search_item(command, index, "folder") or await search_item(command, index, "file")
        if item:
            return await delete_item(item["path"])
        return "❌ Delete करने के लिए item नहीं मिला।"

    if "folder" in command_lower or "open folder" in command_lower:
        item = await search_item(command, index, "folder")
        if item:
            await open_folder(item["path"])
            return f"✅ Folder opened: {item['name']}"
        return "❌ Folder नहीं मिला।."

    item = await search_item(command, index, "file")
    if item:
        await play_file(item["path"])
        return f"✅ File opened: {item['name']}"

    return "⚠ कुछ भी match नहीं हुआ।"
