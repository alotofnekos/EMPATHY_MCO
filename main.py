# https://huggingface.co/docs/transformers/v4.37.2/en/main_classes/pipelines


import random
import warnings

import pandas as pd
from transformers import Conversation, pipeline
from transformers.utils import logging

import recommender
import sentences

import tkinter as tk
from tkinter import scrolledtext, Entry, Button, StringVar

import pandas as pd
import ast

warnings.filterwarnings("ignore")
logging.set_verbosity_error()


class IndianFoodChatbot:

    def __init__(self, gui, recommender):
        self.classifier_pipeline = pipeline(task="text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
        self.chatbot = pipeline(task="conversational", model="microsoft/DialoGPT-medium")
        self.gui = gui
        self.recommender = recommender
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

    def display_message(self, message):
        if self.gui:
            self.gui.display_bot_message(message)
            
    def submit_message(self):
        if self.gui:
            return self.gui.submit_message()
        return False

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

        #self.gui.root.mainloop()
        conversation = Conversation()
        bot_random_response = random.choice(self.sentences.intro_sentences)
        conversation.add_message({"role": "assistant", "content": bot_random_response})
        #user_input = input("Bot: " + bot_random_response + "\nYou: ")
        self.display_message(bot_random_response)
        print(bot_random_response)
        user_input = self.submit_message()
        conversation.add_message({"role": "user", "content": user_input})

        input_emotion_scores = self.classifier_pipeline(user_input)
        self.increment_scores(input_emotion_scores)

        ### CONVERSATION LOOP
        for i in range(3):
            conversation = self.chatbot(conversation)
            bot_response = conversation.messages[-1]["content"]
            bot_followup_response = self.sentences.followup_sentences[i]
            bot_response += " " + bot_followup_response
            # conversation.messages[-1]["content"] = bot_response
            #user_input = input("Bot: " + bot_response + "\nYou: ")
            self.display_message(bot_response)
            user_input = self.submit_message()
            conversation.add_message({"role": "user", "content": user_input})

            input_emotion_scores = self.classifier_pipeline(user_input)
            self.increment_scores(input_emotion_scores)

        #print("Bot: " + random.choice(self.sentences.preferences_sentences))
        self.display_message(random.choice(self.sentences.preferences_sentences))

        # Ask for allergies
        #print("Bot: " + random.choice(self.sentences.ask_allergy_sentences))
        self.display_message(random.choice(self.sentences.ask_allergy_sentences))
        #print("Please type in the names of the ingredients from the list that you are allergic to. If you are not allergic to any of these, type 'None' or leave it blank.")
        self.display_message("\nPlease type in the names of the ingredients from the list that you are allergic to. If you are not allergic to any of these, type 'None' or leave it blank.")
        #user_input = input("You: ")
        user_input = self.submit_message()
        for ingredient in self.allergy_ingredients:
            if ingredient in user_input.lower():
                allergies.append(ingredient)
        

        # Ask for vegan
        #print("Bot: " + random.choice(self.sentences.ask_vegan_sentences))
        self.display_message(random.choice(self.sentences.ask_vegan_sentences))
        #print("Please respond with Yes or No.")
        self.display_message("Please respond with Yes or No.")
        #user_input = input("You: ")
        user_input = self.submit_message()
        if "yes" in user_input.lower():
            is_vegan = True
        # print(is_vegan)

        # Ask for spicy
        #print("Bot: " + random.choice(self.sentences.ask_spicy_sentences))
        self.display_message(random.choice(self.sentences.ask_spicy_sentences))
        #print("Please respond with Yes or No.")
        self.display_message("Please respond with Yes or No.")
        #user_input = input("You: ")
        user_input = self.submit_message()
        if "no" in user_input.lower():
            like_spicy = False
        # print(like_spicy)


        #print(f"Bot: Overall, I can see that you are feeling {self.get_highest_score()}.")
        msg = "Overall, I can see that you are feeling " + str(self.get_highest_score()) + "."
        self.display_message(msg)

        # TODO: Get food recommendation
        self.recommender.recommend_dishes(self.get_highest_score().title(), allergies, is_vegan, like_spicy)


class ChatbotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Indian Food Chatbot")

        self.chat_history = scrolledtext.ScrolledText(self.root, state='disabled', height=15, width=50)
        self.chat_history.pack(padx=10, pady=10)

        self.user_input = StringVar()
        self.entry_field = Entry(self.root, textvariable=self.user_input)
        self.entry_field.pack(padx=10, pady=10)

        self.submit_button = Button(self.root, text="Send", command=self.submit_message)
        self.submit_button.pack(padx=10, pady=10)

    def display_bot_message(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, "Bot: " + message + "\n")
        self.chat_history.config(state='disabled')

    def submit_message(self):
        user_input = self.user_input.get()
        if user_input:
            self.chat_history.config(state='normal')
            self.chat_history.insert(tk.END, "You: " + user_input + "\n")
            self.chat_history.config(state='disabled')
            self.user_input.set("")

        return user_input

class Recommender:
    def __init__(self, gui):
        self.indian_food_df = pd.read_csv("indian_food.csv")
        self.good_ingredients_mood_df = pd.read_csv("ingredients_mood-good.csv")
        self.bad_ingredients_mood_df = pd.read_csv("ingredients_mood-bad.csv")
        self.allergen_df = pd.read_csv("allergen.csv")
        self.allergen_df['allergens'] = self.allergen_df['allergens'].apply(ast.literal_eval)
        self.gui = gui

    def display_message(self, message):
        if self.gui:
            self.gui.display_bot_message(message)
            
    def submit_message(self):
        if self.gui:
            return self.gui.submit_message()
        return False
    
    # Example to filter based on mood to get relevant ingredients
    def get_dishes_based_on_mood(self, mood):
        # Make empty dataframes for positive and negative dishes
        positive_dishes = pd.DataFrame(columns=self.indian_food_df.columns)
        negative_dishes = pd.DataFrame(columns=self.indian_food_df.columns)

        # Get all ingredients that have a non NaN value in the respective mood column
        positive_ingredients = self.good_ingredients_mood_df[
            self.good_ingredients_mood_df[mood].notna()
        ]
        negative_ingredients = self.bad_ingredients_mood_df[
            self.bad_ingredients_mood_df[mood].notna()
        ]

        # Get dishes to recommend from the positive_ingredients df based on the mood
        for index, row in self.indian_food_df.iterrows():
            for ingredient in positive_ingredients["ingredients"]:
                if ingredient.lower() in row["ingredients"].lower():
                    positive_dishes = pd.concat(
                        [
                            positive_dishes,
                            self.indian_food_df[self.indian_food_df["name"] == row["name"]],
                        ]
                    )
            for ingredient in negative_ingredients["ingredients"]:
                if ingredient.lower() in row["ingredients"].lower():
                    negative_dishes = pd.concat(
                        [
                            positive_dishes,
                            self.indian_food_df[self.indian_food_df["name"] == row["name"]],
                        ]
                    )

        # Remove duplicate rows in both dataframes
        positive_dishes = positive_dishes.drop_duplicates()
        negative_dishes = negative_dishes.drop_duplicates()

        return positive_dishes, negative_dishes
    
    # Given a dataframe of dishes, filter out dishes that contain ingredients correlated to the allergens
    def filter_dishes_by_allergens(self, dishes, allergies, get_good_dishes=True):
        bad_ingredients = []

        for index, row in self.allergen_df.iterrows():
            if row['allergens'] != []:
                for allergen in row['allergens']:
                    if allergen in allergies:
                        bad_ingredients.append(row['ingredients'])
                        continue

        # Drop duplicates from bad ingredients
        bad_ingredients = list(set(bad_ingredients))

        # Given the bad ingredients, filter the dishes to remove dishes that contain any of the bad ingredients
        filtered_dishes = pd.DataFrame(columns=dishes.columns)
        for index, row in dishes.iterrows():
            # Terrible implementation but it is what it is 
            common_ingredients = [i for i in bad_ingredients if i in row["ingredients"].split(", ")]
            if common_ingredients == [] and get_good_dishes:
                filtered_dishes = pd.concat([filtered_dishes, dishes[dishes["name"] == row["name"]]])
            elif not get_good_dishes:
                filtered_dishes = pd.concat([filtered_dishes, dishes[dishes["name"] == row["name"]]])
        
        return filtered_dishes
    
    def recommend_dishes(self, mood, allergies, is_vegan, like_spicy):
        # Get relevant ingredients for the mood
        positive_dishes, negative_dishes = self.get_dishes_based_on_mood(mood)
        positive_ingredients = self.good_ingredients_mood_df[self.good_ingredients_mood_df[mood].notna()]
        negative_ingredients = self.bad_ingredients_mood_df[self.bad_ingredients_mood_df[mood].notna()]

        # print(f"before filter: {negative_dishes}")

        # Exclude based on user restrictions
        if is_vegan:
            positive_dishes = positive_dishes[positive_dishes["diet"] == "vegetarian"]
        # for allergen in allergies:
        #     positive_dishes = positive_dishes[~positive_dishes['ingredients'].str.contains(allergen, case=False)]
        if allergies:
            positive_dishes = self.filter_dishes_by_allergens(positive_dishes, allergies, get_good_dishes=True)
        if not like_spicy:
            positive_dishes = positive_dishes[~positive_dishes['flavor_profile'].str.contains("spicy", case=False)]

        if mood.lower() != "joy" and mood.lower() != "neutral":
            if is_vegan:
                negative_dishes = negative_dishes[negative_dishes["diet"] == "non vegetarian"]
            # if allergies:
            #     allergen_mask = pd.Series(False, index=negative_dishes.index)
            #     for allergen in allergies:
            #         # This updates the mask to True for any row where the allergen is found
            #         allergen_mask |= negative_dishes['ingredients'].str.contains(allergen, case=False)
            #     negative_dishes = negative_dishes[allergen_mask]
            if allergies:
                negative_dishes = self.filter_dishes_by_allergens(negative_dishes, allergies, get_good_dishes=False)
            if not like_spicy:
                negative_dishes = negative_dishes[negative_dishes['flavor_profile'].str.contains("spicy", case=False)]

        final_recom = positive_dishes.sample(n=3)  # For simplicity, randomly pick three satisfying all conditions
        # final_recom = positive_dishes.head(3)

        # print(f"after filter: {negative_dishes}")
        # FIXME: Some checks here that are present in recommender.py are missing here
        if mood.lower() != "joy" and mood.lower() != "neutral":
            negative_dishes_empty = negative_dishes.empty
            avoid_recom = pd.DataFrame()
            if not negative_dishes_empty:
                avoid_recom = negative_dishes.sample(n=3)  # For simplicity, randomly pick three satisfying all conditions

        # Check if final_recom is empty
        if final_recom.empty:
            #print("Sorry, I couldn't find any dishes satisfying your preferences and restrictions.")
            self.display_message("Sorry, I couldn't find any dishes satisfying your preferences and restrictions.")
        else:
            print(f"Based on your mood and preferences, I recommend trying the following dishes: ")
            self.display_message("Based on your mood and preferences, I recommend trying the following dishes: ")
            for index, row in final_recom.iterrows():
                region_string = ""
                state_string = ""
                flavor_string = ""
                if row['region'] != "-1":
                    region_string = f" of the {row['region']} region"
                if row['state'] != "-1":
                    state_string = f" from the {row['state']} state"
                # print(type(row['flavor_profile']))
                if row['flavor_profile'] != "-1":
                    flavor_string = f" is a {row['flavor_profile']} dish and"
                msg = f"{row['name']}{state_string}{region_string}, which is a {row['course']} dish."
                self.display_message(msg)
                msg = f"{row['name']}{flavor_string} is {row['diet']}."
                self.display_message(msg)
                msg = f"{row['name']} contains the ingredients {row['ingredients']}."
                self.display_message(msg)
                for ingredient in row['ingredients'].split(","):
                    # print(ingredient)
                    ingredient = ingredient.strip()
                    # print(positive_ingredients)
                    # FIXME: Check if ingredient is really missing from positive_ingredients["ingredients"] or it's just a difference in capitalization
                    # FIXME: If it's the former, then why is it missing if we got our recommendation based on the ingredients?
                    if ingredient in positive_ingredients["ingredients"].values:
                        # print(positive_ingredients.loc[positive_ingredients['ingredients'] == ingredient, "Y Reason"].iloc[0])
                        ingredient_reason = positive_ingredients.loc[positive_ingredients['ingredients'] == ingredient, "Y Reason"].iloc[0]
                        # print(ingredient_reason)
                        if isinstance(ingredient_reason, str):
                            self.display_message("  " + ingredient_reason)


        if mood.lower() != "joy" and mood.lower() != "neutral":
            # Check if avoid_recom is empty
            if negative_dishes_empty:
                # print("I couldn't find any dishes that you should avoid.")
                pass
            else:
                self.display_message(f"Based on your mood and preferences, I recommend avoiding the following dishes: ")

                for index, row in avoid_recom.iterrows():
                    region_string = ""
                    state_string = ""
                    flavor_string = ""
                    if row['region'] != "-1":
                        region_string = f" of the {row['region']} region"
                    if row['state'] != "-1":
                        state_string = f" from the {row['state']} state"
                    # print(type(row['flavor_profile']))
                    if row['flavor_profile'] != "-1":
                        flavor_string = f" is a {row['flavor_profile']} dish and"
                    self.display_message(f"{row['name']}{state_string}{region_string}, which is a {row['course']} dish.")
                    self.display_message(f"{row['name']}{flavor_string} is {row['diet']}.")
                    self.display_message(f"{row['name']} contains the ingredients {row['ingredients']}.")
                    for ingredient in row['ingredients'].split(","):
                        # print(ingredient)
                        ingredient = ingredient.strip()
                        # print(negative_ingredients)
                        if ingredient in negative_ingredients["ingredients"].values:
                            # print(negative_ingredients.loc[negative_ingredients['ingredients'] == ingredient, "N Reason"].iloc[0])
                            ingredient_reason = negative_ingredients.loc[negative_ingredients['ingredients'] == ingredient, "X Reason"].iloc[0]
                            # print(ingredient_reason)
                            if isinstance(ingredient_reason, str):
                                self.display_message("  " + ingredient_reason)

        self.display_message("Hope you enjoy these dishes once you try them!")


if __name__ == "__main__":
    while True:
        gui = ChatbotGUI()
        recommender = Recommender(gui)
        chatbot = IndianFoodChatbot(gui, recommender)
        gui.display_bot_message("hoy")
        chatbot.chat()

        gui.display_bot_message("Would you like to start a new conversation? (Yes/No): ")
        continue_chat = gui.submit_message()

        if "no" in continue_chat.lower():
            break
        elif "yes" in continue_chat.lower():
            continue
        else:
            print("Invalid input. Exiting chatbot.")
            break
