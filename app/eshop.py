"""
This module contains classes for an e-commerce application,
including Product, ShoppingCart, and Order.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from services import ShippingService


class Product:
    """Represents a product in the e-shop."""

    def __init__(self, name: str, price: float, available_amount: int):
        """Initializes a product with name, price, and available amount."""
        if price < 0:
            raise ValueError("Price cannot be negative")
        if available_amount < 0:
            raise ValueError("Available amount cannot be negative")
        self.name = name
        self.price = price
        self.available_amount = available_amount

    def is_available(self, amount: int) -> bool:
        """Checks if the product is available in the given amount."""
        return self.available_amount >= amount

class ShoppingCart:
    """Represents a shopping cart containing multiple products."""

    def __init__(self):
        """Initializes an empty shopping cart."""
        self.items = {}

    def add_product(self, product: Product, amount: int) -> bool:
        """Adds a product to the cart if enough stock is available."""
        if product.is_available(amount):
            self.items[product] = self.items.get(product, 0) + amount
            return True
        return False

    def remove_product(self, product: Product):
        """Removes a product from the cart."""
        if product in self.items:
            del self.items[product]

    def is_empty(self) -> bool:
        """Checks if the shopping cart is empty."""
        return len(self.items) == 0

class Order:
    """Represents an order created from the shopping cart."""

    def __init__(self, cart: ShoppingCart, shipping_service):
        """Initializes an order with a cart and shipping service."""
        if cart.is_empty():
            raise ValueError("Cannot place an order with an empty cart")
        self.cart = cart
        self.shipping_service = shipping_service
        self.status = "Pending"

    def place_order(self):
        """Processes the order by deducting stock and initiating shipping."""
        for product, amount in self.cart.items.items():
            product.available_amount -= amount
        self.shipping_service.create_shipping(self)
        self.cart.items.clear()
        self.status = "Shipped"



@dataclass
class Shipment:
    """Represents a shipment and allows checking its status."""

    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self) -> str:
        """Returns the current status of the shipment."""
        return self.shipping_service.check_status(self.shipping_id)