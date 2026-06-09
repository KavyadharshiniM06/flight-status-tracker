import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session,flash
from flask_login import LoginManager, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from models import db, User
from api import get_flight_data
from scraper import get_airport_info
from alerts import send_alerts
from app import parse_time, format_time, get_delay, format_delay

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
app.config["SECRET_KEY"]                     = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"]        = os.getenv("DATABASE_URL", "sqlite:///flights.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view    = "auth.login"
login_manager.login_message = "Please log in to continue."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)


@app.route("/", methods=["GET", "POST"])
@login_required                                   # ← fix 1: protect the route
def index():
    from models import SavedFlight, SearchHistory

    

    if request.method == "POST":
        raw        = request.form.get("iata", "")
        flights      = []
        alert_status = None
        iata_codes = [i.strip().upper() for i in raw.split(",") if i.strip()]

        for iata in iata_codes:
            try:
                flight   = get_flight_data(API_KEY, iata)
                dep      = flight["departure"]
                arr      = flight["arrival"]
                dep_info = get_airport_info(dep["airport"])
                arr_info = get_airport_info(arr["airport"])

                def enrich(data, info):
                    scheduled = parse_time(data.get("scheduled"))
                    estimated = parse_time(data.get("estimated"))
                    actual    = parse_time(data.get("actual"))
                    best      = actual or estimated
                    delay     = get_delay(scheduled, best)
                    return {
                        "airport":       data.get("airport", "N/A"),
                        "country":       info.get("country", "N/A"),
                        "timezone":      info.get("timezone", "N/A"),
                        "terminal":      data.get("terminal") or "N/A",
                        "gate":          data.get("gate") or "N/A",
                        "scheduled":     format_time(scheduled),
                        "estimated":     format_time(estimated),
                        "actual":        format_time(actual),
                        "delay":         format_delay(delay, flight["flight_status"]),
                        "delay_minutes": delay
                    }

                dep_enriched = enrich(dep, dep_info)
                arr_enriched = enrich(arr, arr_info)

                # Save to search history
                db.session.add(SearchHistory(
                    user_id     = current_user.id,
                    iata        = iata,
                    airline     = flight["airline"]["name"],
                    status      = flight["flight_status"],
                    dep_airport = dep.get("airport"),
                    arr_airport = arr.get("airport")
                ))
                db.session.commit()

                delay_minutes = dep_enriched.get("delay_minutes")
                send_alerts(
                    flight_iata   = iata,
                    delay_minutes = delay_minutes,
                    airport       = dep.get("airport"),
                    phone=current_user.phone
                )

                alert_status = (
                    f"⚠️ Alert sent for {iata} — delayed by {delay_minutes} min"
                    if delay_minutes and delay_minutes > 0
                    else f"✅ {iata} is on time — no alerts sent"
                )

                flights.append({
                    "airline":   flight["airline"]["name"],
                    "iata":      flight["flight"]["iata"],
                    "status":    flight["flight_status"],
                    "departure": dep_enriched,
                    "arrival":   arr_enriched
                })

            except Exception as e:
                flights.append({"error": str(e), "iata": iata})
        
        # Store results in session and redirect
        session["flights"]      = flights
        session["alert_status"] = alert_status
        session["last_iata"]    = raw
        return redirect(url_for("index"))   # ← PRG redirect

    # GET — read results from session and clear them
    flights      = session.pop("flights", [])
    alert_status = session.pop("alert_status", None)
    last_iata    = session.pop("last_iata", "")


    # fix 2: only query after login_required guarantees current_user exists
    saved   = SavedFlight.query.filter_by(user_id=current_user.id).all()
    history = SearchHistory.query.filter_by(user_id=current_user.id)\
                .order_by(SearchHistory.searched_at.desc()).limit(10).all()

    return render_template("index.html",
        flights      = flights,
        alert_status = alert_status,
        last_iata    = last_iata,
        saved        = saved,
        history      = history
    )


@app.route("/save/<iata>", methods=["POST"])
@login_required
def save_flight(iata):
    from models import SavedFlight
    existing = SavedFlight.query.filter_by(
        user_id=current_user.id, iata=iata
    ).first()
    if not existing:
        db.session.add(SavedFlight(user_id=current_user.id, iata=iata))
        db.session.commit()
    return jsonify({"saved": True})


@app.route("/unsave/<iata>", methods=["POST"])
@login_required
def unsave_flight(iata):
    from models import SavedFlight
    SavedFlight.query.filter_by(
        user_id=current_user.id, iata=iata
    ).delete()
    db.session.commit()
    return jsonify({"saved": False})


@app.route("/api/flight/<iata>")
@login_required
def api_flight(iata):
    try:
        flight   = get_flight_data(API_KEY, iata)
        dep      = flight["departure"]
        arr      = flight["arrival"]
        dep_info = get_airport_info(dep["airport"])
        arr_info = get_airport_info(arr["airport"])
        return jsonify({
            "airline":   flight["airline"]["name"],
            "iata":      flight["flight"]["iata"],
            "status":    flight["flight_status"],
            "departure": {**dep, **dep_info},
            "arrival":   {**arr, **arr_info}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/clear-history", methods=["POST"])
@login_required
def clear_history():
    from models import SearchHistory
    SearchHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        new_password     = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if name:
            current_user.name = name
        if phone:
            current_user.phone = phone

        if new_password:
            if new_password != confirm_password:
                flash("Passwords do not match.", "error")
                return redirect(url_for("profile"))
            if len(new_password) < 6:
                flash("Password must be at least 6 characters.", "error")
                return redirect(url_for("profile"))
            current_user.password = bcrypt.generate_password_hash(
                new_password
            ).decode("utf-8")

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html")

@app.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    from models import SavedFlight, SearchHistory
    from flask_login import logout_user

    user_id = current_user.id
    logout_user()

    SearchHistory.query.filter_by(user_id=user_id).delete()
    SavedFlight.query.filter_by(user_id=user_id).delete()
    User.query.filter_by(id=user_id).delete()
    db.session.commit()

    return redirect(url_for("auth.login"))

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)