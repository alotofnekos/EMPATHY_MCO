import pandas as pd

# Load the datasets
indian_food_df = pd.read_csv("indian_food.csv")
good_ingredients_mood_df = pd.read_csv("ingredients_mood-good.csv")
bad_ingredients_mood_df = pd.read_csv("ingredients_mood-bad.csv")

def get_ingredients_based_on_mood(mood, positive=True):
    """
    Get a list of ingredients based on the mood.

    Parameters:
    - mood: The current mood of the user.
    - positive: If True, return ingredients positively associated with mood;
                if False, return ingredients negatively associated with mood.
    """
    if positive:
        relevant_ingredients = good_ingredients_mood_df.loc[good_ingredients_mood_df[mood] == 'y', 'ingredients']
    else:
        relevant_ingredients = bad_ingredients_mood_df.loc[bad_ingredients_mood_df[mood] == 'x', 'ingredients']
    return relevant_ingredients.tolist()

def recommend_dishes(mood, allergies, is_vegan, like_spicy):
    """
    Recommend top 3 dishes based on mood, allergies, vegan preference, and spicy preference.
    """
    # Pre-filter based on vegan and spicy preferences
    filtered_dishes = indian_food_df.copy()
    if is_vegan:
        filtered_dishes = filtered_dishes[filtered_dishes['diet'] == 'vegetarian']

    # Fetch positive mood ingredients
    positive_ingredients = get_ingredients_based_on_mood(mood)

    # Refine recommendations based on positive ingredients
    mood_filtered_dishes = filtered_dishes[filtered_dishes['ingredients'].apply(lambda x: any(ingredient in x for ingredient in positive_ingredients))]

    for allergen in allergies:  # Exclude based on allergies
        mood_filtered_dishes = mood_filtered_dishes[~mood_filtered_dishes['ingredients'].str.contains(allergen, case=False, regex=False)]

    if not like_spicy:
        mood_filtered_dishes = mood_filtered_dishes[~mood_filtered_dishes['flavor_profile'].str.contains("spicy", case=False)]

    # Select top 3 dishes satisfying all conditions
    # print(mood_filtered_dishes)
    top_recommendations = mood_filtered_dishes.head(3)

    if top_recommendations.empty:
        print("Sorry, we couldn't find any dishes matching all your preferences and mood.")
    else:
        for index, dish in top_recommendations.iterrows():
            print(f"- {dish['name']} from {dish['region']} region, which is a {dish['course']} dish.")

# Example call, using placeholders for mood and preferences
mood = "Sad"  # Placeholder for detected mood after conversation
allergies = ['milk', 'lactose', 'tree nuts', 'peanuts', 'egg']
is_vegan = False  # Placeholder for user preference
like_spicy = True  # Placeholder for user preference

recommend_dishes(mood, allergies, is_vegan, like_spicy)
