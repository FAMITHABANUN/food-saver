from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    return redirect(url_for("user_register"))


# ----------------------------
# USER REGISTER PAGE
# ----------------------------
@app.route("/register", methods=["GET", "POST"])
def user_register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            return redirect(url_for("donate_food"))

        return "Please fill all fields"

    return render_template("user_register.html")


# ----------------------------
# ADMIN LOGIN PAGE
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            return redirect(url_for("admin_dashboard"))

        return "Invalid Admin Login"

    return render_template("admin_login.html")


# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


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
# RUN APPLICATION
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)