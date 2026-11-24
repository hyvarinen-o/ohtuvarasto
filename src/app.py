"""Flask web application for managing warehouse inventories."""

import math

from flask import (
    Blueprint,
    Flask,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from varasto import Varasto

warehouse_routes = Blueprint("warehouse", __name__)

@warehouse_routes.get("/")
def index():
    """Show every warehouse and its inventory."""
    warehouses = current_app.config["WAREHOUSES"]
    return render_template("index.html", warehouses=warehouses.values())


@warehouse_routes.post("/warehouses")
def create_warehouse():  # pylint: disable=too-many-statements
    """Create a warehouse from the submitted form."""
    name = request.form.get("name", "").strip()
    capacity = parse_amount(request.form.get("capacity"))
    initial_stock = parse_amount(request.form.get("initial_stock", "0"))

    if not name:
        flash("Warehouse name is required.", "error")
    elif capacity is None or capacity <= 0:
        flash("Capacity must be a positive number.", "error")
    elif initial_stock is None or initial_stock < 0:
        flash("Initial inventory must be zero or greater.", "error")
    elif initial_stock > capacity:
        flash("Initial inventory cannot exceed warehouse capacity.", "error")
    elif any(
        item["name"].casefold() == name.casefold()
        for item in current_app.config["WAREHOUSES"].values()
    ):
        flash("A warehouse with that name already exists.", "error")
    else:
        warehouse_id = current_app.config["NEXT_WAREHOUSE_ID"]
        current_app.config["NEXT_WAREHOUSE_ID"] += 1
        current_app.config["WAREHOUSES"][warehouse_id] = {
            "id": warehouse_id,
            "name": name,
            "inventory": Varasto(capacity, initial_stock),
        }
        flash(f"Warehouse '{name}' created.", "success")

    return redirect(url_for("warehouse.index"))


@warehouse_routes.post("/warehouses/<int:warehouse_id>/<action>")
def update_inventory(warehouse_id, action):  # pylint: disable=too-many-statements
    """Add items to or take items from a warehouse."""
    warehouse = current_app.config["WAREHOUSES"].get(warehouse_id)
    amount = parse_amount(request.form.get("amount"))

    if warehouse is None:
        flash("Warehouse not found.", "error")
    elif action not in ("add", "take"):
        flash("Unknown inventory operation.", "error")
    elif amount is None or amount <= 0:
        flash("Amount must be a positive number.", "error")
    elif action == "add":
        inventory = warehouse["inventory"]
        added = min(amount, inventory.paljonko_mahtuu())
        inventory.lisaa_varastoon(amount)
        message = f"Added {format_amount(added)} to {warehouse['name']}."
        flash(message, "success")
    else:
        removed = warehouse["inventory"].ota_varastosta(amount)
        flash(
            f"Took {format_amount(removed)} from {warehouse['name']}.",
            "success",
        )

    return redirect(url_for("warehouse.index"))


def create_app():
    """Create the warehouse application."""
    application = Flask(__name__)
    application.config["SECRET_KEY"] = "warehouse-app-development-key"
    application.config["WAREHOUSES"] = {}
    application.config["NEXT_WAREHOUSE_ID"] = 1
    application.jinja_env.filters["amount"] = format_amount
    application.register_blueprint(warehouse_routes)
    return application


def parse_amount(value):
    """Parse a finite number from a form field, returning None if invalid."""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    return amount if math.isfinite(amount) else None


def format_amount(amount):
    """Format integral quantities without a trailing decimal part."""
    return str(int(amount)) if amount.is_integer() else str(amount)


if __name__ == "__main__":
    create_app().run(debug=True)
