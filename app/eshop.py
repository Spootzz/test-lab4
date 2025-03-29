import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from services import ShippingService


class Product:
    def __init__(self, available_amount: int, name: str, price: float):
        self.available_amount = available_amount
        self.name = name
        self.price = price

    def is_available(self, requested_amount: int) -> bool:
        return self.available_amount >= requested_amount

    def buy(self, requested_amount: int):
        if not self.is_available(requested_amount):
            raise ValueError(f"Not enough stock for {self.name}")
        self.available_amount -= requested_amount

    def __eq__(self, other):
        if isinstance(other, Product):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class ShoppingCart:
    def __init__(self):
        self.products: Dict[Product, int] = {}

    def contains_product(self, product: Product) -> bool:
        return product in self.products

    def calculate_total(self) -> float:
        return sum(p.price * count for p, count in self.products.items())

    def add_product(self, product: Product, amount: int):
        if not product.is_available(amount):
            raise ValueError(f"Product {product.name} has only {product.available_amount} items available")
        self.products[product] = self.products.get(product, 0) + amount

    def remove_product(self, product: Product):
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self) -> List[str]:
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))
        self.products.clear()
        return product_ids


@dataclass
class Order:
    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = str(uuid.uuid4())

    def place_order(self, shipping_type: str, due_date: datetime = None) -> str:
        if not due_date:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
        product_ids = self.cart.submit_cart_order()
        return self.shipping_service.create_shipping(shipping_type, product_ids, self.order_id, due_date)


@dataclass
class Shipment:
    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self) -> str:
        return self.shipping_service.check_status(self.shipping_id)
