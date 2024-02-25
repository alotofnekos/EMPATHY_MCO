CREATE TABLE Recipe (
    name VARCHAR(50) PRIMARY KEY,
    ingredients VARCHAR(2000),
    diet VARCHAR(20),
    prep_time INT,
    cook_time INT,
    flavor_profile VARCHAR(20),
    course VARCHAR(20),
    state VARCHAR(50),
    region VARCHAR(20)
);

CREATE TABLE recipe_ingredients AS WITH RECURSIVE cte_count (n,m) 
    AS (
		SELECT 1,3
           UNION ALL
           SELECT n + 1,n*n 
           FROM cte_count 
           WHERE n < 100
         )
     SELECT name, TRIM( BOTH FROM SUBSTRING_INDEX( SUBSTRING_INDEX(ingredients, ',', n) ,',',-1) )AS ingredients
     FROM recipe m
     JOIN cte_count cnt
     WHERE
     cnt.n <= LENGTH(ingredients) -LENGTH(REPLACE(m.ingredients,',','')) +1
     ;
