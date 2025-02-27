"""
This module contains flask forms for html templates
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    StringField,
    SubmitField,
    PasswordField,
)
from wtforms.validators import DataRequired, Length

# WTForm


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    lastname = StringField("Last Name")
    desc = StringField("Description")
    password = PasswordField("Password", validators=[DataRequired(), Length(8)])
    submit = SubmitField("Register")


class PlaceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    desc = StringField("Description")
    submit = SubmitField("Add")


class SensorForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    desc = StringField("Description")
    conf = StringField("Configuration")
    submit = SubmitField("Add")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Enter")


class PersonalForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    lastname = StringField("Last Name")
    desc = StringField("Description")
    old_password = PasswordField(
        "Old Password (leave it blank if you don't need to change)"
    )
    new_password = PasswordField("New Password")
    submit = SubmitField("Save")


class PersonalFormAdmin(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    lastname = StringField("Last Name")
    access = BooleanField("Read Access")
    submit = SubmitField("Save")


class NewPassForm(FlaskForm):
    password = PasswordField("New password", validators=[DataRequired(), Length(8)])
    password2 = PasswordField(
        "Repeat the password", validators=[DataRequired(), Length(8)]
    )
    submit = SubmitField("Save")
