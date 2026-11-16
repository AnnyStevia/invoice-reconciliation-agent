
from scripts.validate_erp import validate_cumulative_receipts


def test_cumulative_receipts_within_ordered_quantity():

    purchase_orders = [
        {
            "po_id": "PO001",
            "line_no": "1",
            "qty_ordered": "10"
        }
    ]

    goods_receipts = [
        {
            "receipt_id": "GR001",
            "po_id": "PO001",
            "line_no": "1",
            "qty_received": "4"
        },
        {
            "receipt_id": "GR002",
            "po_id": "PO001",
            "line_no": "1",
            "qty_received": "3"
        }
    ]

    errors = validate_cumulative_receipts(
        purchase_orders,
        goods_receipts
    )

    assert errors == []


def test_cumulative_receipts_exceed_ordered_quantity():

    purchase_orders = [
        {
            "po_id": "PO001",
            "line_no": "1",
            "qty_ordered": "10"
        }
    ]

    goods_receipts = [
        {
            "receipt_id": "GR001",
            "po_id": "PO001",
            "line_no": "1",
            "qty_received": "7"
        },
        {
            "receipt_id": "GR002",
            "po_id": "PO001",
            "line_no": "1",
            "qty_received": "5"
        }
    ]

    errors = validate_cumulative_receipts(
        purchase_orders,
        goods_receipts
    )

    assert len(errors) == 1
    assert "cumulative received quantity is 12" in errors[0]
