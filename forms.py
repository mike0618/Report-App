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
class CommonForm(FlaskForm):
    name = StringField(
        "Name", validators=[DataRequired()], render_kw={"placeholder": "Name"}
    )
    desc = StringField("Description", render_kw={"placeholder": "Description"})


class RegisterForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired()], render_kw={"placeholder": "Email"}
    )
    name = StringField(
        "Name", validators=[DataRequired()], render_kw={"placeholder": "Name"}
    )
    lastname = StringField("Last Name", render_kw={"placeholder": "Last Name"})
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(8)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Sign up")


class PlaceForm(CommonForm):
    submit = SubmitField("Add")


class SensorForm(CommonForm):
    topic = StringField(
        "MQTT Topic", validators=[DataRequired()], render_kw={"placeholder": "Topic"}
    )
    submit = SubmitField("Add")


class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired()], render_kw={"placeholder": "Email"}
    )
    password = PasswordField(
        "Password", validators=[DataRequired()], render_kw={"placeholder": "Password"}
    )
    submit = SubmitField("Sign in")


class PersonalForm(CommonForm):
    email = StringField("Email", validators=[DataRequired()])
    lastname = StringField("Last Name")
    old_password = PasswordField(
        "Old Password (leave it blank if you don't need to change)"
    )
    new_password = PasswordField("New Password")
    submit = SubmitField("Save")


class PersonalFormAdmin(CommonForm):
    email = StringField("Email", validators=[DataRequired()])
    lastname = StringField("Last Name")
    access = BooleanField("Read Access")
    submit = SubmitField("Save")


class NewPassForm(FlaskForm):
    password = PasswordField("New password", validators=[DataRequired(), Length(8)])
    password2 = PasswordField(
        "Repeat the password", validators=[DataRequired(), Length(8)]
    )
    submit = SubmitField("Save")
