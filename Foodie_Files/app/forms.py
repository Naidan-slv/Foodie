from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# LoginForm: For user authentication
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# RegisterForm: For new user registration
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

# NewRecipeForm: For adding new recipes
class NewRecipeForm(FlaskForm):
    title = StringField('Recipe Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    steps = TextAreaField('Steps', validators=[DataRequired()])
    image = FileField('Recipe Image')  # Optional, can be handled separately in your Flask view
    submit = SubmitField('Add Recipe')
