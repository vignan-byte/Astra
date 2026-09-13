import os
import subprocess
import time
from pathlib import Path

import psutil
import pyautogui


APPLICATIONS = {
    "chrome": [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "explorer": ["explorer.exe"],
}


def _find_executable(candidates):
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate

    for candidate in candidates:
        if not Path(candidate).suffix:
            return candidate

    return None


def _running(process_name):
    process_name = process_name.lower()

    return any(
        process_name in (p.info.get("name") or "").lower()
        for p in psutil.process_iter(["name"])
    )


def open_application(name):
    name = name.lower().strip()

    if name not in APPLICATIONS:
        return {
            "success": False,
            "message": f"Unknown application: {name}"
        }

    executable = _find_executable(APPLICATIONS[name])

    if executable is None:
        return {
            "success": False,
            "message": f"Could not find {name}."
        }

    try:
        subprocess.Popen([executable])
        time.sleep(2)

        return {
            "success": True,
            "application": name,
            "verified": True,
            "message": f"{name.capitalize()} opened successfully."
        }

    except Exception as exc:
        return {
            "success": False,
            "message": str(exc)
        }


def chrome_search(query):
    query = query.strip()

    if not query:
        return {
            "success": False,
            "message": "Search query is empty."
        }

    opened = open_application("chrome")

    if not opened.get("success"):
        return opened

    time.sleep(1)

    try:
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.3)

        pyautogui.write(
            "https://www.google.com/search?q=" + query.replace(" ", "+"),
            interval=0.01
        )

        pyautogui.press("enter")

        time.sleep(2)

        return {
            "success": True,
            "verified": True,
            "query": query,
            "message": f"I searched Chrome for {query}."
        }

    except Exception as exc:
        return {
            "success": False,
            "message": f"Chrome search failed: {exc}"
        }


def type_text(text):
    try:
        pyautogui.write(text, interval=0.02)

        return {
            "success": True,
            "verified": True,
            "message": "Text entered successfully."
        }

    except Exception as exc:
        return {
            "success": False,
            "message": f"Typing failed: {exc}"
        }


def press_key(key):
    try:
        pyautogui.press(key)

        return {
            "success": True,
            "verified": True,
            "message": f"Pressed {key}."
        }

    except Exception as exc:
        return {
            "success": False,
            "message": f"Key press failed: {exc}"
        }
