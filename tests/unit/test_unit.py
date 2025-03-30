import unittest
from app.eshop import Product, ShoppingCart, Order
from unittest.mock import MagicMock


class TestEshop(unittest.TestCase):
    def setUp(self):
        self.product1 = Product(name='Test1', price=100.0, available_amount=10)
        self.product2 = Product(name='Test2', price=50.0, available_amount=5)
        self.cart = ShoppingCart()
        self.order = Order(self.cart, MagicMock())
        self.order.cart = self.cart

    def tearDown(self):
        self.cart.products.clear()

    def test_is_available_true(self):
        self.assertTrue(self.product1.is_available(5))

    def test_is_available_false(self):
        self.assertFalse(self.product1.is_available(15))

    def test_buy_reduces_stock(self):
        self.product1.buy(3)
        self.assertEqual(self.product1.available_amount, 7)

    def test_product_equality(self):
        product_copy = Product(name='Test1', price=200.0, available_amount=2)
        self.assertEqual(self.product1, product_copy)

    def test_product_inequality(self):
        self.assertNotEqual(self.product1, self.product2)

    def test_calculate_total_empty_cart(self):
        self.assertEqual(self.cart.calculate_total(), 0.0)

    def test_calculate_total_multiple_products(self):
        self.cart.add_product(self.product1, 2)
        self.cart.add_product(self.product2, 3)
        expected_total = (100.0 * 2) + (50.0 * 3)
        self.assertEqual(self.cart.calculate_total(), expected_total)

    def test_remove_product(self):
        self.cart.add_product(self.product1, 2)
        self.cart.remove_product(self.product1)
        self.assertFalse(self.cart.contains_product(self.product1))

    def test_place_order_reduces_stock(self):
        self.cart.add_product(self.product1, 4)
        self.cart.add_product(self.product2, 2)
        self.order.place_order("standard")
        self.assertEqual(self.product1.available_amount, 6)
        self.assertEqual(self.product2.available_amount, 3)

    def test_place_order_empties_cart(self):
        self.cart.add_product(self.product1, 4)
        self.order.place_order("standard")
        self.assertEqual(len(self.cart.products), 0)


if __name__ == '__main__':
    unittest.main()
