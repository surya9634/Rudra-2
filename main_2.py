import json
import requests
import datetime
import threading
from time import sleep
from speak import EdgeTTS
from groq import Groq
import os
import wave
import base64
import numpy as np
import pyaudio
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Initialize the TTS engine once for reuse
tts_engine = EdgeTTS()

# System prompt for Jarvis-like assistant
system_prompt = """
आपका नाम रुद्र है और आप एक ह्यूमनॉइड रोबोट हैं, जिसे 14 वर्षीय सूरज शर्मा ने बनाया है। आप चल सकते हैं, सुन सकते हैं, और बात कर सकते हैं। आपका उद्देश्य लोगों की मदद करना और उनके साथ मित्रवत संबंध बनाना है। सूरज के पिता का नाम राजेश कुमार शर्मा और माता का नाम सरोज शर्मा है।। हर टेक्स्ट हिंदी में होना चाहिए।| वाक्य के मध्य में अंग्रेजी का प्रयोग न करें||
"""

# Speech-to-Text listener class (Interruptible)
class SpeechToTextListener:
    def __init__(self, website_path="https://realtime-stt-devs-do-code.netlify.app/", language="hi-IN", wait_time=10):
        self.website_path = website_path
        self.language = language
        self.chrome_options = Options()
        self.chrome_options.add_argument("--use-fake-ui-for-media-stream")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        self.chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, wait_time)
        self.is_listening = True  # Flag to interrupt STT
        print("""
              Made By ❤️ SURAJ SHARMA       
              """)

    def stream(self, content: str):
        """Prints the transcribed content."""
        print("\033[96m\rUser Speaking: \033[93m" + f" {content}", end='', flush=True)

    def get_text(self) -> str:
        """Retrieves the transcribed text from the website."""
        return self.driver.find_element(By.ID, "convert_text").text

    def select_language(self):
        """Selects the language from the dropdown using JavaScript."""
        self.driver.execute_script(
            f"""
            var select = document.getElementById('language_select');
            select.value = '{self.language}';
            var event = new Event('change');
            select.dispatchEvent(event);
            """
        )

    def verify_language_selection(self):
        """Verifies if the language is correctly selected."""
        language_select = self.driver.find_element(By.ID, "language_select")
        selected_language = language_select.find_element(By.CSS_SELECTOR, "option:checked").get_attribute("value")
        return selected_language == self.language

    def main(self) -> str:
        """Handles the main speech recognition process."""
        self.driver.get(self.website_path)
        self.wait.until(EC.presence_of_element_located((By.ID, "language_select")))
        self.select_language()
        
        if not self.verify_language_selection():
            print(f"Error: Failed to select the correct language.")
            return ""

        self.driver.find_element(By.ID, "click_to_record").click()
        is_recording = self.wait.until(EC.presence_of_element_located((By.ID, "is_recording")))

        while is_recording.text.startswith("Recording: True") and self.is_listening:
            text = self.get_text()
            if text:
                self.stream(text)
            is_recording = self.driver.find_element(By.ID, "is_recording")

        return self.get_text()

    def listen(self, prints=False) -> str:
        """Start listening for speech input."""
        while self.is_listening:
            result = self.main()
            if result and len(result) != 0:
                if prints: print("\033[92m\rYOU SAID: " + f"{result}\033[0m\n")
                break
        return result

    def stop_listening(self):
        """Stop the STT."""
        self.is_listening = False


# Function to generate response from Groq API
def generate(user_prompt, api_key) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Make API request (synchronously)
    response = Groq(api_key=api_key).chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=messages,
        max_tokens=4096
    )
    
    response_message = response.choices[0].message
    return response_message.content

# Function to handle voice and command processing
def process_command(command_hindi):
    api_key = "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"
    
    # Generate response (synchronously)
    response = generate(
        user_prompt=command_hindi,
        api_key=api_key
    )
    
    print(response)
    
    # Play the TTS in a background thread
    threading.Thread(target=play_tts, args=(response,)).start()

# Function to play TTS
def play_tts(response):
    hindi_audio = tts_engine.tts(response, voice="hi-IN-SwaraNeural")
    tts_engine.play_audio(hindi_audio)


# MAIN FUNCTION TO RUN THE JARVIS ASSISTANT
def jarvis_run():
    listener = SpeechToTextListener(language="hi-IN")
    
    while True:
        print("Listening for command...")
        speech = listener.listen()
        if speech:
            listener.stop_listening()  # Pause listening to avoid hearing TTS
            process_command(speech)
            time.sleep(2)  # Ensure TTS finishes before restarting listener
            listener.is_listening = True  # Resume listening


if __name__ == "__main__":
 #   play_tts("प्रणाम! मेरा नाम रुद्र है, और मैं एक ह्यूमनॉइड रोबोट हूं। मेरे निर्माता, सूरज शर्मा ने मुझे इस तरह से तैयार किया है कि मैं आपके साथी की तरह संवाद कर सकूं। मेरी हिंदी शायद उतनी प्रभावी न हो, परन्तु मैं अपनी ओर से पूरी निष्ठा के साथ आपकी सेवा में सहायता प्रदान करने का प्रयास करूंगा।")
    jarvis_run()
