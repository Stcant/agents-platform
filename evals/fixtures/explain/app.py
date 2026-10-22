import sys

from service import create_order


def main(argv):
    order_id = int(argv[1])
    amount = float(argv[2])
    order = create_order(order_id, amount)
    print(f"order {order['id']} status={order['status']}")


if __name__ == "__main__":
    main(sys.argv)
