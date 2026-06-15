from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- STORAGE ----------------

users = []
donations = []

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")


# ---------------- USER REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def user_register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        users.append({
            "username": username,
            "password": password
        })

        return redirect(url_for("user_login"))

    return render_template("user_register.html")


# ---------------- USER LOGIN ----------------

@app.route("/user-login", methods=["GET", "POST"])
def user_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        for user in users:

            if user["username"] == username and user["password"] == password:
                return redirect(url_for("donate_food"))

        return "Invalid User Login"

    return render_template("user_login.html")


# ---------------- DONATE FOOD ----------------

@app.route("/donate", methods=["GET", "POST"])
def donate_food():

    if request.method == "POST":

        name = request.form.get("name")
        food = request.form.get("food")
        quantity = request.form.get("quantity")
        address = request.form.get("address")

        donations.append({
            "name": name,
            "food": food,
            "quantity": quantity,
            "address": address,
            "status": "Pending",
            "delivery_person": "Not Assigned",
            "pickup_time": "-"
        })

        return render_template(
            "success.html",
            message="Food Donation Submitted Successfully!"
        )

    return render_template("donate_food.html")


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "foodsaver2026":
            return redirect(url_for("admin_dashboard"))

        return "Invalid Admin Login"

    return render_template("admin_login.html")


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin-dashboard")
def admin_dashboard():

    return render_template(
        "admin_dashboard.html",
        donations=donations
    )


# ---------------- DELIVERY LOGIN ----------------

@app.route("/delivery-login", methods=["GET", "POST"])
def delivery_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "delivery" and password == "foodsaver":
            return redirect(url_for("delivery_dashboard"))

        return "Invalid Delivery Login"

    return render_template("delivery_login.html")


# ---------------- DELIVERY DASHBOARD ----------------

@app.route("/delivery-dashboard")
def delivery_dashboard():

    return render_template(
        "delivery_dashboard.html",
        donations=donations
    )


# ---------------- TRACK DONATION ----------------

@app.route("/track-donation")
def track_donation():

    return render_template(
        "track_donation.html",
        donations=donations
    )


# ---------------- UPDATE STATUS ----------------

@app.route("/update-status/<int:index>/<status>")
def update_status(index, status):

    if index < len(donations):
        donations[index]["status"] = status

    return redirect(url_for("admin_dashboard"))


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)