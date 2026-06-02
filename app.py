from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- STORAGE ----------------
donations = []


# ---------------- HOME ----------------
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


# ---------------- DONATE FOOD ----------------
@app.route("/donate")
def donate_food():
    return render_template("donate_food.html")


# ---------------- SUBMIT DONATION ----------------
@app.route("/submit-donation", methods=["POST"])
def submit_donation():

    name = request.form.get("name")
    food = request.form.get("food")
    quantity = request.form.get("quantity")
    address = request.form.get("address")

    # SAVE DATA
    donations.append({
        "name": name,
        "food": food,
        "quantity": quantity,
        "address": address
    })

    return render_template(
        "success.html",
        message="Food Donation Submitted Successfully!"
    )


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template(
        "admin_dashboard.html",
        donations=donations
    )


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)