from store import save


def create_order(order_id, amount):
    order = {"id": order_id, "amount": amount, "status": "created"}
    return save(order)
