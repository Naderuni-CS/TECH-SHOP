from flask import Flask, request, jsonify, g
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from inventory import inventory_bp

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

    if not data or not all(k in data for k in ["name", "price", "quantity"]):
        return jsonify({"error": "Missing fields"}), 400

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




# 🔥 create DB if not exists (for Render)
if not os.path.exists("database.db"):
    with sqlite3.connect("database.db") as db:
        with open("database.sql") as f:
            db.executescript(f.read())

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)