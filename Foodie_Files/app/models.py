from app import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"{self.username} (ID: {self.id})"
    
    # Our relationships with other classes
    recipes = db.relationship('Recipe', back_populates='author', cascade="all, delete-orphan")
    likes = db.relationship('Like', back_populates='user', cascade="all, delete-orphan")
    saved_recipes = db.relationship('SavedRecipe', back_populates='user', cascade="all, delete-orphan")

    # our users are unique but the primary key in our database. Eveything is based off them.
    # Classes cannot exist without them

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Key and Relationship to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', back_populates='recipes')
    
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))  # Optional, we can set a default picture if anythign 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    # Our relationships with other classes
    likes = db.relationship('Like', back_populates='recipe', cascade="all, delete-orphan")
    saved_by = db.relationship('SavedRecipe', back_populates='recipe', cascade="all, delete-orphan")
    # users can create multiple recipes showing off a one to many relationship
    

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # These are our Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    liked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Our relationships with other clas
    user = db.relationship('User', back_populates='likes')
    recipe = db.relationship('Recipe', back_populates='likes')
    # a post can have many likes 

class SavedRecipe(db.Model):
    __tablename__ = 'saved_recipes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Our relationships with other classes
    user = db.relationship('User', back_populates='saved_recipes')
    recipe = db.relationship('Recipe', back_populates='saved_by')

    # a single user can have many saved recipes

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User')
    recipe = db.relationship('Recipe')
    # a single user can comment on many posts same way a post can have many comments
