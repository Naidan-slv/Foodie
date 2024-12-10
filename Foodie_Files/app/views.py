from app import app, models, db, admin
from flask import render_template, flash, request
from .forms import LoginForm, RegisterForm, NewRecipeForm
from flask_admin.contrib.sqla import ModelView
from wtforms_sqlalchemy.fields import QuerySelectField#
from flask_admin.form import Select2Widget
from .models import User, Recipe, SavedRecipe , Like, Comment

# we need to create a form for registering and to login
# we also need a form to create a new recipe
# import a class to login or something Assign your own class name and then assign a function
#  use ajax for the like button and for the saved thins. Users can like and unlike without reloading the page 
class RecipeAdmin(ModelView):
    # Override the form field for user_id to use a dropdown
    form_overrides = {
        'user_id': QuerySelectField
    }

    form_widget_args = {
        'user_id': {'widget': Select2Widget()}  # Use Select2 for better UI
    }

    # Define form_args to specify how the user_id field is populated
    form_args = {
        'user_id': {
            'query_factory': lambda: User.query.all(),
            'get_label': 'username',  # Replace 'username' with the field to display
        }
    }

admin.add_view(ModelView(User, db.session))
admin.add_view(RecipeAdmin(Recipe, db.session))
admin.add_view(ModelView(SavedRecipe, db.session))
admin.add_view(ModelView(Like, db.session))
admin.add_view(ModelView(Comment, db.session))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Handle login logic here
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Handle registration logic here
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    form = NewRecipeForm()
    if form.validate_on_submit():
        # Handle adding recipe logic here
        return redirect(url_for('index'))
    return render_template('new_recipe.html', form=form)