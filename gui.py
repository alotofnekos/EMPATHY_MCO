import random
import tkinter as tk
import warnings
from tkinter import messagebox, scrolledtext

from transformers import Conversation, pipeline
from transformers.utils import logging

warnings.filterwarnings("ignore")
logging.set_verbosity_error()

import recommender

# Simulated modules for sentences and recommender. Replace with your actual modules.
import sentences


class IndianFoodChatbotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Indian Food Chatbot")

        self.conversation = Conversation()
        self.emotion_scores = {
            "anger": 0,
            "disgust": 0,
            "fear": 0,
            "joy": 0,
            "neutral": 0,
            "sadness": 0,
            "surprise": 0
        }
        self.allergy_ingredients = ['milk', 'lactose', 'tree nuts', 'peanuts', 'egg', 'wheat', 'soy', 'shellfish']

        self.conversation_text = scrolledtext.ScrolledText(master, height=15, width=75)
        self.conversation_text.pack()

        self.user_input = tk.Entry(master)
        self.user_input.pack()

        self.send_button = tk.Button(master, text="Send", command=self.process_input)
        self.send_button.pack()

        # Set up pipelines for conversation and emotion analysis.
        self.chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")
        self.classifier_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

        self.greet_user()

        self.allergies_button = tk.Button(master, text="Set Allergies", command=self.set_allergies)
        self.allergies_button.pack()

    def greet_user(self):
        bot_random_response = random.choice(sentences.intro_sentences)
        self.append_conversation("Bot", bot_random_response)
        # Add the greeting to the conversation context.
        self.conversation.add_user_input(bot_random_response)

    def append_conversation(self, sender, message):
        self.conversation_text.insert(tk.END, f"{sender}: {message}\n")
        self.conversation_text.see(tk.END)
        self.master.update()

    def process_input(self):
        user_input = self.user_input.get().strip()
        if not user_input:
            return
        self.append_conversation("You", user_input)

        self.conversation.add_user_input(user_input)
        response = self.chatbot([self.conversation], pad_token_id=50256)[0]

        bot_response = response.generated_responses[-1]
        self.append_conversation("Bot", bot_response)

        self.process_emotion(user_input)
        self.user_input.delete(0, tk.END)

    def process_emotion(self, user_input):
        input_emotion_scores = self.classifier_pipeline(user_input)
        for score in input_emotion_scores:
            for emotion_score in score:
                emotion = emotion_score['label'].lower()
                if emotion in self.emotion_scores:
                    self.emotion_scores[emotion] += emotion_score['score']

    def set_allergies(self):
        allergies_selected = []
        for allergy in self.allergy_ingredients:
            answer = messagebox.askyesno("Allergy Check", f"Are you allergic to {allergy}?")
            if answer:
                allergies_selected.append(allergy)
        self.append_conversation("Bot", f"Noted allergies: {', '.join(allergies_selected) if allergies_selected else 'None'}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = IndianFoodChatbotGUI(root)
    root.mainloop()
