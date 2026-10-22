import unittest

from discount import apply_discount


class DiscountTest(unittest.TestCase):
    def test_ten_percent_off_hundred(self):
        self.assertEqual(apply_discount(100, 10), 90.0)

    def test_no_discount(self):
        self.assertEqual(apply_discount(50, 0), 50.0)


if __name__ == "__main__":
    unittest.main()
