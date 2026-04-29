import psycopg2
# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db():
    """Create and return a new database connection and cursor."""
    conn = psycopg2.connect(
        dbname="robert_db",
        user="robert",
        password="sosal1337",
        host="127.0.0.1",
        port="1337"
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
