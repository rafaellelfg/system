from flask import render_template, request, redirect

from database import get_db, add_object, add_staff, add_client, get_specific_data, register_deal

def route( app) :
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