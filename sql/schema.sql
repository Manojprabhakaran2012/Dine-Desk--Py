-- =====================================================================
-- RESTAURANT MANAGEMENT SYSTEM - DATABASE SCHEMA
-- =====================================================================
-- Design Note:
-- Instead of 3 separate tables (Users, Staff, Admin), we use ONE
-- unified "users" table with a "role" column ('user', 'staff', 'admin').
-- This is called "Single Table Inheritance" style design.
--
-- Why this is better:
--   1. Avoids duplicate columns (name, email, password, phone) in 3 tables
--   2. Login system becomes simple: ONE query checks email+password+role
--   3. Easy to promote/demote a person's role (just update one column)
--   4. Foreign keys from Orders/Bookings/Food just point to users.id,
--      no matter if the action was done by a user, staff, or admin
-- =====================================================================

DROP DATABASE IF EXISTS restaurant_management;
CREATE DATABASE restaurant_management;
USE restaurant_management;

-- ---------------------------------------------------------------------
-- TABLE 1: users
-- Stores ALL people who can log in: normal users, staff, and admin.
-- ---------------------------------------------------------------------
CREATE TABLE users (
    user_id      INT AUTO_INCREMENT PRIMARY KEY,
    full_name    VARCHAR(100)  NOT NULL,
    email        VARCHAR(100)  NOT NULL UNIQUE,
    password     VARCHAR(255)  NOT NULL,           -- store hashed password
    phone        VARCHAR(15),
    address      VARCHAR(255),
    role         ENUM('user', 'staff', 'admin') NOT NULL DEFAULT 'user',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- TABLE 2: restaurant_tables
-- Physical dining tables in the restaurant.
-- ---------------------------------------------------------------------
CREATE TABLE restaurant_tables (
    table_id     INT AUTO_INCREMENT PRIMARY KEY,
    table_number VARCHAR(10)   NOT NULL UNIQUE,
    capacity     INT           NOT NULL,
    status       ENUM('Available', 'Booked') NOT NULL DEFAULT 'Available'
);

-- ---------------------------------------------------------------------
-- TABLE 3: food_items
-- Menu items managed by staff.
-- ---------------------------------------------------------------------
CREATE TABLE food_items (
    food_id      INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    description  VARCHAR(255),
    price        DECIMAL(8,2)  NOT NULL,
    category     VARCHAR(50)   DEFAULT 'General',
    image        VARCHAR(255)  DEFAULT 'default_food.png',
    availability ENUM('Available', 'Unavailable') NOT NULL DEFAULT 'Available',
    added_by     INT,                                -- staff who added the item
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (added_by) REFERENCES users(user_id)
        ON DELETE SET NULL
);

-- ---------------------------------------------------------------------
-- TABLE 4: orders
-- One row per food order placed by a user.
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    order_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,                       -- who placed the order
    table_id     INT,                                 -- optional: dine-in table
    order_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status       ENUM('Pending', 'Preparing', 'Ready', 'Delivered')
                 NOT NULL DEFAULT 'Pending',

    FOREIGN KEY (user_id)  REFERENCES users(user_id)  ON DELETE CASCADE,
    FOREIGN KEY (table_id) REFERENCES restaurant_tables(table_id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------------
-- TABLE 5: order_details
-- Line items for each order (many food items per order).
-- ---------------------------------------------------------------------
CREATE TABLE order_details (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    food_id         INT NOT NULL,
    quantity        INT NOT NULL DEFAULT 1,
    price           DECIMAL(8,2) NOT NULL,           -- price at time of order

    FOREIGN KEY (order_id) REFERENCES orders(order_id)       ON DELETE CASCADE,
    FOREIGN KEY (food_id)  REFERENCES food_items(food_id)    ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- TABLE 6: table_bookings
-- Table reservations made by users, assigned by staff.
-- ---------------------------------------------------------------------
CREATE TABLE table_bookings (
    booking_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL,                   -- who booked
    table_id         INT NOT NULL,                   -- which table
    assigned_staff_id INT,                            -- staff who confirmed it
    booking_date     DATE NOT NULL,
    booking_time     TIME NOT NULL,
    number_of_guests INT NOT NULL DEFAULT 1,
    status           ENUM('Pending', 'Confirmed', 'Cancelled')
                     NOT NULL DEFAULT 'Pending',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)  REFERENCES users(user_id)  ON DELETE CASCADE,
    FOREIGN KEY (table_id) REFERENCES restaurant_tables(table_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_staff_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------------
-- TABLE 7: parking_payments
-- Parking fee payments made by users (Bike / Car).
-- ---------------------------------------------------------------------
CREATE TABLE parking_payments (
    payment_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    vehicle_type  ENUM('Bike', 'Car') NOT NULL,
    amount        DECIMAL(8,2) NOT NULL,
    payment_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =====================================================================
-- SAMPLE DATA
-- =====================================================================

-- ---------------- Users (mix of user / staff / admin) ----------------
-- NOTE: The passwords below are already hashed using Werkzeug's
-- generate_password_hash() (the SAME method app.py uses at runtime),
-- so login works immediately after importing this file. The plain-text
-- password for each sample account is written in the comment above it.

-- admin@restaurant.com       -> password: admin123
-- ravi.staff@restaurant.com  -> password: staff123
-- priya.staff@restaurant.com -> password: staff123
-- arjun@example.com          -> password: user123
-- sneha@example.com          -> password: user123
INSERT INTO users (full_name, email, password, phone, address, role) VALUES
('Admin User',     'admin@restaurant.com',       'scrypt:32768:8:1$2GHi2lj40fAVEFk9$38e93834f58a52431093c20faa7c9b05b28539b5be16cf26b1c5353ce4b5c231f38276227933d986f5455b9c9d4da3a1628de6b07e2d48e5561f1b484ba57dd3', '9999999999', 'Restaurant HQ',   'admin'),
('Ravi Kumar',     'ravi.staff@restaurant.com',  'scrypt:32768:8:1$vNkLqj2qNTYxkBVh$c9f85915e038ad65b7e3d9face01a6d04875723a22b59694efe7b2ce21c5ae24bc3219d1b7d192aec46fa7cd5ba4b09bc6ddc189216f9d5c33d781764ecee492', '9876543210', 'Staff Quarters',  'staff'),
('Priya Sharma',   'priya.staff@restaurant.com', 'scrypt:32768:8:1$vNkLqj2qNTYxkBVh$c9f85915e038ad65b7e3d9face01a6d04875723a22b59694efe7b2ce21c5ae24bc3219d1b7d192aec46fa7cd5ba4b09bc6ddc189216f9d5c33d781764ecee492', '9876500000', 'Staff Quarters',  'staff'),
('Arjun Mehta',    'arjun@example.com',          'scrypt:32768:8:1$l0F3Lkf9qXl0vdao$286316724daa784d30a35dda2dc4952d7bd9c2bada0588833dde961f75579a413437c680f2ff336777a06f37d3618d2bfd6dc502c6146f2f35ed5ebc8db71dbb', '9123456780', '12 MG Road, Erode', 'user'),
('Sneha Reddy',    'sneha@example.com',          'scrypt:32768:8:1$l0F3Lkf9qXl0vdao$286316724daa784d30a35dda2dc4952d7bd9c2bada0588833dde961f75579a413437c680f2ff336777a06f37d3618d2bfd6dc502c6146f2f35ed5ebc8db71dbb', '9123456781', '45 Park Street, Erode', 'user');

-- ---------------- Restaurant Tables -----------------------------------
INSERT INTO restaurant_tables (table_number, capacity, status) VALUES
('T1', 2, 'Available'),
('T2', 4, 'Available'),
('T3', 4, 'Booked'),
('T4', 6, 'Available'),
('T5', 8, 'Available');

-- ---------------- Food Items -------------------------------------------
INSERT INTO food_items (name, description, price, category, availability, added_by) VALUES
('Paneer Butter Masala', 'Rich and creamy paneer curry', 220.00, 'Main Course', 'Available', 2),
('Veg Biryani',          'Fragrant basmati rice with vegetables', 180.00, 'Main Course', 'Available', 2),
('Masala Dosa',          'Crispy dosa with potato filling', 90.00, 'Breakfast', 'Available', 2),
('Chicken 65',           'Spicy fried chicken starter', 200.00, 'Starters', 'Available', 3),
('Gulab Jamun',          'Sweet milk-solid dumplings in syrup', 60.00, 'Dessert', 'Unavailable', 3);

-- ---------------- Orders + Order Details --------------------------------
INSERT INTO orders (user_id, table_id, total_amount, status) VALUES
(4, 2, 400.00, 'Pending'),
(5, NULL, 90.00, 'Delivered');

INSERT INTO order_details (order_id, food_id, quantity, price) VALUES
(1, 1, 1, 220.00),
(1, 2, 1, 180.00),
(2, 3, 1, 90.00);

-- ---------------- Table Bookings ----------------------------------------
INSERT INTO table_bookings (user_id, table_id, assigned_staff_id, booking_date, booking_time, number_of_guests, status) VALUES
(4, 3, 2, '2026-07-10', '19:30:00', 4, 'Confirmed'),
(5, 4, NULL, '2026-07-12', '20:00:00', 5, 'Pending');

-- ---------------- Parking Payments --------------------------------------
INSERT INTO parking_payments (user_id, vehicle_type, amount) VALUES
(4, 'Car', 50.00),
(5, 'Bike', 20.00);

-- =====================================================================
-- END OF SCHEMA
-- =====================================================================
