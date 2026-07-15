"""
user_routes.py
--------------
All routes for the "user" (customer) role.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config.db_config import get_db_connection
from routes.decorators import login_required

user_bp = Blueprint("user", __name__, url_prefix="/user")


# ---------------------------------------------------------------------
# DASHBOARD - shows available food items (home page for users)
# ---------------------------------------------------------------------
@user_bp.route("/dashboard")
@login_required(role="user")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM food_items WHERE availability = 'Available'")
    food_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("user/dashboard.html", food_items=food_items)


# ---------------------------------------------------------------------
# ORDER FOOD
# ---------------------------------------------------------------------
@user_bp.route("/order-food", methods=["GET", "POST"])
@login_required(role="user")
def order_food():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        # form sends parallel arrays: food_id[] and quantity[]
        food_ids = request.form.getlist("food_id")
        quantities = request.form.getlist("quantity")
        table_id = request.form.get("table_id") or None

        # Build a list of (food_id, qty) pairs where qty > 0
        items = [(int(f), int(q)) for f, q in zip(food_ids, quantities) if int(q) > 0]

        if not items:
            flash("Please select at least one food item with quantity.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for("user.order_food"))

        # Calculate total using current DB prices
        total_amount = 0
        for food_id, qty in items:
            cursor.execute("SELECT price FROM food_items WHERE food_id = %s", (food_id,))
            row = cursor.fetchone()
            if row:
                total_amount += float(row["price"]) * qty

        # Insert order
        cursor.execute(
            "INSERT INTO orders (user_id, table_id, total_amount, status) VALUES (%s, %s, %s, 'Pending')",
            (session["user_id"], table_id, total_amount)
        )
        order_id = cursor.lastrowid

        # Insert order details (one row per food item)
        for food_id, qty in items:
            cursor.execute("SELECT price FROM food_items WHERE food_id = %s", (food_id,))
            price = cursor.fetchone()["price"]
            cursor.execute(
                "INSERT INTO order_details (order_id, food_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, food_id, qty, price)
            )

        conn.commit()
        cursor.close()
        conn.close()
        flash("Order placed successfully!", "success")
        return redirect(url_for("user.my_orders"))

    # GET request: show the order form
    cursor.execute("SELECT * FROM food_items WHERE availability = 'Available'")
    food_items = cursor.fetchall()
    cursor.execute("SELECT * FROM restaurant_tables WHERE status = 'Available'")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("user/order_food.html", food_items=food_items, tables=tables)


# ---------------------------------------------------------------------
# VIEW AVAILABLE TABLES
# ---------------------------------------------------------------------
@user_bp.route("/view-tables")
@login_required(role="user")
def view_tables():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurant_tables ORDER BY table_number")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("user/view_tables.html", tables=tables)


# ---------------------------------------------------------------------
# BOOK A TABLE
# ---------------------------------------------------------------------
@user_bp.route("/book-table", methods=["GET", "POST"])
@login_required(role="user")
def book_table():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        table_id = request.form.get("table_id")
        booking_date = request.form.get("booking_date")
        booking_time = request.form.get("booking_time")
        guests = request.form.get("number_of_guests")

        cursor.execute(
            """INSERT INTO table_bookings (user_id, table_id, booking_date, booking_time, number_of_guests, status)
               VALUES (%s, %s, %s, %s, %s, 'Pending')""",
            (session["user_id"], table_id, booking_date, booking_time, guests)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Table booking request submitted!", "success")
        return redirect(url_for("user.my_bookings"))

    cursor.execute("SELECT * FROM restaurant_tables WHERE status = 'Available'")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("user/book_table.html", tables=tables)


# ---------------------------------------------------------------------
# PAY PARKING FEES
# ---------------------------------------------------------------------
PARKING_RATES = {"Bike": 20.00, "Car": 50.00}


@user_bp.route("/parking", methods=["GET", "POST"])
@login_required(role="user")
def parking():
    if request.method == "POST":
        vehicle_type = request.form.get("vehicle_type")
        amount = PARKING_RATES.get(vehicle_type, 0)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO parking_payments (user_id, vehicle_type, amount) VALUES (%s, %s, %s)",
            (session["user_id"], vehicle_type, amount)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Parking fee of ₹{amount} paid for {vehicle_type}.", "success")
        return redirect(url_for("user.parking"))

    return render_template("user/parking.html", rates=PARKING_RATES)


# ---------------------------------------------------------------------
# MY ORDERS
# ---------------------------------------------------------------------
@user_bp.route("/my-orders")
@login_required(role="user")
def my_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM orders WHERE user_id = %s ORDER BY order_date DESC",
        (session["user_id"],)
    )
    orders = cursor.fetchall()

    # For each order, fetch its line items
    for order in orders:
        cursor.execute(
            """SELECT od.quantity, od.price, f.name
               FROM order_details od
               JOIN food_items f ON od.food_id = f.food_id
               WHERE od.order_id = %s""",
            (order["order_id"],)
        )
        order["items"] = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("user/my_orders.html", orders=orders)


# ---------------------------------------------------------------------
# MY BOOKINGS
# ---------------------------------------------------------------------
@user_bp.route("/my-bookings")
@login_required(role="user")
def my_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT tb.*, rt.table_number, rt.capacity
           FROM table_bookings tb
           JOIN restaurant_tables rt ON tb.table_id = rt.table_id
           WHERE tb.user_id = %s ORDER BY tb.booking_date DESC""",
        (session["user_id"],)
    )
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("user/my_bookings.html", bookings=bookings)


# ---------------------------------------------------------------------
# PROFILE
# ---------------------------------------------------------------------
@user_bp.route("/profile", methods=["GET", "POST"])
@login_required(role="user")
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        full_name = request.form.get("full_name")
        phone = request.form.get("phone")
        address = request.form.get("address")

        cursor.execute(
            "UPDATE users SET full_name = %s, phone = %s, address = %s WHERE user_id = %s",
            (full_name, phone, address, session["user_id"])
        )
        conn.commit()
        session["full_name"] = full_name
        flash("Profile updated successfully!", "success")

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (session["user_id"],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("user/profile.html", user=user)
