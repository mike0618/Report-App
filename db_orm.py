"""
This module contains DDL commands
Run it first time directly to create tables

5 Tables are here:

User
id: int - primary_key
desc: str - description
date: str - registration date
email: str - user's email
name: str
lastname: str
password: str

Place
id: int - primary_key
desc: str - description
date: str - creation date
name: str
owner_id: int - foreign key of user

Sensor
id: int - primary_key
desc: str - description
date: str - creation date
name: str
topic: str - mqtt topic
owner_id: int - foreign key of user
place_id: int - foreign key of place

Data
id: int - primary_key
desc: str - description
date: str - posting date
value: float
owner_id: int - foreign key of user
place_id: int - foreign key of place
sensor_id: int - foreign key of sensor

Share
id: int - primary_key
owner_id: int - foreign key of who shared the sensor
sensor_id: int - foreign key of sensor
user_id: int - foreign key of who the sensor is shared with
"""

from datetime import datetime
from typing_extensions import List
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from secrets import token_hex
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin
import matplotlib.pyplot as plt
import matplotlib.image as mpi
from eralchemy import render_er
from flask_mqtt import Mqtt

app = Flask("Data App")  # create the app
app.secret_key = token_hex()  # a random session secret key
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data_app.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # To prevent overhead
app.config["MQTT_USERNAME"] = "lilygo"
app.config["MQTT_PASSWORD"] = "lilygo"
app.config["MQTT_TLS_ENABLED"] = False
Bootstrap(app)  # to use bootstrap in html pages
ckeditor = CKEditor(app)  # to use a text editor in html pages
mqtt = Mqtt(app)


class Base(DeclarativeBase): ...  # some advanced config for db here if needed


# initialize the app with the extension
db = SQLAlchemy(app, model_class=Base)


class Common(db.Model):
    __abstract__ = True  # Prevents SQLAlchemy from creating a table from this class
    id: Mapped[int] = mapped_column(primary_key=True)  # properties are columns
    date: Mapped[datetime] = mapped_column(nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(UserMixin, Common):  # a class represents a table
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    lastname: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=False)
    # for convenience create a list of places and sensors for the user
    places: Mapped[List["Place"]] = relationship(
        back_populates="owner",  # back_populates the owner in Place table with the user
        cascade="all, delete",  # if a user is deleted, all his stuff is deleted
    )
    sensors: Mapped[List["Sensor"]] = relationship(
        back_populates="owner",
        cascade="all, delete",
    )
    shared: Mapped[List["Share"]] = relationship(
        back_populates="owner",  # back_populates place in Sensor table with this place
        cascade="all, delete",  # if a place is deleted, all its sensors are deleted
        foreign_keys="[Share.owner_id]",  # this table has 2 foreign_keys in Share
    )
    shared_with: Mapped[List["Share"]] = relationship(
        back_populates="user",  # back_populates place in Sensor table with this place
        cascade="all, delete",  # if a place is deleted, all its sensors are deleted
        foreign_keys="[Share.user_id]",
    )


class Place(Common):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    desc: Mapped[str] = mapped_column(nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    # back_populates places in User table with this post
    owner = relationship("User", back_populates="places")
    sensors: Mapped[List["Sensor"]] = relationship(
        back_populates="place",  # back_populates place in Sensor table with this place
        cascade="all, delete",  # if a place is deleted, all its sensors are deleted
    )


class Sensor(Common):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    desc: Mapped[str] = mapped_column(nullable=True)
    topic: Mapped[str] = mapped_column(unique=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    owner = relationship("User", back_populates="sensors")
    place_id: Mapped[int] = mapped_column(ForeignKey(Place.id))
    place = relationship("Place", back_populates="sensors")
    data: Mapped[List["Data"]] = relationship(
        back_populates="sensor",  # back_populates place in Sensor table with this place
        cascade="all, delete",  # if a place is deleted, all its sensors are deleted
    )
    share: Mapped[List["Share"]] = relationship(
        back_populates="sensor",  # back_populates place in Sensor table with this place
        cascade="all, delete",  # if a place is deleted, all its sensors are deleted
    )


class Data(Common):
    val1: Mapped[float] = mapped_column(nullable=False)
    val2: Mapped[float] = mapped_column(nullable=True)
    battery: Mapped[int] = mapped_column(nullable=True)
    solar: Mapped[int] = mapped_column(nullable=True)
    signal: Mapped[int] = mapped_column(nullable=True)
    bcount: Mapped[int] = mapped_column(nullable=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey(Sensor.id))
    sensor = relationship("Sensor", back_populates="data")


class Share(Common):
    sensor_id: Mapped[int] = mapped_column(ForeignKey(Sensor.id))
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    sensor = relationship("Sensor", back_populates="share")
    # explicitly specify foreign_keys, because they are from the same table
    owner = relationship("User", back_populates="shared", foreign_keys=[owner_id])
    user = relationship("User", back_populates="shared_with", foreign_keys=[user_id])


if __name__ == "__main__":
    # perform the code below only if this file is started directly
    with app.app_context():  # db could be used only with app context
        # CREATE TABLE IF NOT EXISTS Table ();
        db.create_all()
        print("The DB file and tables have been created.")
        img = "model.png"
        render_er(db.metadata, img)
        plot = plt.imshow(mpi.imread(img))
        plt.rcParams["figure.figsize"] = (16, 10)
        plt.show()
