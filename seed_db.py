import sqlite3
from werkzeug.security import generate_password_hash

db = sqlite3.connect('database.db')

# Add admin user if not exists
existing = db.execute("SELECT id FROM users WHERE username='admin'").fetchone()
if not existing:
    db.execute("INSERT INTO users (username, email, password, role_id) VALUES (?, ?, ?, ?)",
        ('admin', 'admin@techshop.com', generate_password_hash('admin@123'), 1))
    print("Admin user created: admin / admin@123")

# Add sample products if none exist
count = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
if count == 0:
    products = [
        ('ASUS VivoBook 15', 'Laptops', 18500.00, 15, '', 'Intel Core i5-1235U, 8GB RAM, 512GB SSD, 15.6 inch FHD Display.'),
        ('Dell Inspiron 14', 'Laptops', 22000.00, 8, '', 'AMD Ryzen 5, 16GB RAM, 512GB NVMe SSD, 14 inch FHD Display.'),
        ('HP 27 Inch FHD Monitor', 'Monitors', 9800.00, 20, '', '27-inch Full HD IPS, 75Hz, AMD FreeSync, HDMI and VGA ports.'),
        ('Logitech MX Keys Keyboard', 'Accessories', 2800.00, 30, '', 'Wireless illuminated keyboard, USB-C charging, multi-device support.'),
        ('Samsung 1TB SSD T7', 'Accessories', 3200.00, 25, '', 'Portable NVMe SSD, USB 3.2 Gen 2, up to 1050MB/s read speed.'),
    ]
    db.executemany('INSERT INTO products (name, category, price, quantity, image, description) VALUES (?,?,?,?,?,?)', products)
    print(f"Seeded {len(products)} sample products")

db.commit()
db.close()
print("All done!")
