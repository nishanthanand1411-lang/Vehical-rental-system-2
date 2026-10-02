from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import date

app = Flask(__name__)

# =========================================================
# DATABASE
# =========================================================

DATABASE = os.path.join(app.root_path, "rental.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_columns(conn, table_name):
    """Return column names for a SQLite table."""
    rows = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return [row["name"] for row in rows]


def add_column_if_missing(conn, table_name, column_name, definition):
    """Add a column if it does not already exist."""
    columns = get_columns(conn, table_name)

    if column_name not in columns:
        conn.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"
        )


# =========================================================
# CREATE / UPDATE DATABASE
# =========================================================

def create_database():

    conn = get_db_connection()

    # =====================================================
    # VEHICLES TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            registration_no TEXT NOT NULL,
            year INTEGER NOT NULL,
            service_date TEXT NOT NULL,
            insurance_date TEXT NOT NULL,
            status TEXT DEFAULT 'Available',
            customer_name TEXT
        )
    """)

    # =====================================================
    # CUSTOMERS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT,
            licence_no TEXT NOT NULL
        )
    """)

    # =====================================================
    # OWNERS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT
        )
    """)

    # =====================================================
    # RENTALS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id TEXT,
            customer_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            vehicle_id INTEGER NOT NULL,
            rented_date TEXT NOT NULL,
            ending_date TEXT,
            starting_km REAL,
            ending_km REAL,
            rental_amount REAL,
            condition_before TEXT,
            condition_after TEXT,
            remarks TEXT,
            status TEXT DEFAULT 'Active'
        )
    """)

    conn.commit()

    # =====================================================
    # MIGRATE OLD VEHICLES TABLE
    # =====================================================

    add_column_if_missing(
        conn, "vehicles", "name", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "vehicles", "model", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "vehicles", "vehicle_type", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "vehicles", "registration_no", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "vehicles", "year", "INTEGER DEFAULT 0"
    )

    add_column_if_missing(
        conn, "vehicles", "service_date", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "vehicles", "insurance_date", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "vehicles", "status", "TEXT DEFAULT 'Available'"
    )

    add_column_if_missing(
        conn, "vehicles", "customer_name", "TEXT DEFAULT ''"
    )

    # =====================================================
    # MIGRATE OLD CUSTOMERS TABLE
    # =====================================================

    add_column_if_missing(
        conn, "customers", "customer_id", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "customers", "customer_name", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "customers", "phone", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "customers", "email", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "customers", "address", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "customers", "licence_no", "TEXT DEFAULT ''"
    )

    # =====================================================
    # MIGRATE OLD OWNERS TABLE
    # =====================================================

    add_column_if_missing(
        conn, "owners", "owner_id", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "owners", "owner_name", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "owners", "phone", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "owners", "email", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "owners", "address", "TEXT DEFAULT ''"
    )

    # =====================================================
    # MIGRATE OLD RENTALS TABLE
    # =====================================================

    add_column_if_missing(
        conn, "rentals", "rental_id", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "rentals", "customer_id", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "rentals", "customer_name", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "rentals", "vehicle_id", "INTEGER DEFAULT 0"
    )

    add_column_if_missing(
        conn, "rentals", "rented_date", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "rentals", "ending_date", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "rentals", "starting_km", "REAL DEFAULT 0"
    )

    add_column_if_missing(
        conn, "rentals", "ending_km", "REAL DEFAULT 0"
    )

    add_column_if_missing(
        conn, "rentals", "rental_amount", "REAL DEFAULT 0"
    )

    add_column_if_missing(
        conn, "rentals", "condition_before", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "rentals", "condition_after", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "rentals", "remarks", "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        conn, "rentals", "status", "TEXT DEFAULT 'Active'"
    )

    conn.commit()
    conn.close()


# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
def home():

    conn = get_db_connection()

    vehicles = conn.execute("""
        SELECT *
        FROM vehicles
        ORDER BY id DESC
    """).fetchall()

    customers = conn.execute("""
        SELECT *
        FROM customers
        ORDER BY id DESC
    """).fetchall()

    owners = conn.execute("""
        SELECT *
        FROM owners
        ORDER BY id DESC
    """).fetchall()

    rentals = conn.execute("""
        SELECT *
        FROM rentals
        ORDER BY id DESC
    """).fetchall()

    total = conn.execute("""
        SELECT COUNT(*)
        FROM vehicles
    """).fetchone()[0]

    available = conn.execute("""
        SELECT COUNT(*)
        FROM vehicles
        WHERE status = 'Available'
    """).fetchone()[0]

    rented = conn.execute("""
        SELECT COUNT(*)
        FROM vehicles
        WHERE status = 'Rented'
    """).fetchone()[0]

    total_customers = conn.execute("""
        SELECT COUNT(*)
        FROM customers
    """).fetchone()[0]

    total_owners = conn.execute("""
        SELECT COUNT(*)
        FROM owners
    """).fetchone()[0]

    active_rentals = conn.execute("""
        SELECT COUNT(*)
        FROM rentals
        WHERE status = 'Active'
    """).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        vehicles=vehicles,
        customers=customers,
        owners=owners,
        rentals=rentals,
        total=total,
        available=available,
        rented=rented,
        total_customers=total_customers,
        total_owners=total_owners,
        active_rentals=active_rentals,
        today=date.today().isoformat()
    )


# =========================================================
# CUSTOMER SECTION
# =========================================================

