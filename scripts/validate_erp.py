
import csv
from datetime import date
from pathlib import Path

# Locate the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define the ERP data directory
ERP_DIR = PROJECT_ROOT / "data" / "erp"


def load_csv(filename):
    """Load a CSV file from the ERP data directory."""

    file_path = ERP_DIR / filename

    with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def validate_unique_ids(suppliers, purchase_orders, goods_receipts):
    """
    Check uniqueness of entity and line identifiers.
    """

    errors = []

    # Supplier IDs
    supplier_ids = [s["supplier_id"] for s in suppliers]

    if len(supplier_ids) != len(set(supplier_ids)):
        errors.append("Duplicate supplier IDs detected")

    # Purchase order IDs (one ID per order, not per line)
    po_ids = [order["po_id"] for order in purchase_orders]

    unique_po_ids = set(po_ids)

    # Receipt IDs
    receipt_ids = [r["receipt_id"] for r in goods_receipts]

    if len(receipt_ids) != len(set(receipt_ids)):
        errors.append("Duplicate receipt IDs detected")

    # Duplicate purchase order lines
    line_keys = [
        (order["po_id"], order["line_no"])
        for order in purchase_orders
    ]

    if len(line_keys) != len(set(line_keys)):
        errors.append("Duplicate purchase order lines detected")

    return errors


def validate_supplier_references(suppliers, purchase_orders):
    """
    Check that every purchase order references
    an existing supplier.
    """

    supplier_ids = {
        supplier["supplier_id"]
        for supplier in suppliers
    }

    errors = []

    for order in purchase_orders:

        supplier_id = order["supplier_id"]

        if supplier_id not in supplier_ids:
            errors.append(
                f"Purchase order {order['po_id']} "
                f"references unknown supplier {supplier_id}"
            )

    return errors


def validate_goods_receipts(purchase_orders, goods_receipts):
    """
    Validate goods receipts against purchase order lines.
    """

    order_lines = {
        (order["po_id"], order["line_no"]): order
        for order in purchase_orders
    }

    errors = []

    for receipt in goods_receipts:

        key = (receipt["po_id"], receipt["line_no"])

        if key not in order_lines:
            errors.append(
                f"Receipt {receipt['receipt_id']} "
                f"references unknown order line {key}"
            )
            continue

        order = order_lines[key]

        ordered_quantity = int(order["qty_ordered"])
        received_quantity = int(receipt["qty_received"])

        if received_quantity <= 0:
            errors.append(
                f"Receipt {receipt['receipt_id']}: "
                "received quantity must be positive"
            )

        if received_quantity > ordered_quantity:
            errors.append(
                f"Receipt {receipt['receipt_id']}: "
                f"received {received_quantity}, "
                f"but ordered only {ordered_quantity}"
            )

        order_date = date.fromisoformat(order["order_date"])
        receipt_date = date.fromisoformat(receipt["receipt_date"])

        if receipt_date < order_date:
            errors.append(
                f"Receipt {receipt['receipt_id']}: "
                "receipt date is before order date"
            )

    return errors


def validate_cumulative_receipts(purchase_orders, goods_receipts):
    """
    Check that cumulative received quantities
    never exceed ordered quantities.
    """

    received_quantities = {}

    # Calculate cumulative received quantities
    for receipt in goods_receipts:

        key = (receipt["po_id"], receipt["line_no"])

        quantity = int(receipt["qty_received"])

        received_quantities[key] = (
            received_quantities.get(key, 0) + quantity
        )

    errors = []

    # Compare cumulative receipts with ordered quantities
    for order in purchase_orders:

        key = (order["po_id"], order["line_no"])

        ordered_quantity = int(order["qty_ordered"])

        total_received = received_quantities.get(key, 0)

        if total_received > ordered_quantity:
            errors.append(
                f"Order {key}: cumulative received quantity "
                f"is {total_received}, but only "
                f"{ordered_quantity} was ordered"
            )

    return errors


def validate_erp(suppliers, purchase_orders, goods_receipts):

    errors = []

    errors.extend(
        validate_supplier_references(suppliers, purchase_orders)
    )

    errors.extend(
        validate_goods_receipts(purchase_orders, goods_receipts)
    )

    errors.extend(
        validate_unique_ids(
            suppliers,
            purchase_orders,
            goods_receipts
        )
    )

    errors.extend(
        validate_cumulative_receipts(
            purchase_orders,
            goods_receipts
        )
    )

    return errors



def main():

    suppliers = load_csv("suppliers.csv")
    purchase_orders = load_csv("purchase_orders.csv")
    goods_receipts = load_csv("goods_receipts.csv")

    print(f"Suppliers loaded: {len(suppliers)}")
    print(f"Purchase order lines loaded: {len(purchase_orders)}")
    print(f"Goods receipt lines loaded: {len(goods_receipts)}")

    errors = validate_erp(
        suppliers,
        purchase_orders,
        goods_receipts
    )

    if errors:
        print("\nERP VALIDATION FAILED")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("\nERP VALIDATION PASSED")
    print("All data integrity checks passed.")


if __name__ == "__main__":
    main()
