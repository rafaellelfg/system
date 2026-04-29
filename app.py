import psycopg2
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.secret_key = "secret"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db():
    """Create and return a new database connection and cursor."""
    conn = psycopg2.connect(
        dbname="---" #use here ur database
        user="---- ", # use here ur user id
        password="---", # use here ur password
        host="127.0.0.1",
        port="---" # use here ur port
    )
    return conn, conn.cursor()


# ==========================================
# BLOCK 1: Data operations
# ==========================================

def add_object(cursor, conn, address, total_area, type_id, price):
    """
    Add a new property object to the database.
    All new objects are assigned status 'Available' (status_id = 1) by default.
    """
    status_id = '1'  # Default status: "Available"

    sql_command = """
    INSERT INTO objects (address, total_area, type_id, price, status_id)
    VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    # "%s" was using to avoid SQL injects
    try:
        cursor.execute(sql_command, (address, total_area, type_id, price, status_id))
        new_id = cursor.fetchone()[0]
        conn.commit()
        return f"[+] Property added successfully. ID: {new_id}"
    except Exception as e:
        conn.rollback()
        return f"[-] Error adding property: {e}"


def add_client(cursor, conn, name, phone, email, client_type_choice):
    """
    Register a new client (individual or company) in the database.
    client_type_choice: "1" = person, "2" = company
    """
    client_type = "person"
    if client_type_choice == "2":
        client_type = "company"

    sql_command = """
    INSERT INTO clients (name, phone, email, type)
    VALUES (%s, %s, %s, %s) RETURNING id;
    """

    try:
        cursor.execute(sql_command, (name, phone, email, client_type))
        new_id = cursor.fetchone()[0]
        conn.commit()
        return f"[+] Client '{name}' registered successfully. ID: {new_id}"
    except Exception as e:
        conn.rollback()
        return f"[-] Error adding client: {e}"


def register_deal(cursor, conn, object_id, client_id, employee_id, amount, action):
    """
    Register a new deal (rental or sale) and automatically update the property status.
    action: "1" = Rental, "2" = Sale
    This operation is atomic — both the deal log and the status update are committed together.
    """
    if action == "1":
        deal_type = "Rental"
        new_status_id = '2'  # Status: "Rented"
    elif action == "2":
        deal_type = "Sale"
        new_status_id = '3'  # Status: "Sold"
    else:
        return "[-] Invalid deal type. Operation cancelled."

    try:
        # STEP 1: Log the deal in the deals table
        sql_insert_deal = """
        INSERT INTO deals (object_id, client_id, employee_id, deal_type, total_amount)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(sql_insert_deal, (object_id, client_id, employee_id, deal_type, amount))

        # STEP 2: Update the property status automatically
        sql_update_object = """
        UPDATE objects SET status_id = %s WHERE id = %s;
        """
        cursor.execute(sql_update_object, (new_status_id, object_id))

        # Commit both operations together as a single transaction
        conn.commit()
        return f"[+] Deal '{deal_type}' registered successfully. Property #{object_id} status updated."

    except Exception as e:
        # If anything fails, roll back the entire transaction
        conn.rollback()
        return f"[-] Error registering deal: {e}"


def add_staff(cursor, conn, full_name, position):
    """Add a new employee to the system."""
    sql_command = """
    INSERT INTO employees (full_name, position)
    VALUES (%s, %s) RETURNING id;
    """

    try:
        cursor.execute(sql_command, (full_name, position))
        new_id = cursor.fetchone()[0]
        conn.commit()
        return f"[+] Employee '{full_name}' added to the system. ID: {new_id}"
    except Exception as e:
        conn.rollback()
        return f"[-] Error adding employee: {e}"


