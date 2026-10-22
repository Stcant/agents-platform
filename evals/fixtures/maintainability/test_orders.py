import unittest

from orders import (
    checkout_total_cents,
    customer_label,
    order_summary,
    warehouse_label,
)


class OrderTest(unittest.TestCase):
    def test_standard_shipping(self):
        for subtotal_cents, shipping_cents in [(4999, 500), (5000, 0), (5001, 0)]:
            with self.subTest(subtotal_cents=subtotal_cents):
                self.assertEqual(
                    checkout_total_cents(subtotal_cents),
                    subtotal_cents + shipping_cents,
                )
                self.assertEqual(
                    order_summary(subtotal_cents),
                    {
                        "subtotal_cents": subtotal_cents,
                        "shipping_cents": shipping_cents,
                        "total_cents": subtotal_cents + shipping_cents,
                    },
                )

    def test_independent_labels(self):
        self.assertEqual(customer_label(" Ada "), "ADA")
        self.assertEqual(warehouse_label(" Depot "), "DEPOT")


if __name__ == "__main__":
    unittest.main()
