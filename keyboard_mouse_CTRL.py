import pyautogui
import asyncio
import threading
import time
from datetime import datetime
from typing import List

from pynput.keyboard import Key, KeyCode, Controller as KeyboardController, Listener as KeyboardListener
from pynput.mouse import Button, Controller as MouseController

import speech_recognition as sr
from PIL import Image
import pytesseract

from livekit.agents import function_tool

# =========================
# GLOBAL CONFIG
# =========================
KILL_HOTKEY = {Key.ctrl_l, Key.shift, KeyCode.from_char('q')}
VOICE_KILL_PHRASE = "vecna stop now"

PERMISSION_LEVEL = "GOD"  # GOD / SAFE / NONE

# =========================
# FULL ACCESS CONTROLLER
# =========================
class VecnaController:
    def __init__(self):
        self.active = True
        self.permission = PERMISSION_LEVEL
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        self.valid_intents = {
            "move", "click", "scroll", "type",
            "press", "hotkey", "volume", "swipe"
        }

        self.special_keys = {
            "enter": Key.enter, "space": Key.space, "tab": Key.tab,
            "shift": Key.shift, "ctrl": Key.ctrl, "alt": Key.alt,
            "esc": Key.esc, "backspace": Key.backspace, "delete": Key.delete,
            "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right
        }

        self.log("VECNA GOD MODE INITIALIZED")

        self.start_kill_switch()
        self.start_voice_kill_switch()

    # =========================
    # CORE SAFETY
    # =========================
    def emergency_stop(self):
        self.active = False
        self.log("🚨 EMERGENCY STOP ACTIVATED")
        print("🛑 VECNA STOPPED")

    def intent_validator(self, intent: str):
        if self.permission != "GOD":
            raise Exception("❌ Insufficient permission")

        if intent not in self.valid_intents:
            raise Exception(f"❌ Invalid intent: {intent}")

    # =========================
    # LOGGING
    # =========================
    def log(self, msg: str):
        with open("vecna_log.txt", "a") as f:
            f.write(f"{datetime.now()} | {msg}\n")

    # =========================
    # KILL SWITCH: KEYBOARD
    # =========================
    def start_kill_switch(self):
        pressed = set()

        def on_press(key):
            pressed.add(key)
            if all(k in pressed for k in KILL_HOTKEY):
                self.emergency_stop()

        def on_release(key):
            pressed.discard(key)

        listener = KeyboardListener(on_press=on_press, on_release=on_release)
        listener.daemon = True
        listener.start()

    # =========================
    # KILL SWITCH: VOICE
    # =========================
    def start_voice_kill_switch(self):
        def listen():
            r = sr.Recognizer()
            mic = sr.Microphone()
            while self.active:
                try:
                    with mic as source:
                        audio = r.listen(source, phrase_time_limit=3)
                        text = r.recognize_google(audio).lower()
                        if VOICE_KILL_PHRASE in text:
                            self.emergency_stop()
                except:
                    pass

        t = threading.Thread(target=listen, daemon=True)
        t.start()

    # =========================
    # SCREEN AWARENESS
    # =========================
    def read_screen_text(self):
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        self.log("Screen text analyzed")
        return text.lower()

    # =========================
    # ACTIONS (ALL VALIDATED)
    # =========================
    async def move_cursor(self, direction: str, distance: int = 100):
        self.intent_validator("move")
        if not self.active: return

        x, y = self.mouse.position
        if direction == "left": self.mouse.position = (x - distance, y)
        if direction == "right": self.mouse.position = (x + distance, y)
        if direction == "up": self.mouse.position = (x, y - distance)
        if direction == "down": self.mouse.position = (x, y + distance)

    async def mouse_click(self, button="left"):
        self.intent_validator("click")
        if button == "left": self.mouse.click(Button.left, 1)
        if button == "right": self.mouse.click(Button.right, 1)

    async def type_text(self, text: str):
        self.intent_validator("type")
        for ch in text:
            self.keyboard.press(ch)
            self.keyboard.release(ch)
            await asyncio.sleep(0.03)

    async def press_key(self, key: str):
        self.intent_validator("press")
        k = self.special_keys.get(key.lower(), key)
        self.keyboard.press(k)
        self.keyboard.release(k)

    async def press_hotkey(self, keys: List[str]):
        self.intent_validator("hotkey")
        resolved = [self.special_keys.get(k.lower(), k) for k in keys]
        for k in resolved: self.keyboard.press(k)
        for k in reversed(resolved): self.keyboard.release(k)

    async def swipe(self, direction: str):
        self.intent_validator("swipe")
        if direction == "up": pyautogui.dragRel(0, -300, 0.4)
        if direction == "down": pyautogui.dragRel(0, 300, 0.4)
        if direction == "left": pyautogui.dragRel(-300, 0, 0.4)
        if direction == "right": pyautogui.dragRel(300, 0, 0.4)

    async def scroll(self, direction: str, amount: int = 5):
        self.intent_validator("scroll")
        dx, dy = 0, 0
        if direction == "up": dy = amount
        elif direction == "down": dy = -amount
        elif direction == "left": dx = -amount
        elif direction == "right": dx = amount
        self.mouse.scroll(dx, dy)

    async def volume(self, action: str):
        self.intent_validator("volume")
        if action == "up": 
            self.keyboard.press(Key.media_volume_up)
            self.keyboard.release(Key.media_volume_up)
        elif action == "down": 
            self.keyboard.press(Key.media_volume_down)
            self.keyboard.release(Key.media_volume_down)
        elif action == "mute": 
            self.keyboard.press(Key.media_volume_mute)
            self.keyboard.release(Key.media_volume_mute)

# =========================
# LIVEKIT TOOLS
# =========================
controller = VecnaController()

@function_tool
async def move_cursor_tool(direction: str, distance: int = 100):
    return await controller.move_cursor(direction, distance)

@function_tool
async def mouse_click_tool(button: str = "left"):
    return await controller.mouse_click(button)

@function_tool
async def type_text_tool(text: str):
    return await controller.type_text(text)

@function_tool
async def press_key_tool(key: str):
    return await controller.press_key(key)

@function_tool
async def press_hotkey_tool(keys: List[str]):
    return await controller.press_hotkey(keys)

@function_tool
async def swipe_gesture_tool(direction: str):
    return await controller.swipe(direction)

@function_tool
async def scroll_cursor_tool(direction: str, amount: int = 5):
    return await controller.scroll(direction, amount)

@function_tool
async def control_volume_tool(action: str):
    return await controller.volume(action)
