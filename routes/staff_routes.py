"""
staff_routes.py
---------------
All routes for the "staff" role.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config.db_config import get_db_connection
from routes.decorators import login_required

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


# ---------------------------------------------------------------------
# DASHBOARD - quick overview cards
# ---------------------------------------------------------------------
@staff_bp.route("/dashboard")
@login_required(role="staff")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM food_items")
    total_food = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM orders WHERE status != 'Delivered'")
    pending_orders = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM table_bookings WHERE status = 'Pending'")
    pending_bookings = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM restaurant_tables WHERE status = 'Available'")
    available_tables = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    stats = {
        "total_food": total_food,
        "pending_orders": pending_orders,
        "pending_bookings": pending_bookings,
        "available_tables": available_tables
    }
    return render_template("staff/dashboard.html", stats=stats)


# ---------------------------------------------------------------------
# MANAGE FOOD - Add / Edit / Delete / Toggle availability
# ---------------------------------------------------------------------
@staff_bp.route("/manage-food", methods=["GET", "POST"])
@login_required(role="staff")
def manage_food():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        cursor.execute(
            """INSERT INTO food_items (name, description, price, category, added_by)
               VALUES (%s, %s, %s, %s, %s)""",
            (name, description, price, category, session["user_id"])
        )
        conn.commit()
        flash("Food item added successfully!", "success")

    cursor.execute("SELECT * FROM food_items ORDER BY food_id DESC")
    food_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("staff/manage_food.html", food_items=food_items)


@staff_bp.route("/edit-food/<int:food_id>", methods=["GET", "POST"])
@login_required(role="staff")
def edit_food(food_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        cursor.execute(
            """UPDATE food_items SET name=%s, description=%s, price=%s, category=%s
               WHERE food_id=%s""",
            (name, description, price, category, food_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Food item updated successfully!", "success")
        return redirect(url_for("staff.manage_food"))

    cursor.execute("SELECT * FROM food_items WHERE food_id = %s", (food_id,))
    food = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("staff/edit_food.html", food=food)


@staff_bp.route("/delete-food/<int:food_id>")
@login_required(role="staff")
def delete_food(food_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_items WHERE food_id = %s", (food_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Food item deleted.", "success")
    return redirect(url_for("staff.manage_food"))


@staff_bp.route("/toggle-food/<int:food_id>")
@login_required(role="staff")
def toggle_food(food_id):
    """Flip a food item's availability between Available <-> Unavailable."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT availability FROM food_items WHERE food_id = %s", (food_id,))
    current = cursor.fetchone()["availability"]
    new_status = "Unavailable" if current == "Available" else "Available"
    cursor.execute("UPDATE food_items SET availability = %s WHERE food_id = %s", (new_status, food_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f"Food item marked as {new_status}.", "success")
    return redirect(url_for("staff.manage_food"))


# ---------------------------------------------------------------------
# VIEW ALL TABLE BOOKINGS + ASSIGN TABLES
# ---------------------------------------------------------------------
@staff_bp.route("/bookings")
@login_required(role="staff")
def bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT tb.*, rt.table_number, u.full_name AS customer_name
           FROM table_bookings tb
           JOIN restaurant_tables rt ON tb.table_id = rt.table_id
           JOIN users u ON tb.user_id = u.user_id
           ORDER BY tb.booking_date DESC"""
    )
    all_bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("staff/bookings.html", bookings=all_bookings)


@staff_bp.route("/confirm-booking/<int:booking_id>")
@login_required(role="staff")
def confirm_booking(booking_id):
    """Staff confirms a booking and assigns themselves as the handling staff."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE table_bookings SET status = 'Confirmed', assigned_staff_id = %s WHERE booking_id = %s",
        (session["user_id"], booking_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash("Booking confirmed.", "success")
    return redirect(url_for("staff.bookings"))


@staff_bp.route("/cancel-booking/<int:booking_id>")
@login_required(role="staff")
def cancel_booking(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE table_bookings SET status = 'Cancelled' WHERE booking_id = %s", (booking_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Booking cancelled.", "success")
    return redirect(url_for("staff.bookings"))


# ---------------------------------------------------------------------
# MANAGE TABLES - mark Available / Booked
# ---------------------------------------------------------------------
@staff_bp.route("/manage-tables")
@login_required(role="staff")
def manage_tables():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurant_tables ORDER BY table_number")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("staff/manage_tables.html", tables=tables)


@staff_bp.route("/toggle-table/<int:table_id>")
@login_required(role="staff")
def toggle_table(table_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM restaurant_tables WHERE table_id = %s", (table_id,))
    current = cursor.fetchone()["status"]
    new_status = "Booked" if current == "Available" else "Available"
    cursor.execute("UPDATE restaurant_tables SET status = %s WHERE table_id = %s", (new_status, table_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f"Table marked as {new_status}.", "success")
    return redirect(url_for("staff.manage_tables"))


# ---------------------------------------------------------------------
# VIEW CUSTOMER ORDERS + UPDATE STATUS
# ---------------------------------------------------------------------
@staff_bp.route("/orders")
@login_required(role="staff")
def orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT o.*, u.full_name AS customer_name
           FROM orders o
           JOIN users u ON o.user_id = u.user_id
           ORDER BY o.order_date DESC"""
    )
    all_orders = cursor.fetchall()

    for order in all_orders:
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
    return render_template("staff/orders.html", orders=all_orders)


@staff_bp.route("/update-order-status/<int:order_id>", methods=["POST"])
@login_required(role="staff")
def update_order_status(order_id):
    new_status = request.form.get("status")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Order status updated.", "success")
    return redirect(url_for("staff.orders"))
