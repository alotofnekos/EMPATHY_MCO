select distinct ingredients from recipe_ingredients;

UPDATE recipe_ingredients
SET ingredients = REPLACE(ingredients, 'red chili', 'red chilli')
WHERE ingredients = 'red chili';

UPDATE recipe_ingredients
SET ingredients = REPLACE(ingredients, 'fried milk power', 'fried milk powder')
WHERE ingredients = 'fried milk power';

#same thing
UPDATE recipe_ingredients
SET ingredients = REPLACE(ingredients, 'elachi', 'cardamom')
WHERE ingredients = 'elachi';

#same thing
UPDATE recipe_ingredients
SET ingredients = REPLACE(ingredients, 'yoghurt', 'yogurt')
WHERE ingredients = 'yoghurt';
