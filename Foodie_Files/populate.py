from app import app, db
from app.models import User, Recipe
from datetime import datetime

# Create an application context
with app.app_context():
    # Fetch an existing user (replace 1 with the actual user ID in your database)
    existing_user = User.query.get(2)

    if not existing_user:
        print("No user found with ID 1. Please create a user first.")
    else:
        # Create a dummy recipe
        dummy_recipe = Recipe(
            user_id=existing_user.id,
            title="GUACAMOLE",
            description="A quick and creamy Italian pasta dish made with eggs, cheese, pancetta, and pepper.",
            ingredients="200g spaghetti, 100g pancetta, 2 large eggs, 50g Parmesan cheese, freshly ground black pepper, salt.",
            steps=(
                "1. Cook spaghetti in salted boiling water until al dente.\n"
                "2. Fry pancetta in a pan until crispy.\n"
                "3. Beat eggs and mix with grated Parmesan cheese.\n"
                "4. Drain pasta and mix with pancetta.\n"
                "5. Remove from heat and quickly mix in egg and cheese mixture.\n"
                "6. Serve immediately with extra cheese and black pepper."
            ),
            created_at=datetime.utcnow()
        )

        # Add and commit the recipe to the database
        db.session.add(dummy_recipe)
        db.session.commit()
        print("Dummy recipe added successfully!")
