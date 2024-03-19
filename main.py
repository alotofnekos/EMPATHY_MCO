# https://huggingface.co/docs/transformers/v4.37.2/en/main_classes/pipelines


import random

import pandas as pd
from transformers import Conversation, pipeline

import sentences


class IndianFoodChatbot:

    def __init__(self):
        self.classifier_pipeline = pipeline(task="text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
        self.chatbot = pipeline(task="conversational")
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
        allergies = []
        is_vegan = False
        like_spicy = True

        conversation = Conversation()
        bot_random_response = random.choice(self.sentences.intro_sentences)
        conversation.add_message({"role": "assistant", "content": bot_random_response})
        user_input = input("Bot: " + bot_random_response + "\nYou: ")
        conversation.add_message({"role": "user", "content": user_input})

        input_emotion_scores = self.classifier_pipeline(user_input)
        self.increment_scores(input_emotion_scores)

        ### CONVERSATION LOOP
        for i in range(3):
            conversation = self.chatbot(conversation)
            # print(conversation.messages)
            bot_response = conversation.messages[-1]["content"]
            bot_followup_response = self.sentences.followup_sentences[i]
            bot_response += " " + bot_followup_response
            conversation.messages[-1]["content"] = bot_response
            # print(conversation.messages)
            user_input = input("Bot: " + bot_response + "\nYou: ")
            conversation.add_message({"role": "user", "content": user_input})

            input_emotion_scores = self.classifier_pipeline(user_input)
            self.increment_scores(input_emotion_scores)

        print("Bot: " + random.choice(self.sentences.preferences_sentences))
        print("Please respond with Yes or No, and type in the names of the ingredients from the list that you are allergic to when I ask.")

        # Ask for allergies
        user_input = input("Bot: " + random.choice(self.sentences.ask_allergy_sentences) + "\nYou: ")
        for ingredient in self.allergy_ingredients:
            if ingredient in user_input.lower():
                allergies.append(ingredient)

        # Ask for vegan
        user_input = input("Bot: " + random.choice(self.sentences.ask_vegan_sentences) + "\nYou: ")
        if "yes" in user_input.lower():
            is_vegan = True

        # Ask for spicy
        user_input = input("Bot: " + random.choice(self.sentences.ask_spicy_sentences) + "\nYou: ")
        if "no" in user_input.lower():
            like_spicy = False


        print(f"Bot: I can see that you are feeling {self.get_highest_score()}.")

        # TODO: Get food recommendation


if __name__ == "__main__":
    while True:
        chatbot = IndianFoodChatbot()
        chatbot.chat()

        continue_chat = input("Would you like to start a new conversation? (Yes/No): ")
        if "no" in continue_chat.lower():
            break
        elif "yes" in continue_chat.lower():
            continue
        else:
            print("Invalid input. Exiting chatbot.")
            break
