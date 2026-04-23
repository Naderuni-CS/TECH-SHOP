from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
import sqlite3
from datetime import datetime
from inventory import update_stock # Demonstrating subsystem communication

sales_bp = Blueprint('sales', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("database.db", timeout=20)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@sales_bp.route("/add-to-cart/<int:id>")
def add_to_cart(id):
    if "user" not in session:
        flash("You must be logged in to add items to your cart. Please sign in or create an account! 🔒", "error")
        return redirect(url_for("web_login"))

    if session.get("role") == "admin":
        flash("Admins cannot order products.", "error")
        return redirect(url_for("products"))
    
    if "cart" not in session:
        session["cart"] = []

    db = get_db()
    product = db.execute("SELECT quantity FROM products WHERE id=?", (id,)).fetchone()

    if product and product["quantity"] > 0:
        session["cart"].append(id)
        session.modified = True
        flash("Item added to cart! 🛒", "success")
    else:
        flash("Sorry, this item is out of stock.", "error")
        
    return redirect(url_for("products"))

@sales_bp.route("/remove-from-cart/<int:id>")
def remove_from_cart(id):
    if "user" not in session:
        return redirect(url_for("web_login"))
    
    if "cart" in session and id in session["cart"]:
        session["cart"].remove(id)
        session.modified = True
        flash("Item removed from cart.", "success")
        
    return redirect(url_for("sales.cart"))

@sales_bp.route("/cart")
def cart():
    if "cart" not in session or len(session["cart"]) == 0:
        return render_template("cart.html", items=[], total=0)

    db = get_db()
    items = []
    total = 0
    for product_id in session["cart"]:
        row = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        if row:
            items.append(row)
            total += row["price"]

    return render_template("cart.html", items=items, total=total)

@sales_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if session.get("role") == "admin":
        return redirect(url_for("home"))
    
    if "cart" not in session or not session["cart"]:
        return redirect(url_for("products"))

    if request.method == "POST":
        address = request.form["address"]
        user_id = session.get("user_id")
        
        db = get_db()
        product_counts = {}
        for pid in session["cart"]:
            product_counts[pid] = product_counts.get(pid, 0) + 1

        # Validation
        for pid, qty in product_counts.items():
            db_qty = db.execute("SELECT quantity FROM products WHERE id=?", (pid,)).fetchone()["quantity"]
            if db_qty < qty:
                flash("Insufficient stock for some items.", "error")
                return redirect(url_for("sales.cart"))

        # Create Order (Sales Subsystem responsibility)
        total_price = sum([db.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()["price"] for pid in session["cart"]])
        
        # Use a single cursor for the transaction
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO orders (user_id, total_price, created_at, address, status)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, total_price, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), address, "Pending"))
        order_id = cursor.lastrowid

        for pid, qty in product_counts.items():
            price = db.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()["price"]
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, pid, qty, price))
            
            # 🔥 Communicating with Inventory Subsystem to update stock
            update_stock(pid, qty)

        db.commit()
        
        session.pop("cart", None)
        return redirect(url_for("sales.thank_you"))

    return render_template("checkout.html")

@sales_bp.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

@sales_bp.route("/order-history")
def order_history():
    if "user" not in session or session.get("role") == "admin":
        return redirect(url_for("web_login"))
    
    user_id = session.get("user_id")
    db = get_db()
    
    # Query to get orders with their items and product details
    orders_data = db.execute("""
        SELECT o.id as order_id, o.total_price, o.created_at, o.status, 
               oi.quantity as item_qty, oi.price as item_price,
               p.name as product_name, p.image as product_image
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    """, (user_id,)).fetchall()

    # Group items by order
    history = {}
    for row in orders_data:
        oid = row['order_id']
        if oid not in history:
            history[oid] = {
                'id': oid,
                'total': row['total_price'],
                'date': row['created_at'],
                'status': row['status'],
                'order_items': []
            }
        history[oid]['order_items'].append({
            'name': row['product_name'],
            'image': row['product_image'],
            'qty': row['item_qty'],
            'price': row['item_price']
        })

    return render_template("order_history.html", orders=list(history.values()))
