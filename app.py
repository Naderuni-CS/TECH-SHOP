from flask import Flask, request, jsonify, g, render_template, redirect, url_for, flash, session
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from inventory import inventory_bp
from sales import sales_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"
JWT_SECRET = "jwtsecretkey"

# ================= DB =================
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("database.db", timeout=20)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db:
        db.close()

# ================= AUTH =================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = data
        except:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


def has_permission(user_id, permission):
    db = get_db()

    result = db.execute("""
        SELECT p.name
        FROM users u
        JOIN roles r ON u.role_id = r.id
        JOIN role_permissions rp ON r.id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE u.id = ? AND p.name = ?
    """, (user_id, permission)).fetchone()

    return result is not None


def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = request.user["id"]

            if not has_permission(user_id, permission):
                return jsonify({"error": "Permission denied"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator


# ================= AUTH API =================

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not all(k in data for k in ["username", "email", "password"]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        db = get_db()
        db.execute("""
            INSERT INTO users (username, email, password, role_id)
            VALUES (?, ?, ?, ?)
        """, (
            data["username"],
            data["email"],
            generate_password_hash(data["password"]),
            2
        ))
        db.commit()
        return jsonify({"message": "User registered"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ["username", "password"]):
        return jsonify({"error": "Missing fields"}), 400

    db = get_db()

    user = db.execute("""
        SELECT u.*, r.name as role_name
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE username=?
    """, (data["username"],)).fetchone()

    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "id": user["id"],
        "username": user["username"],
        "role": user["role_name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token})


# ================= PRODUCTS =================

@app.route("/api/products", methods=["GET"])
def get_products():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return jsonify([dict(p) for p in products])


@app.route("/api/products/<int:id>", methods=["GET"])
def get_product(id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(dict(product))


# ================= ADMIN =================

@app.route("/api/add-product", methods=["POST"])
@token_required
@require_permission("add_product")
def add_product():
    data = request.get_json()

    db = get_db()
    db.execute("""
        INSERT INTO products (name, category, price, quantity)
        VALUES (?, ?, ?, ?)
    """, (
        data["name"],
        data.get("category", ""),
        data["price"],
        data["quantity"]
    ))
    db.commit()

    return jsonify({"message": "Product added"}), 201


@app.route("/api/delete-product/<int:id>", methods=["DELETE"])
@token_required
@require_permission("delete_product")
def delete_product(id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id=?", (id,))
    db.commit()

    return jsonify({"message": "Deleted"})


@app.route("/api/update-product/<int:id>", methods=["PUT"])
@token_required
@require_permission("add_product")
def update_product(id):
    data = request.get_json()

    db = get_db()
    db.execute("""
        UPDATE products
        SET name=?, category=?, price=?, quantity=?
        WHERE id=?
    """, (
        data["name"],
        data.get("category", ""),
        data["price"],
        data["quantity"],
        id
    ))
    db.commit()

    return jsonify({"message": "Updated"})


# ================= FRONTEND =================

app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)

@app.context_processor
def inject_globals():
    cart_count = len(session.get("cart", []))
    return dict(cart_count=cart_count)

@app.route("/")
def home():
    if "user" in session:
        if session.get("role") == "admin":
            return redirect(url_for("inventory.admin"))
        return redirect(url_for("dashboard"))
    return redirect(url_for("web_login"))


@app.route("/login", methods=["GET", "POST"])
def web_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("""
            SELECT u.*, r.name as role_name 
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE username=?
        """, (username,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            session["user_id"] = user["id"]
            session["role"] = user["role_name"]

            if user["role_name"] == "admin":
                return redirect(url_for("inventory.admin"))
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session or session.get("role") == "admin":
        return redirect(url_for("web_login"))
    return render_template("dashboard.html")


@app.route("/register", methods=["GET", "POST"])
def web_register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, email, password, role_id) VALUES (?, ?, ?, ?)", 
                         (username, email, password, 2))
            db.commit()
            flash("Account created! Please login.", "success")
            return redirect(url_for("web_login"))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists.", "error")
    return render_template("register.html")


@app.route("/products")
def products():
    db = get_db()
    products_list = db.execute("SELECT * FROM products").fetchall()
    return render_template("products.html", products=products_list)


@app.route("/product/<int:id>")
def product_details(id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()
    return render_template("product_details.html", product=product)


@app.route("/admin-users")
def admin_users():
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))
    
    db = get_db()
    search_query = request.args.get("q", "").strip()
    
    if search_query:
        users = db.execute(
            """SELECT u.id, u.username, u.email, r.name as role 
               FROM users u 
               JOIN roles r ON u.role_id = r.id 
               WHERE u.username LIKE ? OR u.email LIKE ?""", 
            (f"%{search_query}%", f"%{search_query}%")
        ).fetchall()
    else:
        users = db.execute(
            """SELECT u.id, u.username, u.email, r.name as role 
               FROM users u 
               JOIN roles r ON u.role_id = r.id"""
        ).fetchall()
        
    return render_template("admin_users.html", users=users, search_query=search_query)


@app.route("/admin/delete-user/<int:id>", methods=["POST"])
def delete_user(id):
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))

    # Prevent admin from deleting their own account
    if session.get("user_id") == id:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("admin_users"))

    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    flash("User removed successfully.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/change-role/<int:id>", methods=["POST"])
def change_role(id):
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))

    # Prevent admin from changing their own role
    if session.get("user_id") == id:
        flash("You cannot change your own role.", "error")
        return redirect(url_for("admin_users"))

    new_role = request.form.get("role")
    db = get_db()

    # Get role_id from role name
    role_row = db.execute("SELECT id FROM roles WHERE name=?", (new_role,)).fetchone()
    if not role_row:
        flash("Invalid role selected.", "error")
        return redirect(url_for("admin_users"))

    db.execute("UPDATE users SET role_id=? WHERE id=?", (role_row["id"], id))
    db.commit()
    flash(f"User role updated to '{new_role}' successfully.", "success")
    return redirect(url_for("admin_users"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("web_login"))


# ================= INIT DB =================
if not os.path.exists("database.db"):
    with sqlite3.connect("database.db") as db:
        with open("database.sql") as f:
            db.executescript(f.read())

if __name__ == "__main__":
    app.run(debug=True)