@app.route("/add_customer", methods=["POST"])
def add_customer():

    customer_id = request.form.get("customer_id", "").strip()
    customer_name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()
    licence_no = request.form.get("licence_no", "").strip()

    if not customer_id or not customer_name or not phone or not licence_no:
        return """
        <h2>Please fill in all required customer fields.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    conn = get_db_connection()

    # Check Customer ID manually
    existing_customer = conn.execute("""
        SELECT id
        FROM customers
        WHERE customer_id = ?
    """, (customer_id,)).fetchone()

    if existing_customer:
        conn.close()

        return """
        <h2>Customer ID already exists.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    # Check Driving Licence manually
    existing_licence = conn.execute("""
        SELECT id
        FROM customers
        WHERE licence_no = ?
    """, (licence_no,)).fetchone()

    if existing_licence:
        conn.close()

        return """
        <h2>Driving Licence Number already exists.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    conn.execute("""
        INSERT INTO customers
        (
            customer_id,
            customer_name,
            phone,
            email,
            address,
            licence_no
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        customer_name,
        phone,
        email,
        address,
        licence_no
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home") + "#customer")


# =========================================================
# DELETE CUSTOMER
# =========================================================

@app.route("/delete_customer/<int:customer_id>")
def delete_customer(customer_id):

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM customers
        WHERE id = ?
    """, (customer_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("home") + "#customer")


# =========================================================
# OWNER SECTION
# =========================================================

@app.route("/add_owner", methods=["POST"])
def add_owner():

    owner_id = request.form.get("owner_id", "").strip()
    owner_name = request.form.get("owner_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()

    if not owner_id or not owner_name or not phone:
        return """
        <h2>Please fill in all required owner fields.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    conn = get_db_connection()

    existing_owner = conn.execute("""
        SELECT id
        FROM owners
        WHERE owner_id = ?
    """, (owner_id,)).fetchone()

    if existing_owner:
        conn.close()

        return """
        <h2>Owner ID already exists.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    conn.execute("""
        INSERT INTO owners
        (
            owner_id,
            owner_name,
            phone,
            email,
            address
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        owner_id,
        owner_name,
        phone,
        email,
        address
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home") + "#owner")


# =========================================================
# DELETE OWNER
# =========================================================

@app.route("/delete_owner/<int:owner_id>")
def delete_owner(owner_id):

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM owners
        WHERE id = ?
    """, (owner_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("home") + "#owner")


# =========================================================
# VEHICLE SECTION
# =========================================================

@app.route("/add_vehicle", methods=["POST"])
def add_vehicle():

    name = request.form.get("name", "").strip()
    model = request.form.get("model", "").strip()
    vehicle_type = request.form.get("vehicle_type", "").strip()
    registration_no = request.form.get("registration_no", "").strip()
    year = request.form.get("year", "").strip()
    service_date = request.form.get("service_date", "").strip()
    insurance_date = request.form.get("insurance_date", "").strip()

    if (
        not name
        or not model
        or not vehicle_type
        or not registration_no
        or not year
        or not service_date
        or not insurance_date
    ):
        return """
        <h2>Please fill in all vehicle fields.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    conn = get_db_connection()

    existing_vehicle = conn.execute("""
        SELECT id
        FROM vehicles
        WHERE registration_no = ?
    """, (registration_no,)).fetchone()

    if existing_vehicle:
        conn.close()

        return """
        <h2>Registration number already exists.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    conn.execute("""
        INSERT INTO vehicles
        (
            name,
            model,
            vehicle_type,
            registration_no,
            year,
            service_date,
            insurance_date,
            status,
            customer_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Available', NULL)
    """, (
        name,
        model,
        vehicle_type,
        registration_no,
        year,
        service_date,
        insurance_date
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home") + "#vehicle")


# =========================================================
# DELETE VEHICLE
# =========================================================

@app.route("/delete_vehicle/<int:vehicle_id>")
def delete_vehicle(vehicle_id):

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM vehicles
        WHERE id = ?
    """, (vehicle_id,))

    conn.execute("""
        DELETE FROM rentals
        WHERE vehicle_id = ?
    """, (vehicle_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("home") + "#vehicle")


# =========================================================
# RENT VEHICLE
# =========================================================

@app.route("/rent_vehicle/<int:vehicle_id>")
def rent_vehicle(vehicle_id):

    conn = get_db_connection()

    vehicle = conn.execute("""
        SELECT *
        FROM vehicles
        WHERE id = ?
    """, (vehicle_id,)).fetchone()

    conn.close()

    if vehicle is None:
        return "Vehicle not found."

    if vehicle["status"] == "Rented":
        return "Vehicle is already rented."

    return redirect(url_for("home") + "#rental")


# =========================================================
# SAVE RENTAL
# =========================================================

@app.route("/confirm_rental", methods=["POST"])
def confirm_rental():

    rental_id = request.form.get("rental_id", "").strip()
    customer_id = request.form.get("customer_id", "").strip()
    vehicle_id = request.form.get("vehicle_id", "").strip()
    rented_date = request.form.get("rented_date", "").strip()
    ending_date = request.form.get("ending_date", "").strip()
    starting_km = request.form.get("starting_km", "").strip()
    rental_amount = request.form.get("rental_amount", "").strip()
    condition_before = request.form.get(
        "condition_before", ""
    ).strip()
    remarks = request.form.get("remarks", "").strip()

    if not customer_id or not vehicle_id or not rented_date:
        return """
        <h2>Customer, vehicle and rented date are required.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    conn = get_db_connection()

    customer = conn.execute("""
        SELECT *
        FROM customers
        WHERE customer_id = ?
    """, (customer_id,)).fetchone()

    if customer is None:
        conn.close()

        return """
        <h2>Customer ID not found.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    vehicle = conn.execute("""
        SELECT *
        FROM vehicles
        WHERE id = ?
    """, (vehicle_id,)).fetchone()

    if vehicle is None:
        conn.close()

        return """
        <h2>Vehicle not found.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    if vehicle["status"] == "Rented":
        conn.close()

        return """
        <h2>This vehicle is already rented.</h2>
        <br>
        <a href="/">Go Back</a>
        """

    conn.execute("""
        INSERT INTO rentals
        (
            rental_id,
            customer_id,
            customer_name,
            vehicle_id,
            rented_date,
            ending_date,
            starting_km,
            rental_amount,
            condition_before,
            remarks,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
    """, (
        rental_id,
        customer["customer_id"],
        customer["customer_name"],
        vehicle["id"],
        rented_date,
        ending_date,
        starting_km if starting_km else None,
        rental_amount if rental_amount else None,
        condition_before,
        remarks
    ))

    conn.execute("""
        UPDATE vehicles
        SET status = 'Rented',
            customer_name = ?
        WHERE id = ?
    """, (
        customer["customer_name"],
        vehicle["id"]
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home") + "#vehicle")


# =========================================================
# RETURN VEHICLE
# =========================================================

@app.route("/return_vehicle/<int:vehicle_id>")
def return_vehicle(vehicle_id):

    conn = get_db_connection()

    rental = conn.execute("""
        SELECT *
        FROM rentals
        WHERE vehicle_id = ?
          AND status = 'Active'
        ORDER BY id DESC
        LIMIT 1
    """, (vehicle_id,)).fetchone()

    conn.execute("""
        UPDATE vehicles
        SET status = 'Available',
            customer_name = NULL
        WHERE id = ?
    """, (vehicle_id,))

    if rental:

        conn.execute("""
            UPDATE rentals
            SET status = 'Completed'
            WHERE id = ?
        """, (rental["id"],))

    conn.commit()
    conn.close()

    return redirect(url_for("home") + "#vehicle")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)