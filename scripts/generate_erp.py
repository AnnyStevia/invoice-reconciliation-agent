import csv
import random
from pathlib import Path
from datetime import date, timedelta

# Locate the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define the ERP data directory
ERP_DIR = PROJECT_ROOT / "data" / "erp"

# Anchor date for receipt delays. Order dates are generated before this date.
REFERENCE_DATE = date.today()

SUPPLIERS = [
    {
        "name": "Atlas Tech",
        "currency": "MAD"
    },
    {
        "name": "Global Systems",
        "currency": "EUR"
    },
    {
        "name": "Maroc Digital",
        "currency": "MAD"
    },
    {
        "name": "Euro Supplies",
        "currency": "EUR"
    },
    {
        "name": "Casablanca Electronics",
        "currency": "MAD"
    },
    {
        "name": "Techno Distribution",
        "currency": "MAD"
    },
    {
        "name": "North Africa Solutions",
        "currency": "EUR"
    },
    {
        "name": "Maghreb Office",
        "currency": "MAD"
    }
]

PRODUCTS = [
    {"sku": "LAP001", "description": "Laptop Dell", "unit_price": 5000},
    {"sku": "MON001", "description": "Monitor 24 inches", "unit_price": 1500},
    {"sku": "KEY001", "description": "Wireless Keyboard", "unit_price": 200},
    {"sku": "MOU001", "description": "Wireless Mouse", "unit_price": 120},
    {"sku": "PRI001", "description": "Office Printer", "unit_price": 2500},
    {"sku": "HDD001", "description": "External Hard Drive", "unit_price": 800},
    {"sku": "USB001", "description": "USB Flash Drive", "unit_price": 100},
    {"sku": "CHA001", "description": "Office Chair", "unit_price": 1200}
]

SUPPLIER_COLUMNS = [
    "supplier_id",
    "name",
    "ice",
    "currency",
    "vat_rate"
]

PURCHASE_ORDER_COLUMNS = [
    "po_id",
    "supplier_id",
    "line_no",
    "sku",
    "description",
    "qty_ordered",
    "unit_price",
    "currency",
    "order_date"
]

GOODS_RECEIPT_COLUMNS = [
    "receipt_id",
    "po_id",
    "line_no",
    "qty_received",
    "receipt_date"
]


def generate_suppliers():
    """Generate 8 fictional suppliers."""

    generated_suppliers = []

    for index, supplier in enumerate(SUPPLIERS, start=1):
        generated_supplier = {
            "supplier_id": f"SUP{index:03d}",
            "name": supplier["name"],
            "ice": f"{random.randint(10**14, 10**15 - 1)}",
            "currency": supplier["currency"],
            "vat_rate": 0.20
        }

        generated_suppliers.append(generated_supplier)

    return generated_suppliers


def generate_purchase_orders(suppliers, number_of_orders=40):
    """
    Generate fictional purchase orders.

    Each order belongs to an existing supplier
    and contains between 1 and 3 product lines.
    """

    purchase_orders = []

    for order_index in range(1, number_of_orders + 1):

        # Select an existing supplier
        supplier = random.choice(suppliers)

        supplier_id = supplier["supplier_id"]
        currency = supplier["currency"]

        # Generate a unique purchase order ID
        po_id = f"PO{order_index:03d}"

        # Generate between 1 and 3 order lines
        number_of_lines = random.randint(1, 3)

        for line_number in range(1, number_of_lines + 1):

            # Select a product from our catalog
            product = random.choice(PRODUCTS)

            # Generate the ordered quantity
            quantity = random.randint(1, 20)

            # Generate the order date
            order_date = date.today() - timedelta(
                days=random.randint(1, 180)
            )

            order_line = {
                "po_id": po_id,
                "supplier_id": supplier_id,
                "line_no": line_number,
                "sku": product["sku"],
                "description": product["description"],
                "qty_ordered": quantity,
                "unit_price": product["unit_price"],
                "currency": currency,
                "order_date": order_date.isoformat()
            }

            purchase_orders.append(order_line)

    return purchase_orders

    
def generate_goods_receipts(purchase_orders):
    """
    Generate fictional goods receipts based on purchase order lines.

    Distribution:
    - 80% fully received
    - 15% partially received
    - 5% not received
    """

    goods_receipts = []
    receipt_counter = 1

    for order_line in purchase_orders:

        ordered_quantity = order_line["qty_ordered"]

        # Decide the receipt situation
        receipt_status = random.random()

        if receipt_status < 0.05:
            # No goods received: no receipt record is created
            continue

        elif receipt_status < 0.20 and ordered_quantity >= 2:
            # Partial delivery
            received_quantity = random.randint(
                1,
                ordered_quantity - 1
            )

        else:
            # Full delivery
            received_quantity = ordered_quantity

        # Generate a receipt date after the purchase order date
        order_date = date.fromisoformat(order_line["order_date"])

        max_delay = min(
            14,
            (REFERENCE_DATE - order_date).days
        )

        receipt_date = order_date + timedelta(
            days=random.randint(1, max_delay)
        )

        receipt = {
            "receipt_id": f"GR{receipt_counter:03d}",
            "po_id": order_line["po_id"],
            "line_no": order_line["line_no"],
            "qty_received": received_quantity,
            "receipt_date": receipt_date.isoformat()
        }

        goods_receipts.append(receipt)
        receipt_counter += 1

    return goods_receipts



def save_to_csv(data, filename, fieldnames):
    """
    Save a list of dictionaries to a CSV file.

    Args:
        data: List of dictionaries to save.
        filename: Name of the output CSV file.
        fieldnames: Column names of the CSV.
    """

    file_path = ERP_DIR / filename

    with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        # Write column headers
        writer.writeheader()

        # Write data rows
        writer.writerows(data)

    print(f"Generated: {file_path}")


def main():
    # Ensure reproducible data generation
    random.seed(42)

    # Create the directory if it does not exist
    ERP_DIR.mkdir(parents=True, exist_ok=True)

    suppliers = generate_suppliers()

    save_to_csv(
        data=suppliers,
        filename="suppliers.csv",
        fieldnames=SUPPLIER_COLUMNS
    )

    purchase_orders = generate_purchase_orders(suppliers)

    save_to_csv(
        data=purchase_orders,
        filename="purchase_orders.csv",
        fieldnames=PURCHASE_ORDER_COLUMNS
        
    )

    # Generate goods receipts
    goods_receipts = generate_goods_receipts(purchase_orders)

    save_to_csv(
        data=goods_receipts,
        filename="goods_receipts.csv",
        fieldnames=GOODS_RECEIPT_COLUMNS
    )




if __name__ == "__main__":
    main()
