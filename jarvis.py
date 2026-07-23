"""Jarvis assistant main file."""

import speech_recognition as speech_recognition
import pyttsx3
import requests
import json
import os
import re
import subprocess
import webbrowser


class sr:
    class Recognizer(speech_recognition.Recognizer):
        def __init__(self):
            super().__init__()

        def listen(self, source, timeout=None, phrase_time_limit=None):
            return super().listen(source, timeout=timeout,
                                  phrase_time_limit=phrase_time_limit)

        def listen_in_background(self, source, callback,
                                 phrase_time_limit=None):
            return super().listen_in_background(
                source, callback, phrase_time_limit=phrase_time_limit)

        def recognize_google(
            self,
            audio_data,
            key=None,
            language="en-US",
            show_all=False,
        ):
            return super().recognize_google(
                audio_data,
                key=key,
                language=language,
                show_all=show_all,
            )

        def adjust_for_ambient_noise(self, source, duration=1):
            return super().adjust_for_ambient_noise(source, duration=duration)

    Microphone = speech_recognition.Microphone
    UnknownValueError = speech_recognition.UnknownValueError
    RequestError = speech_recognition.RequestError


# Configuration
API_KEY = "YOUR_API_KEY"

API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-site.com",
    "X-Title": "Jarvis Assistant",
}

# Initialize
engine = pyttsx3.init()
engine.setProperty("rate", 180)

recognizer = sr.Recognizer()
microphone = sr.Microphone()


def callback(recognizer, audio):
    try:
        command = recognizer.recognize_google(audio)

        if command.lower() == "stop":
            engine.stop()
            print("Speech stopped by user")
    except (sr.UnknownValueError, sr.RequestError):
        # ignore recognition errors in background callback
        pass


def speak(text, allow_interruption=False):
    stopper = None
    if allow_interruption:
        # start background listening and keep stopper to stop it later
        stopper = recognizer.listen_in_background(microphone, callback)

    engine.say(text)
    engine.runAndWait()

    if stopper:
        # stop background listening without waiting for callbacks to finish
        stopper(wait_for_stop=False)


def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

        print("Listening...")
        audio = recognizer.listen(source)

        try:
            query = recognizer.recognize_google(audio)
            print("You said:", query)
            return query

        except (sr.UnknownValueError, sr.RequestError):
            return None


def clean_response(text):
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\*+", "", text)
    text = text.strip()
    return text


def chat_with_deepseek(prompt):

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are Jarvis, an intelligent AI assistant.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(
        API_URL,
        headers=HEADERS,
        data=json.dumps(data),
    )

    result = response.json()

    answer = result["choices"][0]["message"]["content"]
    return clean_response(answer)


# Utility Functions


def shutdown():
    speak("Shutting down the system.")
    os.system("shutdown /s /t 1")


def open_chrome():
    speak("Opening Chrome")

    path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    subprocess.Popen(path)


def search_google(query):
    speak(f"Searching Google for {query}")
    webbrowser.open(f"https://www.google.com/search?q={query}")


# Main Loop

if __name__ == "__main__":

    speak("Hello, I am Jarvis. Say Jarvis to wake me.")

    while True:

        wake_input = listen()

        if wake_input and "jarvis" in wake_input.lower():

            speak("Yes? What would you like me to do?")

            command = listen()

            if command:

                command = command.lower()

                if any(word in command for word in ["exit", "quit", "stop"]):
                    speak("Goodbye!")
                    break

                elif "shutdown" in command:
                    shutdown()

                elif "open chrome" in command:
                    open_chrome()

                elif "search for" in command:
                    search_query = command.replace("search for", "")
                    search_google(search_query)

                else:
                    response = chat_with_deepseek(command)
                    speak(response)
