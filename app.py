from flask import Flask, render_template, request, redirect, session, url_for, flash, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from inventory import inventory_bp
from sales import sales_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database connection management using 'g'
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("database.db", timeout=20)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Register Blueprints
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)

@app.context_processor
def inject_globals():
    cart_count = len(session.get("cart", []))
    return dict(cart_count=cart_count)

@app.route("/")
def home():
    if "user" in session:
        if session["user"] == "admin":
            return redirect(url_for("inventory.admin"))
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", 
                         (username, email, password, "user"))
            db.commit()
            flash("Account created! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "nader" and password == "nader@123":
            session["user"] = "admin"
            flash("Logged in to Inventory Subsystem as Admin", "success")
            return redirect(url_for("inventory.admin"))

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            session["user_id"] = user["id"]
            flash(f"Welcome back to the Sales System, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Credentials ❌", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session or session["user"] == "admin":
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/products")
def products():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("products.html", products=products)

@app.route("/product/<int:id>")
def product_details(id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()
    return render_template("product_details.html", product=product)

if __name__ == "__main__":
    app.run(debug=True)