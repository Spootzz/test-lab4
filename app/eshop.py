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
    """Represents a product with a name, price, and available stock."""

    def __init__(self, available_amount: int, name: str, price: float):
        """Initializes a product with availability, name, and price."""
        self.available_amount = available_amount
        self.name = name
        self.price = price

    def is_available(self, requested_amount: int) -> bool:
        """Checks if the requested amount of the product is available."""
        return self.available_amount >= requested_amount

    def buy(self, requested_amount: int):
        """Reduces the available stock of the product by the requested amount."""
        if not self.is_available(requested_amount):
            raise ValueError(f"Not enough stock for {self.name}")
        self.available_amount -= requested_amount

    def __eq__(self, other):
        """Checks if two products are the same based on their name."""
        if isinstance(other, Product):
            return self.name == other.name
        return False

    def __hash__(self):
        """Returns a hash of the product based on its name."""
        return hash(self.name)

    def __str__(self):
        """Returns the string representation of the product."""
        return self.name


class ShoppingCart:
    """Represents a shopping cart containing products."""

    def __init__(self):
        """Initializes an empty shopping cart."""
        self.products: Dict[Product, int] = {}

    def contains_product(self, product: Product) -> bool:
        """Checks if the cart contains a given product."""
        return product in self.products

    def calculate_total(self) -> float:
        """Calculates the total cost of the products in the cart."""
        return sum(p.price * count for p, count in self.products.items())

    def add_product(self, product: Product, amount: int):
        """Adds a product to the cart in the specified amount."""
        if not product.is_available(amount):
            raise ValueError(
                f"Product {product.name} has only {product.available_amount} items available"
            )
        self.products[product] = self.products.get(product, 0) + amount

    def remove_product(self, product: Product):
        """Removes a product from the cart if it exists."""
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self) -> List[str]:
        """Processes the cart order and clears the cart."""
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))
        self.products.clear()
        return product_ids


@dataclass
class Order:
    """Represents an order placed from a shopping cart."""

    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = str(uuid.uuid4())

    def place_order(self, shipping_type: str, due_date: datetime = None) -> str:
        """Places an order and returns a shipping confirmation."""
        if not due_date:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
        product_ids = self.cart.submit_cart_order()
        return self.shipping_service.create_shipping(  # type: ignore
            shipping_type, product_ids, self.order_id, due_date
        )


@dataclass
class Shipment:
    """Represents a shipment and allows checking its status."""

    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self) -> str:
        """Returns the current status of the shipment."""
        return self.shipping_service.check_status(self.shipping_id)