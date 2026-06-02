from flask import Flask, render_template, request, redirect, url_for

app = Flask(_name_)

# --------------------
# HOME PAGE
# --------------------
@app.route("/")
def home():
    return redirect(url_for("user_register"))


# --------------------
# USER REGISTER
# --------------------
@app.route("/register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            return redirect(url_for("donate_food"))

        return "Please fill all fields"

    return render_template("user_register.html")


# --------------------
# ADMIN LOGIN
# --------------------
@app.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid login"

    return render_template("admin_login.html")


# --------------------
# ADMIN DASHBOARD
# --------------------
@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


# --------------------
# DONATE FOOD
# --------------------
@app.route("/donate", methods=["GET", "POST"])
def donate_food():
    if request.method == "POST":
        name = request.form.get("name")
        food = request.form.get("food")
        quantity = request.form.get("quantity")
        address = request.form.get("address")

        return render_template(
            "success.html",
            message="Food donated successfully!"
        )

    return render_template("donate_food.html")


# --------------------
# RUN APP (LOCAL ONLY)
# --------------------
if _name_ == "_main_":
    app.run(host="0.0.0.0", port=10000)