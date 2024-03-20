import pandas as pd

# Load the datasets
indian_food_df = pd.read_csv("indian_food.csv")
ingredients_mood_df = pd.read_csv("ingredients_mood-good.csv")
bad_ingredients_mood_df = pd.read_csv("ingredients_mood-bad.csv")

# Example to filter based on mood to get relevant ingredients
def get_ingredients_based_on_mood(mood):
    positive_ingredients = ingredients_mood_df.loc[:, ["ingredients", mood]].dropna()
    negative_ingredients = bad_ingredients_mood_df.loc[:, ["ingredients", mood]].dropna()
    # You can further filter based on the mood - for positive emotions, you might consider positive_ingredients and vice versa
    return positive_ingredients, negative_ingredients

def recommend_dishes(mood, allergies, is_vegan, like_spicy):
    # Get relevant ingredients for the mood
    positive_ingredients, negative_ingredients = get_ingredients_based_on_mood(mood)
    # Start with all dishes
    recommendations = indian_food_df.copy()

    # Exclude based on user restrictions
    if is_vegan:
        recommendations = recommendations[recommendations["diet"] == "vegetarian"]
    for allergen in allergies:
        recommendations = recommendations[~recommendations['ingredients'].str.contains(allergen, case=False)]
    if not like_spicy:
        recommendations = recommendations[~recommendations['flavor_profile'].str.contains("spicy", case=False)]

    # If there are positive ingredients based on mood, prioritize dishes containing them
    # (This is a simple implementation. For more accuracy, intersect the dishes with the positive ingredient list)

    final_recom = recommendations.sample(n=1)  # For simplicity, randomly pick one satisfying all conditions
    dish = final_recom.iloc[0]
    print(f"Based on your mood and preferences, I recommend trying {dish['name']} from {dish['region']} region, which is a {dish['course']} dish.")

# Example call, using placeholders for mood and preferences
mood = "Joy"  # Placeholder for detected mood after conversation
allergies = ['milk', 'lactose', 'tree nuts', 'peanuts', 'egg']
is_vegan = False  # Placeholder for user preference
like_spicy = True  # Placeholder for user preference

recommend_dishes(mood, allergies, is_vegan, like_spicy)
