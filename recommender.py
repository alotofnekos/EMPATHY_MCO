import pandas as pd

# Load the datasets
indian_food_df = pd.read_csv("indian_food.csv")
good_ingredients_mood_df = pd.read_csv("ingredients_mood-good.csv")
bad_ingredients_mood_df = pd.read_csv("ingredients_mood-bad.csv")

# Example to filter based on mood to get relevant ingredients
def get_dishes_based_on_mood(mood):
    # Make empty dataframes for positive and negative dishes
    positive_dishes = pd.DataFrame(columns=indian_food_df.columns)
    negative_dishes = pd.DataFrame(columns=indian_food_df.columns)

    # Get all ingredients that have a non NaN value in the respective mood column
    positive_ingredients = good_ingredients_mood_df[good_ingredients_mood_df[mood].notna()]
    negative_ingredients = bad_ingredients_mood_df[bad_ingredients_mood_df[mood].notna()]

    # Get dishes to recommend from the positive_ingredients df based on the mood
    for index, row in indian_food_df.iterrows():
        for ingredient in positive_ingredients["ingredients"]:
            if ingredient.lower() in row["ingredients"].lower():
                positive_dishes = pd.concat([positive_dishes, indian_food_df[indian_food_df["name"] == row["name"]]])
        for ingredient in negative_ingredients["ingredients"]:
            if ingredient.lower() in row["ingredients"].lower():
                negative_dishes = pd.concat([positive_dishes, indian_food_df[indian_food_df["name"] == row["name"]]])

    # Remove duplicate rows in both dataframes
    positive_dishes = positive_dishes.drop_duplicates()
    negative_dishes = negative_dishes.drop_duplicates()

    return positive_dishes, negative_dishes


def recommend_dishes(mood, allergies, is_vegan, like_spicy):
    # Get relevant ingredients for the mood
    positive_dishes, negative_dishes = get_dishes_based_on_mood(mood)
    positive_ingredients = good_ingredients_mood_df[good_ingredients_mood_df[mood].notna()]
    negative_ingredients = bad_ingredients_mood_df[bad_ingredients_mood_df[mood].notna()]

    # Exclude based on user restrictions
    if is_vegan:
        positive_dishes = positive_dishes[positive_dishes["diet"] == "vegetarian"]
    for allergen in allergies:
        positive_dishes = positive_dishes[~positive_dishes['ingredients'].str.contains(allergen, case=False)]
    if not like_spicy:
        positive_dishes = positive_dishes[~positive_dishes['flavor_profile'].str.contains("spicy", case=False)]

    # print(positive_dishes)
    final_recom = positive_dishes.sample(n=3)  # For simplicity, randomly pick three satisfying all conditions

    # Check if final_recom is empty
    if final_recom.empty:
        print("Sorry, I couldn't find any dishes satisfying your preferences and restrictions.")
    else:
        print(f"Based on your mood and preferences, I recommend trying the following dishes: ")
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
            print(f"{row['name']}{state_string}{region_string}, which is a {row['course']} dish.")
            print(f"{row['name']}{flavor_string} is {row['diet']}.")
            print(f"{row['name']} contains the ingredients {row['ingredients']}.")
            for ingredient in row['ingredients'].split(","):
                ingredient = ingredient.strip()
                if ingredient in positive_ingredients["ingredients"].values:
                    ingredient_reason = positive_ingredients.loc[positive_ingredients['ingredients'] == ingredient, "Y Reason"].iloc[0]
                    if isinstance(ingredient_reason, str):
                        print("  " + ingredient_reason)
    print("Hope you enjoy these dishes once you try them!")


# Example call, using placeholders for mood and preferences
if __name__ == "__main__":
    mood = "Sad"  # Placeholder for detected mood after conversation
    allergies = ['milk', 'lactose', 'tree nuts', 'peanuts', 'egg']
    is_vegan = False  # Placeholder for user preference
    like_spicy = True  # Placeholder for user preference

    recommend_dishes(mood, allergies, is_vegan, like_spicy)
