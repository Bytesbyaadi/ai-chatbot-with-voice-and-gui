import google.generativeai as ai
import speech_recognition as sr
import pyttsx3
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence, ImageDraw
import pywhatkit
import webbrowser

# Configure Google AI Model
ai.configure(api_key="AIzaSyAKpdBlvws2eqZLMVbo9NDbOSKEv5xWWFM")
model = ai.GenerativeModel("gemini-1.5-pro-latest")
chat = model.start_chat()

# Initialize Speech Engine
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Setup GUI Window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("AI Chatbot")
root.geometry("900x600+350+20")

title_label = ctk.CTkLabel(root, text="AI Chatbot", font=("Arial", 35, "bold"), text_color="white")
title_label.place(relx=0.5, rely=0.04, anchor="center")

# Load & Animate GIF
gif_path = "D:\WorkShop\Image\drib_blink_bot.gif"
gif = Image.open(gif_path)
frames = [ImageTk.PhotoImage(frame.convert("RGBA")) for frame in ImageSequence.Iterator(gif)]
frame_index = 0

canvas = ctk.CTkCanvas(root, width=450, height=500, bd=0, highlightthickness=0, bg='black')
canvas.place(relx=0.21, rely=0.09, anchor="n")
bg_label = canvas.create_image(0, 0, anchor="nw", image=frames[0])

def update_gif():
    global frame_index
    frame_index = (frame_index + 1) % len(frames)
    canvas.itemconfig(bg_label, image=frames[frame_index])
    root.after(100, update_gif)

update_gif()

# Circular User & Bot Avatars
def make_circle(image_path, size=(40, 40)):
    img = Image.open(image_path).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)
    
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    
    img.putalpha(mask)
    return ImageTk.PhotoImage(img)

user_avatar = make_circle("D:\WorkShop\Image\default-profile-picture-avatar-user-avatar-icon-person-icon-head-icon-profile-picture-icons-default-anonymous-user-male-and-female-businessman-photo-placeholder-social-network-avatar-portrait-free-vector.jpg")
bot_avatar = make_circle("D:\WorkShop\Image\chat-bot-robot-avatar-in-circle-round-shape-isolated-on-white-background-stock-illustration-ai-technology-futuristic-helper-communication-conversation-concept-in-flat-style-vector.jpg")

chat_frame = ctk.CTkScrollableFrame(root, width=480, height=390, fg_color='black')
chat_frame.place(x=380, rely=0.09)

entry = ctk.CTkEntry(root, width=400, placeholder_text="Type your message...")
entry.place(x=425, y=470)

send_button = ctk.CTkButton(root, text="Send", command=lambda: get_response(entry.get()))
send_button.place(x=450, y=520)

voice_button = ctk.CTkButton(root, text="🎤 Speak", command=lambda: get_response(listen()))
voice_button.place(x=650, y=520)

# Add Messages to Chat Window
def add_message(text, sender="user"):
    frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
    frame.pack(fill="x", pady=5, padx=5, anchor="w" if sender == "bot" else "e")

    img = user_avatar if sender == "user" else bot_avatar
    avatar = ctk.CTkLabel(frame, image=img, text="")
    avatar.pack(side="left" if sender == "bot" else "right", padx=5)

    msg_label = ctk.CTkLabel(frame, text=text, wraplength=300, justify="left" if sender == "bot" else "right")
    msg_label.pack(side="left" if sender == "bot" else "right")

    chat_frame.update_idletasks()
    chat_frame._parent_canvas.yview_moveto(1)

# Speech Recognition
def listen():
    with sr.Microphone() as source:
        add_message("Listening...", "bot")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            add_message("Could not understand. Try again.", "bot")
        except sr.RequestError:
            add_message("Network issue. Try again later.", "bot")
        except sr.WaitTimeoutError:
            add_message("No speech detected. Try again.", "bot")
        return None

# Chatbot Response Logic
def get_response(message):
    if not message:
        return

    add_message(f"You: {message}", "user")

    if message.lower() == "bye":
        add_message("Chatbot: Goodbye!", "bot")
        engine.say("Goodbye!")
        engine.runAndWait()
        root.quit()
        return

    # Google Search Handling
    if "open google and search for" in message.lower():
        search_query = message.lower().replace("open google and search for", "").strip()
        if search_query:
            add_message(f"Chatbot: Searching Google for '{search_query}'...", "bot")
            pywhatkit.search(search_query)
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
            engine.say(f"Searching Google for {search_query}")
            engine.runAndWait()
            return

    # YouTube Search Handling
    if "open youtube for" in message.lower():
        search_query = message.lower().replace("open youtube for", "").strip()
        if search_query:
            add_message(f"Chatbot: Searching YouTube for '{search_query}'...", "bot")
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
            engine.say(f"Searching YouTube for {search_query}")
            engine.runAndWait()
            return

    # YouTube Video Playback
    if "open video" in message.lower():
        search_query = message.lower().replace("open video", "").strip()
        if search_query:
            add_message(f"Chatbot: Playing '{search_query}' on YouTube...", "bot")
            pywhatkit.playonyt(search_query)
            engine.say(f"Playing {search_query} on YouTube")
            engine.runAndWait()
            return

    # AI Chat Response
    response = chat.send_message(message)
    add_message(f"Chatbot: {response.text}", "bot")

    engine.say(response.text)
    engine.runAndWait()
    
    entry.delete(0, "end")

root.mainloop()