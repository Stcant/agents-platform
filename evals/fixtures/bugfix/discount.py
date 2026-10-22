def apply_discount(price, percent):
    return price + price * percent / 100


def main():
    print(apply_discount(100, 10))


if __name__ == "__main__":
    main()
