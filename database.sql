-- ================= USERS =================
CREATE TABLE roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE
);

CREATE TABLE permissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE
);

CREATE TABLE role_permissions (
  role_id INTEGER,
  permission_id INTEGER,
  FOREIGN KEY (role_id) REFERENCES roles(id),
  FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role_id INTEGER,
  FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- ================= PRODUCTS =================
CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  category TEXT,
  price REAL NOT NULL,
  quantity INTEGER DEFAULT 0,
  image TEXT,
  description TEXT
);

-- ================= ORDERS =================
CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  total_price REAL NOT NULL,
  created_at TEXT NOT NULL,
  address TEXT NOT NULL,
  status TEXT DEFAULT 'Pending',
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ================= ORDER ITEMS =================
CREATE TABLE order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER DEFAULT 1,
  price REAL NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ================= 🔥 DATA SEED =================

-- roles
INSERT INTO roles (id, name) VALUES (1, 'admin');
INSERT INTO roles (id, name) VALUES (2, 'user');

-- permissions
INSERT INTO permissions (id, name) VALUES (1, 'add_product');
INSERT INTO permissions (id, name) VALUES (2, 'delete_product');
INSERT INTO permissions (id, name) VALUES (3, 'view_products');
INSERT INTO permissions (id, name) VALUES (4, 'manage_users');

-- admin permissions
INSERT INTO role_permissions VALUES (1,1);
INSERT INTO role_permissions VALUES (1,2);
INSERT INTO role_permissions VALUES (1,3);
INSERT INTO role_permissions VALUES (1,4);

-- user permissions
INSERT INTO role_permissions VALUES (2,3);

-- ================= DEFAULT USERS =================
-- admin user: username=admin, password=admin@123
INSERT INTO users (username, email, password, role_id) VALUES (
  'admin',
  'admin@techshop.com',
  'scrypt:32768:8:1$ZFEDzVqg5qiC5pPT$8e73c6c4773b7ad51fb6d2ab5a9b40c3b4bdd5dc7b7a2cba92de5fdeed91e17e9f11b0e4a44e7dafabe1a59e5cfa4fcebd28d2e4c22e7fc4e55b28b2e7a7d9b',
  1
);

-- ================= SAMPLE PRODUCTS =================
INSERT INTO products (name, category, price, quantity, image, description) VALUES
  ('ASUS VivoBook 15', 'Laptops', 18500.00, 15, '', 'Intel Core i5-1235U, 8GB RAM, 512GB SSD, 15.6" FHD Display. Perfect for everyday computing and productivity.'),
  ('Dell Inspiron 14', 'Laptops', 22000.00, 8, '', 'AMD Ryzen 5 7530U, 16GB RAM, 512GB NVMe SSD, 14" FHD Anti-Glare Display. Slim and powerful business laptop.'),
  ('HP 27" FHD Monitor', 'Monitors', 9800.00, 20, '', '27-inch Full HD IPS display, 75Hz refresh rate, AMD FreeSync, HDMI and VGA ports. Ideal for home and office use.'),
  ('Logitech MX Keys Keyboard', 'Accessories', 2800.00, 30, '', 'Advanced wireless illuminated keyboard with smart backlighting, USB-C charging, and multi-device support.'),
  ('Samsung 1TB SSD T7', 'Accessories', 3200.00, 25, '', 'Portable NVMe SSD with USB 3.2 Gen 2 interface, up to 1050MB/s read speed. Compact and durable design.');