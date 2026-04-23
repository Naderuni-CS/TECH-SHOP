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