from flask import Flask, render_template, jsonify, request, redirect, session
from flask_cors import CORS

from data import get_organizations, get_dashboard, get_patient_demographics, get_treatments, get_trends

app = Flask(__name__)
app.secret_key = "secret_key"
CORS(app)

# user = {
#     "name": "Dr. Sarah Williamson",
#     'organization': "HOLLYWOOD CROSS MEDICAL CLINIC"
# }

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        is_authenticated = session.get("is_authenticated", False)
        if not is_authenticated:
            username = request.form.get("username")
            password = request.form.get("password")
            organization = request.form.get("organization")

            session["is_authenticated"] = True
            session["user"] = {"name": username, "organization": organization}
            return redirect("/")
        else:
            session["is_authenticated"] = False
            return redirect("/")
    
    is_authenticated = session.get("is_authenticated", False)
    user = session.get("user", {})
    organizations = get_organizations()

    return render_template("index.html", organizations=organizations, is_authenticated=is_authenticated, user=user.get("name", ""))

@app.route("/api/dashboard")
def dashboard():
    user = session.get("user", {})
    data = get_dashboard(user.get("organization", ""))

    return jsonify(data)

@app.route("/api/demographics")
def demographics():
    user = session.get("user", {})
    age_filter = request.args.get("age")
    gender_filter = request.args.get("gender")
    condition_filter = request.args.get("condition")

    data = get_patient_demographics(user.get("organization", ""), age_filter, gender_filter, condition_filter)
    return jsonify(data)

@app.route("/api/treatments")
def treatments():
    user = session.get("user", {})
    time_filter = request.args.get("time")
    medication_filter = request.args.get("medication")
    
    treatments_data = get_treatments(user.get("organization", ""), time_filter, medication_filter)
    return jsonify(treatments_data)

@app.route("/api/trends")
def trends():
    user = session.get("user", {})
    region_filter = request.args.get("region")
    time_filter = request.args.get("time")

    public_health_data = get_trends(user.get("organization", ""), region_filter, time_filter)

    print(public_health_data)
    return jsonify(public_health_data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)