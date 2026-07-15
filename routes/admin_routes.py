"""
admin_routes.py
---------------
All routes for the "admin" role.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from config.db_config import get_db_connection
from routes.decorators import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------
# DASHBOARD - total sales + quick stats
# ---------------------------------------------------------------------
@admin_bp.route("/dashboard")
@login_required(role="admin")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT IFNULL(SUM(total_amount), 0) AS total FROM orders")
    total_food_sales = cursor.fetchone()["total"]

    cursor.execute("SELECT IFNULL(SUM(amount), 0) AS total FROM parking_payments")
    total_parking_sales = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'user'")
    total_users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'staff'")
    total_staff = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM orders")
    total_orders = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM table_bookings")
    total_bookings = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    stats = {
        "total_food_sales": total_food_sales,
        "total_parking_sales": total_parking_sales,
        "grand_total": float(total_food_sales) + float(total_parking_sales),
        "total_users": total_users,
        "total_staff": total_staff,
        "total_orders": total_orders,
        "total_bookings": total_bookings
    }
    return render_template("admin/dashboard.html", stats=stats)


# ---------------------------------------------------------------------
# FOOD ORDER HISTORY
# ---------------------------------------------------------------------
@admin_bp.route("/order-history")
@login_required(role="admin")
def order_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT o.*, u.full_name AS customer_name
           FROM orders o
           JOIN users u ON o.user_id = u.user_id
           ORDER BY o.order_date DESC"""
    )
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/order_history.html", orders=orders)


# ---------------------------------------------------------------------
# TABLE BOOKING HISTORY
# ---------------------------------------------------------------------
@admin_bp.route("/booking-history")
@login_required(role="admin")
def booking_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT tb.*, rt.table_number, u.full_name AS customer_name
           FROM table_bookings tb
           JOIN restaurant_tables rt ON tb.table_id = rt.table_id
           JOIN users u ON tb.user_id = u.user_id
           ORDER BY tb.booking_date DESC"""
    )
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/booking_history.html", bookings=bookings)


# ---------------------------------------------------------------------
# PARKING PAYMENT HISTORY
# ---------------------------------------------------------------------
@admin_bp.route("/parking-history")
@login_required(role="admin")
def parking_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT pp.*, u.full_name AS customer_name
           FROM parking_payments pp
           JOIN users u ON pp.user_id = u.user_id
           ORDER BY pp.payment_date DESC"""
    )
    payments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/parking_history.html", payments=payments)


# ---------------------------------------------------------------------
# MANAGE USERS (customers)
# ---------------------------------------------------------------------
@admin_bp.route("/manage-users")
@login_required(role="admin")
def manage_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE role = 'user' ORDER BY user_id DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/manage_users.html", users=users)


@admin_bp.route("/delete-user/<int:user_id>")
@login_required(role="admin")
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s AND role = 'user'", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("User removed.", "success")
    return redirect(url_for("admin.manage_users"))


# ---------------------------------------------------------------------
# MANAGE STAFF (admin creates staff accounts here)
# ---------------------------------------------------------------------
@admin_bp.route("/manage-staff", methods=["GET", "POST"])
@login_required(role="admin")
def manage_staff():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("An account with this email already exists.", "error")
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                """INSERT INTO users (full_name, email, password, phone, role)
                   VALUES (%s, %s, %s, %s, 'staff')""",
                (full_name, email, hashed_password, phone)
            )
            conn.commit()
            flash("Staff account created successfully!", "success")

    cursor.execute("SELECT * FROM users WHERE role = 'staff' ORDER BY user_id DESC")
    staff_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/manage_staff.html", staff_list=staff_list)


@admin_bp.route("/delete-staff/<int:user_id>")
@login_required(role="admin")
def delete_staff(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s AND role = 'staff'", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Staff account removed.", "success")
    return redirect(url_for("admin.manage_staff"))


# ---------------------------------------------------------------------
# SIMPLE REPORTS
# ---------------------------------------------------------------------
@admin_bp.route("/reports")
@login_required(role="admin")
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Best selling food items
    cursor.execute(
        """SELECT f.name, SUM(od.quantity) AS total_sold
           FROM order_details od
           JOIN food_items f ON od.food_id = f.food_id
           GROUP BY f.food_id ORDER BY total_sold DESC LIMIT 5"""
    )
    top_food = cursor.fetchall()

    # Orders grouped by status
    cursor.execute("SELECT status, COUNT(*) AS total FROM orders GROUP BY status")
    orders_by_status = cursor.fetchall()

    # Bookings grouped by status
    cursor.execute("SELECT status, COUNT(*) AS total FROM table_bookings GROUP BY status")
    bookings_by_status = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        "admin/reports.html",
        top_food=top_food,
        orders_by_status=orders_by_status,
        bookings_by_status=bookings_by_status
    )
