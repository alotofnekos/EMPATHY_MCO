from transformers import pipeline
import random
import pandas as pd
import sentences


class IndianFoodChatbot:

    def __init__(self):
        self.classifier_pipeline = pipeline(task="text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
        self.conversation_pipeline = pipeline(task="conversational")
        self.emotion_scores = {
            "anger": 0,
            "disgust": 0,
            "fear": 0,
            "joy": 0,
            "neutral": 0,
            "sadness": 0,
            "surprise": 0
        }
        self.sentences = sentences
        self.allergy_ingredients = ['milk', 'lactose', 'tree nuts', 'peanuts', 'egg', 'wheat', 'soy', 'shellfish']

    def get_highest_score(self):
        return max(self.emotion_scores, key=self.emotion_scores.get)
    
    def reset_scores(self):
        self.emotion_scores = dict.fromkeys(self.emotion_scores, 0)

    def increment_scores(self, scores):
        for index, (key, value) in enumerate(self.emotion_scores.items()):
            self.emotion_scores[key] += scores[0][index]['score']

    def chat(self):
        while True:
            allergies = []
            is_vegan = False
            like_spicy = True

            user_input = input("Bot: " + self.sentences.intro_sentences[random.randint(len(self.sentences.intro_sentences))] + "\nYou: ")

            input_emotion_scores = self.classifier_pipeline(user_input)
            self.increment_scores(input_emotion_scores)

            ### CONVERSATION LOOP
            for i in range(3):
                bot_response = self.conversation_pipeline("User: " + user_input)[0]['generated_text']
                user_input = input("Bot: " + bot_response + self.sentences.follow_up_sentences[i] + "\nYou: ")
                input_emotion_scores = self.classifier_pipeline(user_input)
                self.increment_scores(input_emotion_scores)

            print("Bot: " + self.sentences.preferences_sentences[random.randint(len(self.sentences.preferences_sentences))])
            print("Please respond with Yes or No, and type in the names of the ingredients from the list that you are allergic to when I ask.")

            # Ask for allergies
            user_input = input("Bot: " + self.sentences.ask_allergy_sentences[random.randint(len(self.sentences.ask_allergy_sentences))] + "\nYou: ")
            for ingredient in self.allergy_ingredients:
                if ingredient in user_input.lower():
                    allergies.append(ingredient)
            
            # Ask for vegan
            user_input = input("Bot: " + self.sentences.ask_vegan_sentences[random.randint(len(self.sentences.ask_vegan_sentences))] + "\nYou: ")
            if "yes" in user_input.lower():
                is_vegan = True

            # Ask for spicy
            user_input = input("Bot: " + self.sentences.ask_spicy_sentences[random.randint(len(self.sentences.ask_spicy_sentences))] + "\nYou: ")
            if "no" in user_input.lower():
                like_spicy = False


            print(f"Bot: I can see that you are feeling {self.get_highest_score()}.")

            if user_input.lower() == "exit":
                break