# 🍽️ Restaurant Management System

A full-stack **Restaurant Management System** built as a college mini
project using **plain HTML/CSS/JavaScript**, **Python Flask**, and
**MySQL** — no frontend frameworks (no Bootstrap, React, or Tailwind).

Three roles are supported from a single, unified login:
- 👤 **User** (customer)
- 🧑‍🍳 **Staff**
- 🛠️ **Admin**

---

## 📁 Project Structure

```
restaurant-management-system/
├── app.py                     # Flask entry point (registers blueprints)
├── requirements.txt            # Python dependencies
│
├── config/
│   └── db_config.py            # MySQL connection settings
│
├── routes/                     # Flask blueprints (one file per module)
│   ├── auth_routes.py          # Login, Register, Logout
│   ├── user_routes.py          # Customer features
│   ├── staff_routes.py         # Staff features
│   ├── admin_routes.py         # Admin features
│   └── decorators.py           # @login_required(role=...) decorator
│
├── sql/
│   └── schema.sql              # Full database schema + sample data
│
├── static/
│   ├── css/                    # style.css, auth.css, dashboard.css, tables.css
│   ├── js/                     # main.js, user.js, staff.js, admin.js
│   └── images/                 # logo & food placeholder images
│
└── templates/
    ├── auth/                   # login.html, register.html
    ├── shared/                 # base.html + role-specific base layouts
    ├── user/                   # 8 pages (menu, orders, bookings, parking, profile)
    ├── staff/                  # 6 pages (dashboard, food, tables, bookings, orders)
    └── admin/                  # 7 pages (dashboard, history, users, staff, reports)
```

---

## 🗄️ Database Design

**Key design decision:** a single `users` table with a `role` column
(`user` / `staff` / `admin`) handles authentication for *everyone*,
instead of 3 separate tables. This keeps the schema normalized and
makes login/authorization logic simple and consistent.

| Table | Purpose |
|---|---|
| `users` | All accounts (customers, staff, admin) |
| `restaurant_tables` | Physical dining tables |
| `food_items` | Menu items |
| `orders` | Food orders placed by customers |
| `order_details` | Line items within each order |
| `table_bookings` | Table reservations |
| `parking_payments` | Bike/Car parking fee payments |

All foreign keys and `ON DELETE` rules are defined in `sql/schema.sql`.

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- MySQL Server (or MariaDB) running locally

### 2. Install Python dependencies
```bash
cd restaurant-management-system
pip install -r requirements.txt
```

### 3. Create the database
Open your MySQL client and run:
```bash
mysql -u root -p < sql/schema.sql
```
This creates the `restaurant_management` database, all 7 tables, and
inserts sample data — **including 5 ready-to-use login accounts**
(see credentials below). Their passwords are already hashed with
Werkzeug, so you can log in immediately without extra steps.

### 4. Configure the database connection
Open `config/db_config.py` and update the credentials to match your
MySQL setup:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",          # <-- your MySQL password
    "database": "restaurant_management"
}
```

### 5. Run the application
```bash
python app.py
```
Visit **http://127.0.0.1:5000** in your browser.

---

## 🔑 Sample Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@restaurant.com | admin123 |
| Staff | ravi.staff@restaurant.com | staff123 |
| Staff | priya.staff@restaurant.com | staff123 |
| User | arjun@example.com | user123 |
| User | sneha@example.com | user123 |

New customers can also self-register via the **Register** link on the
login page (this creates a `role = 'user'` account only). Staff and
Admin accounts are created by the Admin from **Manage Staff**.

---

## ✅ Feature Checklist

**User:** Register/Login, view menu, order food, book a table, view
tables, pay parking (Bike/Car), view my orders, view my bookings, view
profile, logout.

**Staff:** Login, dashboard with stats, add/edit/delete food items,
toggle availability, view & confirm/cancel table bookings, mark tables
Available/Booked, view customer orders, update order status
(Pending → Preparing → Ready → Delivered).

**Admin:** Login, dashboard with total sales, food order history,
table booking history, parking payment history, manage users, manage
staff (create/remove), simple reports (top-selling items, order/booking
status breakdown).

---

## 🧪 Testing Instructions

This project was tested end-to-end before delivery:

1. **Auth:** registered a new user, logged in as each of the 3 roles,
   confirmed role-based redirects work correctly.
2. **Access control:** confirmed a logged-in "user" is redirected away
   from `/staff/...` and `/admin/...` routes, and that anonymous
   visitors are redirected to `/login`.
3. **User flows:** placed a food order (multi-item), booked a table,
   made a parking payment — all verified against the database.
4. **Staff flows:** added a food item, updated an order's status,
   confirmed a booking, toggled a table's status — all verified.
5. **Admin flows:** created a new staff account, and loaded the
   reports/order-history/booking-history/parking-history/manage-users
   pages — all returned HTTP 200 with correct data.

### To test it yourself
1. Follow the Setup Instructions above.
2. Log in with each sample account from the credentials table.
3. Try each feature from the checklist above.
4. Check the terminal running `python app.py` for any errors — with a
   correctly configured `db_config.py`, none should appear.

### Common issues
| Problem | Fix |
|---|---|
| `Database connection failed` on every page | Check `config/db_config.py` credentials and that MySQL is running |
| `Access denied for user 'root'@'localhost'` | Update the `password` field in `db_config.py`, or create a dedicated MySQL user |
| Login fails with correct sample password | Make sure you imported `sql/schema.sql` fresh — it contains pre-hashed passwords |
| Port 5000 already in use | Stop other running Flask apps, or change the port in `app.run(debug=True, port=5001)` |

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3 (custom, no framework), Vanilla JavaScript
- **Backend:** Python 3 + Flask (Blueprints for modular routing)
- **Database:** MySQL / MariaDB
- **Auth:** Flask sessions + Werkzeug password hashing

---

## 📌 Notes for Extension

- Passwords are hashed with `werkzeug.security.generate_password_hash`.
- Session-based auth (`session['user_id']`, `session['role']`) drives
  the `@login_required(role=...)` decorator in `routes/decorators.py`.
- To add a new page: create the route in the relevant `routes/*.py`
  file, add a template extending the matching `*_base.html`, and add a
  sidebar link in `templates/shared/<role>_base.html`.
