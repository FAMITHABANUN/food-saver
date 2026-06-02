from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    return redirect(url_for("admin_login"))


# ---------------- ADMIN LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            return redirect(url_for("admin_dashboard"))

        return "Invalid Login"

    return render_template("admin_login.html")


# ---------------- USER REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def user_register():

    if request.method == "POST":
        return redirect(url_for("donate_food"))

    return render_template("user_register.html")


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


# ---------------- DONATE FOOD ----------------
@app.route("/donate", methods=["GET", "POST"])
def donate_food():

    if request.method == "POST":

        return render_template(
            "success.html",
            message="Food Donation Submitted Successfully!"
        )

    return render_template("donate_food.html")


# ---------------- SUCCESS PAGE ----------------
@app.route("/success")
def success():
    return render_template("success.html")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)