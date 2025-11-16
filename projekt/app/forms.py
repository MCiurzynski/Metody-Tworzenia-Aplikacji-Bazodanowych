from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, Email, EqualTo, ValidationError
from app.db import db, User

class PersonForm(FlaskForm):
    first_name = StringField('Imię', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Nazwisko', validators=[DataRequired(), Length(min=2, max=100)])

    pesel = StringField('PESEL', validators=[
        DataRequired(), 
        Length(min=11, max=11), 
        Regexp(r'^\d{11}$', message="PESEL musi składać się z cyfr")
    ])
    
    phone_number = StringField('Telefon', validators=[
        DataRequired(),
        Length(min=9, max=15)
    ])

class RegistrationForm(PersonForm):
    username = StringField('Login', validators=[DataRequired(), Length(min=4, max=25)])
    email = EmailField('Email', validators=[DataRequired(), Email(message='Nieprawidłowy adres email')])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password', message='Musi być takie samo jak hasło')])

    def validate_username(self, username):
        user = db.session.execute(db.select(User).where(User.username == username.data)).scalar()
        if user:
            raise ValidationError('Ta nazwa użytkownika jest już zajęta.')

    def validate_email(self, email):
        user = db.session.execute(db.select(User).where(User.email == email.data)).scalar()
        if user:
            raise ValidationError('Ten email jest już zajęty.')

class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = StringField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')