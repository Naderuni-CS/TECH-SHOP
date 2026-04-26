from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
import sqlite3
import os

inventory_bp = Blueprint('inventory', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("database.db", timeout=20)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@inventory_bp.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))
    return render_template("admin_dashboard.html")

@inventory_bp.route("/admin-products")
def admin_products():
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))
    
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("admin_products.html", products=products)

@inventory_bp.route("/add-product", methods=["GET", "POST"])
def add_product():
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))

    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        description = request.form["description"]
        image = request.files["image"]

        if image and image.filename:
            filename = image.filename.replace("\\", "/").split("/")[-1]
            image_path = os.path.join("static", filename)
            image.save(image_path)
            image_db_path = filename  # store just filename, url_for handles the static prefix
        else:
            image_path = ""
            image_db_path = ""

        db = get_db()
        db.execute("""
            INSERT INTO products (name, category, price, quantity, image, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, category, price, quantity, image_db_path, description))
        db.commit()
        flash("Product added successfully to Inventory!", "success")
        return redirect(url_for("inventory.admin_products"))

    return render_template("add_product.html")

@inventory_bp.route("/delete-product/<int:id>")
def delete_product(id):
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))
        
    db = get_db()
    # Remove order_items that reference this product first (FK constraint)
    db.execute("DELETE FROM order_items WHERE product_id=?", (id,))
    db.execute("DELETE FROM products WHERE id=?", (id,))
    db.commit()
    flash("Product removed from Inventory.", "success")
    return redirect(url_for("inventory.admin_products"))

@inventory_bp.route("/view-orders")
def view_orders():
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))
    
    db = get_db()
    # Fetch orders with username
    orders = db.execute("""
        SELECT orders.*, users.username 
        FROM orders 
        JOIN users ON orders.user_id = users.id 
        ORDER BY orders.created_at DESC
    """).fetchall()
    return render_template("orders.html", orders=orders)

@inventory_bp.route("/mark-shipped/<int:id>")
def mark_shipped(id):
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))
    
    db = get_db()
    db.execute("UPDATE orders SET status = 'Shipped' WHERE id = ?", (id,))
    db.commit()
    flash(f"Order #{id} has been marked as Shipped!", "success")
    return redirect(url_for("inventory.view_orders"))

@inventory_bp.route("/restock/<int:id>", methods=["POST"])
def restock(id):
    if session.get("role") != "admin":
        return redirect(url_for("web_login"))
    
    amount = int(request.form.get("amount", 0))
    if amount > 0:
        db = get_db()
        db.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (amount, id))
        db.commit()
        flash(f"Added {amount} units to stock.", "success")
    else:
        flash("Please enter a valid amount.", "error")
        
    return redirect(url_for("inventory.admin_products"))

# API-like helper for communication between subsystems
def update_stock(id, quantity_diff):
    db = get_db()
    db.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity_diff, id))
    db.commit()
