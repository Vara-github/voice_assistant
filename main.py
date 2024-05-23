import pvporcupine
import pyaudio
import numpy as np
import speech_recognition as sr
import pyttsx3
import time
import pyjokes

# Initialize the recognizer and the text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Replace 'YOUR_ACCESS_KEY' with the access key you obtained from Picovoice Console
access_key = "rPkAx6tjjeMwxt02GSSWdfER3o0lgKopxYVveryLJr8LelX9opOHTQ=="

# Porcupine initialization for hotword detection
porcupine = pvporcupine.create(access_key=access_key, keywords=["alexa"])

# Audio stream setup
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("Listening for wake word...")

def get_response(command):
    responses = {
        "what is your name": "My name is Alexa.",
        "how are you": "I am just a program, so I don't have feelings, but thanks for asking.",
        "what time is it": time.strftime("It's %I:%M %p."),
        "tell me a joke": pyjokes.get_joke(),
        "exit": "Goodbye!"
    }
    return responses.get(command.lower(), "I didn't understand that.")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = np.frombuffer(pcm, dtype=np.int16)
        
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Wake word detected!")
            
            # Listen for a command
            with sr.Microphone() as source:
                print("Listening for command...")
                audio = recognizer.listen(source)

            # Recognize the command
            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                
                # Get the response for the command
                response = get_response(command)
                print(f"Response: {response}")

                # Speak the response back to the user
                engine.say(response)
                engine.runAndWait()

                # Exit the loop if the command is 'exit'
                if command.lower() == "exit":
                    break
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service")
                engine.say("I couldn't request results")
                engine.runAndWait()
            except sr.UnknownValueError:
                print("Could not understand the audio")
                engine.say("I couldn't understand the audio")
                engine.runAndWait()
finally:
    audio_stream.stop_stream()
    audio_stream.close()
    porcupine.delete()
    pa.terminate()
