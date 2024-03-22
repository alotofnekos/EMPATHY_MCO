import pandas as pd
import ast

# Load the datasets
indian_food_df = pd.read_csv("indian_food.csv")
good_ingredients_mood_df = pd.read_csv("ingredients_mood-good.csv")
bad_ingredients_mood_df = pd.read_csv("ingredients_mood-bad.csv")
allergen_df = pd.read_csv("allergen.csv")

# Fixing allergen_df
allergen_df['allergens'] = allergen_df['allergens'].apply(ast.literal_eval)


# Example to filter based on mood to get relevant ingredients
def get_dishes_based_on_mood(mood):
    # Make empty dataframes for positive and negative dishes
    positive_dishes = pd.DataFrame(columns=indian_food_df.columns)
    negative_dishes = pd.DataFrame(columns=indian_food_df.columns)

    # Get all ingredients that have a non NaN value in the respective mood column
    positive_ingredients = good_ingredients_mood_df[
        good_ingredients_mood_df[mood].notna()
    ]
    negative_ingredients = bad_ingredients_mood_df[
        bad_ingredients_mood_df[mood].notna()
    ]

    # Get dishes to recommend from the positive_ingredients df based on the mood
    for index, row in indian_food_df.iterrows():
        for ingredient in positive_ingredients["ingredients"]:
            if ingredient.lower() in row["ingredients"].lower():
                positive_dishes = pd.concat(
                    [
                        positive_dishes,
                        indian_food_df[indian_food_df["name"] == row["name"]],
                    ]
                )
        for ingredient in negative_ingredients["ingredients"]:
            if ingredient.lower() in row["ingredients"].lower():
                negative_dishes = pd.concat(
                    [
                        positive_dishes,
                        indian_food_df[indian_food_df["name"] == row["name"]],
                    ]
                )

    # Remove duplicate rows in both dataframes
    positive_dishes = positive_dishes.drop_duplicates()
    negative_dishes = negative_dishes.drop_duplicates()

    return positive_dishes, negative_dishes

# Given a dataframe of dishes, filter out dishes that contain ingredients correlated to the allergens
def filter_dishes_by_allergens(dishes, allergies, get_good_dishes=True):
    bad_ingredients = []

    for index, row in allergen_df.iterrows():
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

def recommend_dishes(mood, allergies, is_vegan, like_spicy):
    # Get relevant ingredients for the mood
    positive_dishes, negative_dishes = get_dishes_based_on_mood(mood)
    positive_ingredients = good_ingredients_mood_df[good_ingredients_mood_df[mood].notna()]
    negative_ingredients = bad_ingredients_mood_df[bad_ingredients_mood_df[mood].notna()]

    # print(f"before filter: {negative_dishes}")

    # Exclude based on user restrictions
    if is_vegan:
        positive_dishes = positive_dishes[positive_dishes["diet"] == "vegetarian"]
    # for allergen in allergies:
    #     positive_dishes = positive_dishes[~positive_dishes['ingredients'].str.contains(allergen, case=False)]
    if allergies:
        positive_dishes = filter_dishes_by_allergens(positive_dishes, allergies, get_good_dishes=True)
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
            negative_dishes = filter_dishes_by_allergens(negative_dishes, allergies, get_good_dishes=False)
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
                        print("  " + ingredient_reason)

    if mood.lower() != "joy" and mood.lower() != "neutral":
        # Check if avoid_recom is empty
        if negative_dishes_empty:
            # print("I couldn't find any dishes that you should avoid.")
            pass
        else:
            print(f"Based on your mood and preferences, I recommend avoiding the following dishes: ")
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
                print(f"{row['name']}{state_string}{region_string}, which is a {row['course']} dish.")
                print(f"{row['name']}{flavor_string} is {row['diet']}.")
                print(f"{row['name']} contains the ingredients {row['ingredients']}.")
                for ingredient in row['ingredients'].split(","):
                    # print(ingredient)
                    ingredient = ingredient.strip()
                    # print(negative_ingredients)
                    if ingredient in negative_ingredients["ingredients"].values:
                        # print(negative_ingredients.loc[negative_ingredients['ingredients'] == ingredient, "N Reason"].iloc[0])
                        ingredient_reason = negative_ingredients.loc[negative_ingredients['ingredients'] == ingredient, "X Reason"].iloc[0]
                        # print(ingredient_reason)
                        if isinstance(ingredient_reason, str):
                            print("  " + ingredient_reason)

    print("Hope you enjoy these dishes once you try them!")


# Example call, using placeholders for mood and preferences
if __name__ == "__main__":
    mood = "Sad"  # Placeholder for detected mood after conversation
    allergies = ["milk", "lactose", "tree nuts", "peanuts", "egg"]
    is_vegan = False  # Placeholder for user preference
    like_spicy = True  # Placeholder for user preference

    recommend_dishes(mood, allergies, is_vegan, like_spicy)