def get_specific_data(cursor, choice):
    """
    Fetch a specific category of data from the database.
    choice:
        '1' = Employees
        '2' = Active properties (not deleted)
        '3' = Clients
        '4' = Archived properties (soft-deleted)
    """
    try:
        if choice == '1':
            # Fetch all employees
            cursor.execute("SELECT id, full_name, position FROM employees ORDER BY id;")
            data = cursor.fetchall()
            return {"type": "staff", "data": data, "error": None}

        elif choice == '2':
            # Fetch only active (non-deleted) properties
            cursor.execute("""
                SELECT id, address, total_area, price, type_id, status_id, is_deleted
                FROM objects
                WHERE is_deleted = FALSE
                ORDER BY id;
            """)
            data = cursor.fetchall()
            return {"type": "objects", "data": data, "error": None}

        elif choice == '3':
            # Fetch all clients
            cursor.execute("SELECT id, name, phone, type FROM clients ORDER BY id;")
            data = cursor.fetchall()
            return {"type": "clients", "data": data, "error": None}

        elif choice == '4':
            # Fetch archived (soft-deleted) properties
            cursor.execute("""
                SELECT id, address, total_area, price, type_id, status_id, is_deleted
                FROM objects
                WHERE is_deleted = TRUE
                ORDER BY id;
            """)
            data = cursor.fetchall()
            return {"type": "archive", "data": data, "error": None}

        else:
            return {"type": "unknown", "data": [], "error": "Invalid category selection."}

    except Exception as e:
        return {"type": "error", "data": [], "error": f"Error fetching data: {e}"}


# ==========================================
# BLOCK 2: Flask routes
# ==========================================

@app.route("/")
def index():
    """Landing page — role selection."""
    return render_template("index.html")


# --- Manager routes ---

@app.route("/manager/add_object", methods=["GET", "POST"])
def route_add_object():
    """Handle adding a new property object."""
    message = None
    if request.method == "POST":
        conn, cursor = get_db()
        message = add_object(
            cursor, conn,
            request.form["address"],
            request.form["total_area"],
            request.form["type_id"],
            request.form["price"]
        )
        cursor.close()
        conn.close()
    return render_template("add_object.html", message=message)


@app.route("/manager/add_staff", methods=["GET", "POST"])
def route_add_staff():
    """Handle adding a new employee."""
    message = None
    if request.method == "POST":
        conn, cursor = get_db()
        message = add_staff(
            cursor, conn,
            request.form["full_name"],
            request.form["position"]
        )
        cursor.close()
        conn.close()
    return render_template("add_staff.html", message=message)


@app.route("/manager/add_client", methods=["GET", "POST"])
def route_add_client():
    """Handle registering a new client."""
    message = None
    if request.method == "POST":
        conn, cursor = get_db()
        message = add_client(
            cursor, conn,
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["client_type"]
        )
        cursor.close()
        conn.close()
    return render_template("add_client.html", message=message)


@app.route("/manager/see_all", methods=["GET"])
def route_view_all():
    """
    Display a selected category of records.
    The 'choice' query parameter determines which category is shown.
    """
    data_type = None
    data_list = []
    message = None

    if "choice" in request.args:
        conn, cursor = get_db()

        result = get_specific_data(cursor, request.args["choice"])

        # Unpack the result dictionary into template variables
        data_type = result["type"]
        data_list = result["data"]
        message = result["error"]

        cursor.close()
        conn.close()

    return render_template(
        "view_all.html",
        data_type=data_type,
        data_list=data_list,
        message=message
    )


@app.route("/manager/delete_object/<int:obj_id>", methods=["POST"])
def route_soft_delete(obj_id):
    """
    Soft-delete a property by setting is_deleted = TRUE.
    The record is preserved in the database and can be restored later.
    """
    conn, cursor = get_db()
    try:
        cursor.execute("UPDATE objects SET is_deleted = TRUE WHERE id = %s", (obj_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    # Redirect back to the active properties list
    return redirect("/manager/see_all?choice=2")


@app.route("/manager/restore_object/<int:obj_id>", methods=["POST"])
def route_restore_object(obj_id):
    """
    Restore a previously soft-deleted property by setting is_deleted = FALSE.
    """
    conn, cursor = get_db()
    try:
        cursor.execute("UPDATE objects SET is_deleted = FALSE WHERE id = %s", (obj_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    # Redirect back to the active properties list
    return redirect("/manager/see_all?choice=2")


# --- Realtor routes ---

@app.route("/realtor/register_deal", methods=["GET", "POST"])
def route_register_deal():
    """Handle registering a new rental or sale deal."""
    message = None
    if request.method == "POST":
        conn, cursor = get_db()
        message = register_deal(
            cursor, conn,
            request.form["object_id"],
            request.form["client_id"],
            request.form["employee_id"],
            request.form["amount"],
            request.form["action"]
        )
        cursor.close()
        conn.close()
    return render_template("register_deal.html", message=message)


# ==========================================
# BLOCK 3: Entry point
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
