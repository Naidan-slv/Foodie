from app import app, models, db, admin
from flask import render_template, flash, request
from .forms import LoginForm, RegisterForm, NewRecipeForm
from flask_admin.contrib.sqla import ModelView
from .models import User, Recipe, SavedRecipe , Like, Comment

# we need to create a form for registering and to login
# we also need a form to create a new recipe
# import a class to login or something Assign your own class name and then assign a function
#  use ajax for the like button and for the saved thins. Users can like and unlike without reloading the page 

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Recipe, db.session))
admin.add_view(ModelView(SavedRecipe, db.session))
admin.add_view(ModelView(Like, db.session))
admin.add_view(ModelView(Comment, db.session))