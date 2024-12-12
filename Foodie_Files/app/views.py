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
login_manager.login_view = 'Login'  
# Here we redirect to the login page if not authenticated
login_manager.login_message = "Please log in to access this page."

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  
# Flask-Admin Recipe Management

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Recipe, db.session))
admin.add_view(ModelView(SavedRecipe, db.session))
admin.add_view(ModelView(Like, db.session))
admin.add_view(ModelView(Comment, db.session))

###### HELPER FUNCTIONS ######
# Check to see whether the file uploaded in add_recipes follows the right formatting
# Check if the user has liked or saved any posts so we know what to display 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def user_has_liked(user, recipe):
    return any(like.user_id == user.id for like in recipe.likes)

def user_has_saved(user, recipe):
    return any(save.user_id == user.id for save in recipe.saved_by)

@app.template_filter('has_liked')
def user_has_liked_filter(recipe, user):
    return user_has_liked(user, recipe)

@app.template_filter('has_saved')
def user_has_saved_filter(recipe, user):
    return user_has_saved(user, recipe)


# This is our Home page
@app.route('/')
def index():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template('index.html', recipes=recipes)


# Here is where we login
# Only display certain pages if not logged in and limit what they can do
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('User is now logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password try again .', 'danger')
    return render_template('login.html', form=form)


# Register Route
# When creating a new password verify they are the same by having them write it out twice
# We also encrypt the users password using werkzeug
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email or username already exist to ensure theyre unique
        existing_user = User.query.filter((User.email == form.email.data) | (User.username == form.username.data)).first()
        if existing_user:
            flash('The Username or Email are already registered', 'danger')
            return redirect(url_for('register'))
        
        # If email and username are unique, proceed with registration
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account Registrated Please login : ', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html', form=form)


# Can only LOGOUT if logged in 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out ', 'info')
    return redirect(url_for('login'))


# Add Recipe Route
@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = NewRecipeForm()
    if form.validate_on_submit():
        # Create the new recipe object by calling it 
        new_recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            ingredients=form.ingredients.data,
            steps=form.steps.data,
            user_id=current_user.id
        )
        if form.image.data:
            # validate and save the image
            filename = secure_filename(form.image.data.filename)
            if allowed_file(filename):
                filepath = os.path.join('app/static/uploads', filename)
                form.image.data.save(filepath)
                new_recipe.image_url = f'app/static/uploads/{filename}'
            else:
                flash('Invalid file type. Please upload an image file (png, jpg, jpeg, gif).', 'danger')
                return redirect(request.url)

        try:
            # save the recipe to the database
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
    # Look for the recipes created by the logged-in user
    recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.created_at.desc()).all()
    return render_template('my_recipes.html', recipes=recipes)

@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        flash('You are not authorised to edit this recipe.', 'danger')
        return redirect(url_for('my_recipes'))
    
    # Pre-fill the form with the current recipe data
    form = NewRecipeForm(obj=recipe) 
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
            flash('Recipe updated successfully ', 'success')
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
        flash('You are not authorised to delete this recipe.', 'danger')
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

    # Checking if the user has liked the recipe
    existing_like = Like.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
    if existing_like:
        # Unlike the recipe
        db.session.delete(existing_like)
        db.session.commit()
        like_count = len(recipe.likes)  # Updated likes count
        return jsonify({'status': 'unliked', 'like_count': like_count})
    
    # If they have liked the recipe
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

    #check if the user has already saved the recipe
    existing_save = SavedRecipe.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
    if existing_save:
        # Remove from saved recipes
        db.session.delete(existing_save)
        db.session.commit()
        return jsonify({'status': 'unsaved'})

    # save the recipe
    new_save = SavedRecipe(user_id=current_user.id, recipe_id=recipe.id)
    db.session.add(new_save)
    db.session.commit()
    return jsonify({'status': 'saved'})

@app.route('/saved_recipes', methods=['GET'])
@login_required
def saved_recipes():
    # get the recipes saved by the current user
    saved_recipes = Recipe.query.join(SavedRecipe, Recipe.id == SavedRecipe.recipe_id) \
                                .filter(SavedRecipe.user_id == current_user.id).all()
    return render_template('saved_recipes.html', saved_recipes=saved_recipes)

@app.route('/get_recipe_details', methods=['GET'])
def get_recipe_details():
    recipe_id = request.args.get('recipe_id', type=int)
    recipe = Recipe.query.get_or_404(recipe_id)

    # fetch comments and serialize them
    comments_data = []
    comments = Comment.query.filter_by(recipe_id=recipe_id).order_by(Comment.created_at.asc()).all()
    for c in comments:
        comments_data.append({
            'author': c.user.username,
            'content': c.content,
            'created_at': c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    recipe_data = {
        'title': recipe.title,
        'author': recipe.author.username,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'steps': recipe.steps,
        'image_url': recipe.image_url,
        'comments': comments_data
    }

    return jsonify(recipe_data)

@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    data = request.get_json()
    recipe_id = data.get('recipe_id')
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'status': 'error', 'message': 'Comment content cannot be empty.'}), 400
    
    recipe = Recipe.query.get_or_404(recipe_id)

    # Create the new comment
    new_comment = Comment(user_id=current_user.id, recipe_id=recipe_id, content=content)
    db.session.add(new_comment)
    db.session.commit()

    # Return updated comments
    comments_data = []
    comments = Comment.query.filter_by(recipe_id=recipe_id).order_by(Comment.created_at.asc()).all()
    for c in comments:
        comments_data.append({
            'author': c.user.username,
            'content': c.content,
            'created_at': c.created_at.strftime("%Y-%m-%d")
        })

    return jsonify({'status': 'success', 'comments': comments_data})

@app.route('/filter_recipes', methods=['GET'])
def filter_recipes():
    sort_option = request.args.get('sort', 'all')
    search_query = request.args.get('q', '').strip()
    
    query = Recipe.query
    
    # Filter by search query
    if search_query:
        query = query.filter(
            (Recipe.title.ilike(f"%{search_query}%")) |
            (Recipe.description.ilike(f"%{search_query}%"))
        )

    # Sorting
    if sort_option == 'liked':
        query = query.outerjoin(Like).group_by(Recipe.id).order_by(db.func.count(Like.id).desc())
    elif sort_option == 'saved':
        query = query.outerjoin(SavedRecipe).group_by(Recipe.id).order_by(db.func.count(SavedRecipe.id).desc())
    elif sort_option == 'recent':
        query = query.order_by(Recipe.created_at.desc())
    else:
        query = query.order_by(Recipe.id.asc())

    recipes = query.all()

    recipe_data = []
    for r in recipes:
        user_liked = False
        user_saved = False
        if current_user.is_authenticated:
            user_liked = any(l.user_id == current_user.id for l in r.likes)
            user_saved = any(s.user_id == current_user.id for s in r.saved_by)

        recipe_data.append({
            'id': r.id,
            'title': r.title,
            'author': r.author.username,
            'like_count': len(r.likes),  # Include like_count
            'user_liked': user_liked,
            'user_saved': user_saved
        })

    return jsonify(recipe_data)





