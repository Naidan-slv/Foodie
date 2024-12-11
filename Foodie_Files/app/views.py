import os
from app import app, models, db, admin
from flask import render_template, flash, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from .models import User, Recipe, SavedRecipe, Like, Comment
from .forms import NewRecipeForm, LoginForm, RegisterForm


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if not authenticated
login_manager.login_message = "Please log in to access this page."

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Assumes user_id is the primary key of User model
# Flask-Admin Recipe Management

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Recipe, db.session))
admin.add_view(ModelView(SavedRecipe, db.session))
admin.add_view(ModelView(Like, db.session))
admin.add_view(ModelView(Comment, db.session))

###### HELPER FUNCTIONS ######
# Checks to see whether the file uploaded in add_recipes follows the right formatting
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def user_has_liked(user, recipe):
    """Check if the user has liked the recipe."""
    return any(like.user_id == user.id for like in recipe.likes)

def user_has_saved(user, recipe):
    """Check if the user has saved the recipe."""
    return any(save.user_id == user.id for save in recipe.saved_by)

@app.template_filter('has_liked')
def user_has_liked_filter(recipe, user):
    return user_has_liked(user, recipe)

@app.template_filter('has_saved')
def user_has_saved_filter(recipe, user):
    return user_has_saved(user, recipe)


# Index Route
@app.route('/')
def index():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template('index.html', recipes=recipes)


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('You have successfully logged in.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if the email or username already exists
        existing_user = User.query.filter((User.email == form.email.data) | (User.username == form.username.data)).first()
        if existing_user:
            flash('Email or username is already registered.', 'danger')
            return redirect(url_for('register'))
        
        # If the email and username are unique, proceed with registration
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html', form=form)


# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# Add Recipe Route
@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = NewRecipeForm()
    if form.validate_on_submit():
        # Create the new recipe object
        new_recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            ingredients=form.ingredients.data,
            steps=form.steps.data,
            user_id=current_user.id
        )
        if form.image.data:
            # Validate and save the uploaded image
            filename = secure_filename(form.image.data.filename)
            if allowed_file(filename):
                filepath = os.path.join('app/static/uploads', filename)
                form.image.data.save(filepath)
                new_recipe.image_url = f'app/static/uploads/{filename}'
            else:
                flash('Invalid file type. Please upload an image file (png, jpg, jpeg, gif).', 'danger')
                return redirect(request.url)

        try:
            # Save the recipe to the database
            db.session.add(new_recipe)
            db.session.commit()
            flash('Recipe added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while adding the recipe: {str(e)}', 'danger')

    return render_template('add_recipe.html', form=form)

@app.route('/view_recipes')
def view_recipes():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template('view_recipes.html', recipes=recipes)


@app.route('/my_recipes', methods=['GET'])
@login_required
def my_recipes():
    # Fetch recipes created by the logged-in user
    recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.created_at.desc()).all()
    return render_template('my_recipes.html', recipes=recipes)

@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        flash('You are not authorized to edit this recipe.', 'danger')
        return redirect(url_for('my_recipes'))
    
    form = NewRecipeForm(obj=recipe)  # Pre-fill the form with the current recipe data
    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.ingredients = form.ingredients.data
        recipe.steps = form.steps.data
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join('app/static/uploads', filename)
            form.image.data.save(filepath)
            recipe.image_url = f'/static/uploads/{filename}'
        
        try:
            db.session.commit()
            flash('Recipe updated successfully!', 'success')
            return redirect(url_for('my_recipes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating recipe: {str(e)}', 'danger')
    
    return render_template('edit_recipe.html', form=form)

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST', 'GET'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        flash('You are not authorized to delete this recipe.', 'danger')
        return redirect(url_for('my_recipes'))

    try:
        db.session.delete(recipe)
        db.session.commit()
        flash(f'Recipe "{recipe.title}" has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting recipe: {str(e)}', 'danger')

    return redirect(url_for('my_recipes'))


@app.route('/like_recipe', methods=['POST'])
@login_required
def like_recipe():
    data = request.get_json()
    recipe_id = data.get('recipe_id')
    recipe = Recipe.query.get_or_404(recipe_id)

    # Check if the user has already liked the recipe
    existing_like = Like.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
    if existing_like:
        # Unlike the recipe
        db.session.delete(existing_like)
        db.session.commit()
        like_count = len(recipe.likes)  # Updated likes count
        return jsonify({'status': 'unliked', 'like_count': like_count})
    
    # Like the recipe
    new_like = Like(user_id=current_user.id, recipe_id=recipe.id)
    db.session.add(new_like)
    db.session.commit()
    like_count = len(recipe.likes)  # Updated likes count
    return jsonify({'status': 'liked', 'like_count': like_count})


@app.route('/save_recipe', methods=['POST'])
@login_required
def save_recipe():
    data = request.get_json()
    recipe_id = data.get('recipe_id')
    recipe = Recipe.query.get_or_404(recipe_id)

    # Check if the user has already saved the recipe
    existing_save = SavedRecipe.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
    if existing_save:
        # Remove from saved recipes
        db.session.delete(existing_save)
        db.session.commit()
        return jsonify({'status': 'unsaved'})

    # Save the recipe
    new_save = SavedRecipe(user_id=current_user.id, recipe_id=recipe.id)
    db.session.add(new_save)
    db.session.commit()
    return jsonify({'status': 'saved'})



# AJAX Like/Unlike Route
# @app.route('/like/<int:recipe_id>', methods=['POST'])
# @login_required
# def like_recipe(recipe_id):
#     recipe = Recipe.query.get_or_404(recipe_id)
#     like = Like.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()

#     if like:
#         db.session.delete(like)
#         db.session.commit()
#         return jsonify({'status': 'unliked', 'like_count': len(recipe.likes)})

#     new_like = Like(user_id=current_user.id, recipe_id=recipe_id)
#     db.session.add(new_like)
#     db.session.commit()
#     return jsonify({'status': 'liked', 'like_count': len(recipe.likes)})
