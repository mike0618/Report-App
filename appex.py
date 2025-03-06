"""
This module contains flask handling functions and DML commands
"""

from sqlalchemy import desc
from orm import db, app, User, Symptoms
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from time import sleep
import os
from flask import (
    render_template,
    send_from_directory,
    redirect,
    url_for,
    flash,
    request,
    Response,
)
from flask_login import (
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)
from forms import (
    PersonalFormAdmin,
    RegisterForm,
    LoginForm,
    EditDayForm,
    PersonalForm,
    symp_map,
)


# Current date and time
def date_time():
    return datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")


# Connect to LoginManager
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


@app.route("/")  # root web site url, by default used GET method
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if not current_user.access:
        return redirect(url_for("personal"))
    w = db.session.query(Symptoms).order_by(desc(Symptoms.id)).limit(7).all()[::-1]
    cols = Symptoms.metadata.tables["symptoms"].columns.keys()[5:]
    tr = [[symp_map.get(col)] + [getattr(rec, col) for rec in w] for col in cols]
    return render_template("index.html", rows=tr, week=w, current=True)


# this route works with GET and POST methods
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()  # use form from the forms module
    if form.validate_on_submit():  # when validated it comes via POST method
        email = form.email.data
        # check if email exists in the DB
        # SELECT * FROM User WHERE email=email;
        if db.session.query(User).filter_by(email=email).first():
            flash("This account already exists. Try to login please.")
            # offer to try login if exists
            return redirect(url_for("login", email=email))
        user_hash = generate_password_hash(
            str(form.password.data), method="pbkdf2:sha256", salt_length=16
        )  # create pw hash
        new_user = User()  # create a user and save its columns
        # save the data from the form, hash and date
        new_user.email = str(email)
        new_user.name = str(form.name.data)
        new_user.lastname = str(form.lastname.data)
        new_user.password = user_hash
        new_user.reg_date = date_time()
        # INSERT INTO User (columns) VALUES (values);
        db.session.add(new_user)
        # add the user to the DB and commit changes
        db.session.commit()
        if new_user.id == 1:
            new_user.access = True
            db.session.commit()
        login_user(new_user)
        # if registered and login successfully the user redirected to the personal page
        return redirect(url_for("home"))
    # if it's GET method, register page opened with the form
    return render_template("register.html", form=form)


@app.route("/personal")
def personal():
    if current_user.is_authenticated:
        return render_template("personal.html")
    # if there is no authenticated user, redirect to the home page
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
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
            return redirect(url_for("login"))
        if not check_password_hash(user.password, str(form.password.data)):
            flash("The password is wrong.", "error")
            return redirect(url_for("login"))
        # if everything is ok, log in the user, and redirect to the home page
        login_user(user)
        return redirect(url_for("home"))
    # if it's GET, show login page with the form
    return render_template("login.html", form=form)


@app.route("/edit-day/<int:id>", methods=["GET", "POST"])
def edit_day(id):
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if current_user.id != 1:
        return redirect(url_for("home"))
    day = db.get_or_404(Symptoms, id)
    day_form = EditDayForm(
        flback=day.flback,
        sdream=day.sdream,
        nausea=day.nausea,
        stpain=day.stpain,
        srspain=day.srspain,
        shoulders=day.shoulders,
        jawcl=day.jawcl,
        crying=day.crying,
        ncogn=day.ncogn,
        ocogn=day.ocogn,
        ehrate=day.ehrate,
        panic=day.panic,
        fear=day.fear,
        sweating=day.sweating,
        shaking=day.shaking,
        unsafe=day.unsafe,
        scream=day.scream,
        tinnit=day.tinnit,
    )
    if day_form.validate_on_submit():
        day.flback = str(day_form.flback.data)
        day.sdream = str(day_form.sdream.data)
        day.nausea = str(day_form.nausea.data)
        day.stpain = str(day_form.stpain.data)
        day.srspain = str(day_form.srspain.data)
        day.shoulders = str(day_form.shoulders.data)
        day.jawcl = str(day_form.jawcl.data)
        day.crying = str(day_form.crying.data)
        day.ncogn = str(day_form.ncogn.data)
        day.ocogn = str(day_form.ocogn.data)
        day.ehrate = str(day_form.ehrate.data)
        day.panic = str(day_form.panic.data)
        day.fear = str(day_form.fear.data)
        day.sweating = str(day_form.sweating.data)
        day.shaking = str(day_form.shaking.data)
        day.unsafe = str(day_form.unsafe.data)
        day.scream = str(day_form.scream.data)
        day.tinnit = str(day_form.tinnit.data)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit-day.html", form=day_form, day=day)


