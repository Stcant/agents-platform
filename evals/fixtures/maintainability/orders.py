def checkout_total_cents(subtotal_cents):
    shipping_cents = 0 if subtotal_cents >= 5000 else 500
    return subtotal_cents + shipping_cents


def order_summary(subtotal_cents):
    shipping_cents = 0 if subtotal_cents >= 5000 else 500
    return {
        "subtotal_cents": subtotal_cents,
        "shipping_cents": shipping_cents,
        "total_cents": subtotal_cents + shipping_cents,
    }


def customer_label(name):
    """Customer-facing label; independent of warehouse formatting policy."""
    return name.strip().upper()


def warehouse_label(name):
    """Warehouse-facing label; independent of customer formatting policy."""
    return name.strip().upper()
