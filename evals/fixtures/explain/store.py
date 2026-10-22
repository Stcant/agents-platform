ORDERS = {}


def save(order):
    ORDERS[order["id"]] = order
    return order


def get(order_id):
    return ORDERS.get(order_id)
