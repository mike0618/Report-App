from datetime import datetime
from time import sleep
import json
from random import randint
from db_orm import app, db, User, Place, Sensor, Data, Share
from werkzeug.security import generate_password_hash, check_password_hash
import os
from db_orm import mqtt
from flask import (
    Response,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from forms import (
    PlaceForm,
    RegisterForm,
    LoginForm,
    PersonalForm,
    SensorForm,
)

# subscribe on topics
with app.app_context():
    sensors = db.session.query(Sensor).all()
    for s in sensors:
        mqtt.subscribe(s.topic)


@mqtt.on_message()
def on_message(client, userdata, message):
    with app.app_context():
        sensor = db.session.query(Sensor).filter_by(topic=message.topic).first()
        if not sensor:
            return False
        payload = json.loads(message.payload.decode())
        if not payload:
            return False
        print(payload)
        data = Data()
        data.val1 = float(payload.get("val1"))
        data.val2 = float(payload.get("val2"))
        data.battery = int(payload.get("bat"))
        data.solar = int(payload.get("sol"))
        data.signal = int(payload.get("sig"))
        data.bcount = int(payload.get("bc"))
        data.sensor_id = sensor.id
        data.date = datetime.now()
        data.save()


login_manager = LoginManager()
login_manager.init_app(app)


# User Loader
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Year for all templates
@app.context_processor
def inject_year():
    return {"year": datetime.now().year}


@app.route("/favicon.ico")  # set web site icon
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    places = db.session.query(Place).all()
    return render_template("index.html", places=places)


@app.route("/dashboard")
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    return render_template("dash.html")


@app.route("/webrtc")
def webrtc():
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    return render_template("webrtc.html")


@app.route("/stream")
@login_required
def stream():
    def event_stream():
        with app.app_context():
            while True:
                data = [randint(1, 100) for _ in range(7)]
                data2 = [randint(1, 100) for _ in range(7)]
                labels = [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
                yield f"data: {json.dumps({'data': data, 'data2': data2, 'labels': labels})}\n\n"
                sleep(10)

    return Response(event_stream(), content_type="text/event-stream", mimetype="text/event-stream")


@app.route("/sign")
def sign():
    return render_template("sign.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = LoginForm()
    email = request.args.get("email")
    if email:  # check if email was send in the link and add it to the form
        form.email.data = email
    if form.validate_on_submit():
        # when validated, search user in the DB, and check the password
        email = form.email.data
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            flash("This account does not exist.", "error")
            return redirect(url_for("sign"))
        if not check_password_hash(user.password, str(form.password.data)):
            flash("The password is wrong.", "error")
            return redirect(url_for("sign"))
        # if everything is ok, log in the user, and redirect to the home page
        login_user(user)
        return redirect(url_for("home"))
    if request.method == "POST":
        return redirect(url_for("home"))
    return render_template("signin.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():  # when validated it comes via POST method
        email = form.email.data
        # check if email exists in the DB
        # SELECT * FROM User WHERE email=email;
        if db.session.query(User).filter_by(email=email).first():
            flash("This account already exists. Try to login please.")
            print("This account already exists. Try to login please.")
            # offer to try login if exists
            return redirect(url_for("sign", email=email))
        user_hash = generate_password_hash(
            str(form.password.data), method="pbkdf2:sha256", salt_length=16
        )  # create pw hash
        new_user = User()  # create a user and save its columns
        # save the data from the form, hash and date
        new_user.email = str(email)
        new_user.name = str(form.name.data)
        new_user.lastname = str(form.lastname.data)
        new_user.password = user_hash
        new_user.date = datetime.now()
        # add the user to the DB and commit changes
        # INSERT INTO User (columns) VALUES (values);
        new_user.save()
        login_user(new_user)
        # if registered and login successfully the user redirected to the personal page
        return redirect(url_for("home"))
    if request.method == "POST":
        return redirect(url_for("home"))
    return render_template("signup.html", form=form)


@app.route("/logout")  # this is obviously a logout function
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/personal/edit", methods=["GET", "POST"])
def edit_personal():  # edit personal data
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    form = PersonalForm()
    if request.method != "POST":
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.lastname.data = current_user.lastname
    if form.validate_on_submit():
        email = form.email.data
        current_user.name = form.name.data
        current_user.lastname = form.lastname.data
        if email != current_user.email:
            # if email changed, check whether it exists in the DB
            if db.session.query(User).filter_by(email=email).first():
                flash("This email is already registered.", "error")
                return redirect(url_for("edit_personal"))
            current_user.email = email
        if (
            form.old_password.data
            and check_password_hash(current_user.password, str(form.old_password.data))
            and len(str(form.new_password.data)) > 7
        ):
            current_user.password = generate_password_hash(
                str(form.new_password.data), method="pbkdf2:sha256", salt_length=16
            )  # create pw hash
            flash("Your password changed")
        # if everything is ok, perform UPDATE and commit
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit-personal.html", form=form)


@app.route("/add_place", methods=["GET", "POST"])
def add_place():
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    form = PlaceForm()  # use form from the forms module
    if form.validate_on_submit():  # when validated it comes via POST method
        name = str(form.name.data)
        if db.session.query(Place).filter_by(name=name).first():
            flash("This place is already exist.", "error")
            return redirect(url_for("home"))
        new_place = Place()
        # save the data from the form, hash and date
        new_place.name = name
        new_place.desc = str(form.desc.data)
        new_place.date = datetime.now()
        new_place.owner = current_user
        new_place.save()
        return redirect(url_for("home"))
    return render_template("add-place.html", form=form)


@app.route("/edit_place/<int:place_id>", methods=["GET", "POST"])
def edit_place(place_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    form = PlaceForm()  # use form from the forms module
    place = db.get_or_404(Place, place_id)
    if request.method == "GET":
        form.name.data = place.name
        form.desc.data = place.desc
    if form.validate_on_submit():  # when validated it comes via POST method
        name = str(form.name.data)
        if not db.session.query(Place).filter_by(name=name).first():
            place.name = name
        place.desc = str(form.desc.data)
        place.date = datetime.now()
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit-place.html", form=form, place=place)


@app.route("/place/<int:place_id>")
def place(place_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    place = db.get_or_404(Place, place_id)
    return render_template("place.html", place=place)


@app.route("/sensor/<int:sensor_id>")
def sensor(sensor_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    sensor = db.get_or_404(Sensor, sensor_id)
    return render_template("sensor.html", sensor=sensor)


@app.route("/<int:place_id>/add_sensor", methods=["GET", "POST"])
def add_sensor(place_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    form = SensorForm()  # use form from the forms module
    if form.validate_on_submit():  # when validated it comes via POST method
        topic = str(form.topic.data)
        name = str(form.name.data)
        if db.session.query(Sensor).filter_by(topic=topic).first():
            flash("This topic is already exist.", "error")
            return redirect(url_for("home"))
        if db.session.query(Sensor).filter_by(name=name).first():
            flash("This name is already exist.", "error")
            return redirect(url_for("home"))
        new_sensor = Sensor()
        # save the data from the form, hash and date
        new_sensor.name = name
        new_sensor.desc = str(form.desc.data)
        new_sensor.topic = topic
        new_sensor.date = datetime.now()
        new_sensor.owner = current_user
        new_sensor.place_id = place_id
        new_sensor.save()
        return redirect(url_for("home"))
    return render_template("add-sensor.html", form=form, place_id=place_id)


@app.route("/edit_sensor/<int:sensor_id>", methods=["GET", "POST"])
def edit_sensor(sensor_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    form = SensorForm()  # use form from the forms module
    sensor = db.get_or_404(Sensor, sensor_id)
    if request.method == "GET":
        form.name.data = sensor.name
        form.desc.data = sensor.desc
        form.topic.data = sensor.topic
    if form.validate_on_submit():  # when validated it comes via POST method
        name = str(form.name.data)
        topic = str(form.topic.data)
        if not db.session.query(Sensor).filter_by(name=name).first():
            sensor.name = name
        if not db.session.query(Sensor).filter_by(topic=topic).first():
            sensor.topic = topic
        sensor.desc = str(form.desc.data)
        sensor.date = datetime.now()
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit-sensor.html", form=form, sensor=sensor)


@app.route("/add_share/<sensor_id>/<user_id>", methods=["GET", "POST"])
def add_share(sensor_id, user_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    sensor = db.get_or_404(Sensor, sensor_id)
    if sensor.owner == current_user or current_user.id == 1:
        new_share = Share()
        new_share.sensor_id = sensor_id
        new_share.user_id = user_id
        new_share.date = datetime.now()
        new_share.owner = current_user
        new_share.save()
    return redirect(url_for("home"))


@app.route("/user/<int:user_id>/delete", methods=["DELETE"])
def delete_user(user_id):
    if not current_user.is_authenticated or current_user.id not in (1, user_id):
        return redirect(url_for("home"))
    # only authenticated admin or owner can do this
    user = db.get_or_404(User, user_id)
    if current_user.id == user_id:
        logout_user()
    user.delete()
    return Response(headers={"HX-Refresh": "true"}), 204


@app.route("/places/<int:place_id>/delete", methods=["DELETE"])
def delete_place(place_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    place = db.get_or_404(Place, place_id)
    if current_user.id == 1 or current_user == place.owner:
        # admin or owner can do this
        place.delete()
        return "", 200
    return redirect(url_for("home"))


@app.route("/sensors/<int:sensor_id>/delete", methods=["DELETE"])
def delete_sensor(sensor_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    sensor = db.get_or_404(Sensor, sensor_id)
    if current_user.id == 1 or current_user == sensor.owner:
        # admin or owner can do this
        sensor.delete()
        return "", 200
    return redirect(url_for("home"))


@app.route("/<int:share_id>/delete", methods=["DELETE"])
def delete_share(share_id):
    if not current_user.is_authenticated:
        return redirect(url_for("sign"))
    share = db.get_or_404(Share, share_id)
    if current_user.id == 1 or current_user == share.owner:
        # admin or owner can do this
        share.delete()
        return "", 200
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
