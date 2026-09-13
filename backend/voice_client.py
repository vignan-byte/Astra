import json
import queue
import threading
import time
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import scrolledtext

import speech_recognition as sr
import pyttsx3

from app.tools.computer import chrome_search, open_application


API = "http://127.0.0.1:8000"


class AstraVoice:

    def __init__(self, root):
        self.root = root
        self.root.title("ASTRA AI")
        self.root.geometry("760x540")

        self.running = True
        self.events = queue.Queue()

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.7

        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", 175)

        self.log = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state="disabled",
            font=("Segoe UI", 11)
        )
        self.log.pack(fill="both", expand=True, padx=15, pady=15)

        self.status = tk.Label(
            root,
            text="Starting ASTRA...",
            font=("Segoe UI", 12)
        )
        self.status.pack(pady=(0, 15))

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.log_message("ASTRA", "Voice system starting...")

        threading.Thread(
            target=self.voice_loop,
            daemon=True
        ).start()

        self.root.after(100, self.process_events)

    def log_message(self, speaker, message):
        self.events.put(("log", f"{speaker}: {message}"))

    def set_status(self, text):
        self.events.put(("status", text))

    def process_events(self):

        try:
            while True:

                event, value = self.events.get_nowait()

                if event == "log":
                    self.log.configure(state="normal")
                    self.log.insert(tk.END, value + "\n")
                    self.log.see(tk.END)
                    self.log.configure(state="disabled")

                elif event == "status":
                    self.status.config(text=value)

        except queue.Empty:
            pass

        if self.running:
            self.root.after(100, self.process_events)

    def chat(self, message):

        data = json.dumps({
            "message": message
        }).encode("utf-8")

        request = urllib.request.Request(
            f"{API}/chat",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            raw = response.read().decode("utf-8")

            self.log_message(
                "BACKEND",
                raw
            )

            return json.loads(raw)

    def execute_command(self, command):

        command = command.lower().strip()

        # Direct computer tools
        if command.startswith("search for "):

            query = command[len("search for "):].strip()

            result = chrome_search(query)

            return result.get(
                "message",
                "Search completed."
            )

        if command.startswith("search "):

            query = command[len("search "):].strip()

            result = chrome_search(query)

            return result.get(
                "message",
                "Search completed."
            )

        applications = (
            "chrome",
            "notepad",
            "calculator",
            "paint",
            "explorer"
        )

        if command.startswith("open "):

            app_name = command[len("open "):].strip()

            if app_name in applications:

                result = open_application(app_name)

                return result.get(
                    "message",
                    "Application command completed."
                )

        # Everything else goes through the real ASTRA agent
        result = self.chat(command)

        return result.get(
            "response",
            "Request completed."
        )

    def speak(self, text):

        self.log_message(
            "ASTRA",
            text
        )

        try:
            self.tts.say(text)
            self.tts.runAndWait()

        except Exception as exc:

            self.log_message(
                "TTS ERROR",
                str(exc)
            )

    def listen(self, source, timeout=5, phrase_limit=12):

        try:

            self.set_status("Listening...")

            audio = self.recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit
            )

            self.set_status("Understanding...")

            text = self.recognizer.recognize_google(
                audio
            ).lower().strip()

            if text:
                self.log_message(
                    "YOU",
                    text
                )

            return text

        except sr.WaitTimeoutError:
            return None

        except sr.UnknownValueError:
            return None

        except sr.RequestError as exc:

            self.log_message(
                "VOICE ERROR",
                str(exc)
            )

            return None

        except Exception as exc:

            self.log_message(
                "VOICE ERROR",
                str(exc)
            )

            return None

    def extract_command(self, text):

        if not text:
            return None

        text = text.lower().strip()

        wake_words = (
            "hey astra",
            "hey aster",
            "hey extra",
            "hey alexa",
            "astra",
            "aster"
        )

        for wake in wake_words:

            if wake in text:

                return text.split(
                    wake,
                    1
                )[1].strip()

        return None

    def handle_command(self, command):

        try:

            self.set_status(
                "ASTRA is working..."
            )

            self.log_message(
                "ASTRA",
                f"Executing: {command}"
            )

            response = self.execute_command(
                command
            )

            self.speak(response)

        except urllib.error.HTTPError as exc:

            try:
                body = exc.read().decode(
                    "utf-8",
                    errors="replace"
                )
            except Exception:
                body = str(exc)

            self.log_message(
                "API ERROR",
                f"HTTP {exc.code}: {body}"
            )

            self.speak(
                "The ASTRA backend returned an error."
            )

        except urllib.error.URLError as exc:

            self.log_message(
                "API ERROR",
                str(exc)
            )

            self.speak(
                "I cannot reach the ASTRA backend."
            )

        except Exception as exc:

            self.log_message(
                "ASTRA ERROR",
                str(exc)
            )

            self.speak(
                "Something went wrong."
            )

        self.set_status(
            "Waiting for Hey Astra..."
        )

    def voice_loop(self):

        try:

            with sr.Microphone() as source:

                self.set_status(
                    "Calibrating microphone..."
                )

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                self.log_message(
                    "ASTRA",
                    "Microphone ready."
                )

                self.speak(
                    "ASTRA is ready."
                )

                self.set_status(
                    "Waiting for Hey Astra..."
                )

                while self.running:

                    text = self.listen(
                        source,
                        timeout=5,
                        phrase_limit=12
                    )

                    if not text:
                        continue

                    command = self.extract_command(
                        text
                    )

                    if command is None:
                        continue

                    if not command:

                        self.speak(
                            "Yes?"
                        )

                        command = self.listen(
                            source,
                            timeout=8,
                            phrase_limit=15
                        )

                        if not command:
                            continue

                    if command in (
                        "sleep",
                        "go to sleep",
                        "stop listening"
                    ):

                        self.speak(
                            "Going to sleep."
                        )

                        self.set_status(
                            "Waiting for Hey Astra..."
                        )

                        continue

                    threading.Thread(
                        target=self.handle_command,
                        args=(command,),
                        daemon=True
                    ).start()

                    time.sleep(0.5)

        except Exception as exc:

            self.log_message(
                "VOICE SYSTEM ERROR",
                str(exc)
            )

            self.set_status(
                "Voice system error"
            )

    def close(self):

        self.running = False

        try:
            self.tts.stop()
        except Exception:
            pass

        self.root.destroy()


if __name__ == "__main__":

    root = tk.Tk()

    app = AstraVoice(root)

    root.mainloop()
