from flask import Flask, render_template, request, redirect, url_for

app = Flask(_name_)

# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    return redirect(url_for("user_register"))


# ----------------------------
# ADMIN LOGIN
# URL: /login
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Simple admin credentials
        if username == "admin" and password == "admin123":
            return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid Admin Login"

    return render_template("admin_login.html")


# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


# ----------------------------
# USER REGISTER / LOGIN
# URL: /register
# ----------------------------
@app.route("/register", methods=["GET", "POST"])
def user_register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Simple demo login/register
        # Later you can store in database

        if username and password:
            return redirect(url_for("donate_food"))

        return "Please enter details"

    return render_template("user_register.html")


# ----------------------------
# DONATE FOOD PAGE
# ----------------------------
@app.route("/donate", methods=["GET", "POST"])
def donate_food():

    if request.method == "POST":

        donor_name = request.form.get("name")
        food_item = request.form.get("food")
        quantity = request.form.get("quantity")
        address = request.form.get("address")

        print("Donation Received")
        print(donor_name, food_item, quantity, address)

        return render_template(
            "success.html",
            message="Food Donation Submitted Successfully!"
        )

    return render_template("donate_food.html")


# ----------------------------
# RUN APP
# ----------------------------
if _name_ == "_main_":
    app.run(host="0.0.0.0", port=10000)