@app.route("/logout")  # this is obviously a logout function
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/admin")
def admin():
    if not current_user.is_authenticated or current_user.id != 1:
        return redirect(url_for("home"))
    users = db.session.query(User).order_by(User.id).all()
    return render_template("admin.html", all_users=users)


@app.route("/personal/edit", methods=["GET", "POST"])
def edit_personal():  # edit personal data
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
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
        return redirect(url_for("personal"))
    return render_template("edit-personal.html", form=form)


@app.route("/admin/user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):  # edit user data for administrator
    if not current_user.is_authenticated or current_user.id != 1:
        return redirect(url_for("home"))
    user = db.get_or_404(User, user_id)
    form = PersonalFormAdmin(
        email=user.email, name=user.name, lastname=user.lastname, access=user.access
    )
    if form.validate_on_submit():
        user.email = str(form.email.data)
        user.name = str(form.name.data)
        user.lastname = str(form.lastname.data)
        user.access = form.access.data
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("edit-user.html", form=form, user=user)


@app.route("/calendar")
def calendar():
    if current_user.is_authenticated and current_user.access:
        years = db.session.query(Symptoms.year).distinct().all()
        return render_template("calendar.html", years=years)
    return redirect(url_for("home"))


@app.route("/get_months/<int:year>", methods=["POST"])
def get_months(year):
    if not current_user.is_authenticated or not current_user.access:
        return redirect(url_for("home"))
    months = (
        db.session.query(Symptoms.month).filter(Symptoms.year == year).distinct().all()
    )
    html = "".join(
        f"""<button class="btn btn-outline-dark btn-block"
    hx-post="/get_weeks/{year}/{month[0]}" 
    hx-target="#weeks"
    hx-swap="innerHTML">{month[0]}
    </button>"""
        for month in months
    )
    return html


@app.route("/get_weeks/<int:year>/<month>", methods=["POST"])
def get_weeks(year, month):
    if not current_user.is_authenticated or not current_user.access:
        return redirect(url_for("home"))
    weeks = (
        db.session.query(Symptoms.date)
        .filter(
            Symptoms.year == year,
            Symptoms.month == month,
            Symptoms.day == "Friday",
        )
        .distinct()
        .all()
    )
    html = "".join(
        f"""<button class="btn btn-outline-dark btn-block"
        hx-post="/week/{week[0]}" 
        hx-target="#week"
        hx-swap="innerHTML">
        {week[0][4:6]}/{week[0][6:]}/{week[0][:4]}
        </button>"""
        for week in weeks
    )
    return html


@app.route("/week/<week>", methods=["POST"])
def get_week(week):
    if not current_user.is_authenticated or not current_user.access:
        return redirect(url_for("home"))
    w = db.session.query(Symptoms).filter(Symptoms.date >= week).limit(7).all()
    cols = Symptoms.metadata.tables["symptoms"].columns.keys()[5:]
    tr = [[symp_map.get(col)] + [getattr(rec, col) for rec in w] for col in cols]
    return render_template("table.html", rows=tr, week=w, current=False)


@app.route("/stream")
def stream():
    # if not current_user.is_authenticated or not current_user.access:
    #     return redirect(url_for("home"))

    def event_stream():
        with app.app_context():
            data = None
            while True:
                w = (
                    db.session.query(Symptoms)
                    .order_by(desc(Symptoms.id))
                    .limit(7)
                    .all()[::-1]
                )
                if data == w:
                    sleep(1)
                    continue
                data = w
                cols = Symptoms.metadata.tables["symptoms"].columns.keys()[5:]
                tr = [
                    [symp_map.get(col)] + [getattr(rec, col) for rec in w]
                    for col in cols
                ]
                content = render_template("table.html", rows=tr, week=w).replace(
                    "\n", " "
                )
                yield f"event: message\ndata: {content}\n\n"
                sleep(1)

    return Response(
        event_stream(), content_type="text/event-stream", mimetype="text/event-stream"
    )


@app.route("/admin/user/<int:user_id>/delete")
def delete_user(user_id):
    if not current_user.is_authenticated or current_user.id != 1:
        return redirect(url_for("home"))
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="10.0.0.2", debug=True)
