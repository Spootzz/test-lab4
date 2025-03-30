from behave import given, when, then
from app.eshop import Product, ShoppingCart, Order

# Мок-об'єкт для ShippingService
class MockShippingService:
    def create_shipping(self, shipping_type, product_ids, order_id, due_date):
        return f"MockShipping-{order_id}"

    def check_status(self, shipping_id):
        return "Delivered"

@given('I create a product with name "{name}", price {price:f}, and availability {availability:d}')
def step_create_product(context, name, price, availability):
    try:
        context.product = Product(availability, name, price)
        context.product_creation_success = True
    except ValueError:
        context.product_creation_success = False

@then('The product should have name "{name}", price {price:f}, and availability {availability:d}')
def step_verify_product(context, name, price, availability):
    assert context.product.name == name
    assert context.product.price == price
    assert context.product.available_amount == availability

@then('The product creation should fail')
def step_verify_creation_failure(context):
    assert not context.product_creation_success, "Product creation should have failed"

@given('I have an empty shopping cart')
def step_empty_cart(context):
    context.cart = ShoppingCart()

@when('I check if the product is available in amount {amount:d}')
def step_check_availability(context, amount):
    context.is_available = context.product.is_available(amount)

@then('The product should be available')
def step_product_available(context):
    assert context.is_available, "Product should be available"

@then('The product should not be available')
def step_product_not_available(context):
    assert not context.is_available, "Product should not be available"

@given('I add the product to the cart in amount {amount:d}')
@when('I add the product to the cart in amount {amount:d}')
def step_add_product_to_cart(context, amount):
    try:
        context.cart.add_product(context.product, amount)
        context.add_success = True
    except ValueError:
        context.add_success = False

@then('The product should be added to the cart successfully')
def step_verify_add_to_cart(context):
    assert context.add_success, "Product should have been added to the cart"

@then('The product should not be added to the cart successfully')
def step_verify_add_to_cart_failure(context):
    assert not context.add_success, "Product should NOT have been added to the cart"

@when('I remove the product from the cart')
def step_remove_product(context):
    context.cart.remove_product(context.product)

@then('The cart should be empty')
def step_verify_cart_empty(context):
    assert context.cart.is_empty(), "Cart should be empty"

@given('I have a mock shipping service')
def step_mock_shipping_service(context):
    context.shipping_service = MockShippingService()

@when('I place an order')
@when('I try to place an order')
def step_place_order(context):
    context.order = Order(context.cart, context.shipping_service)
    try:
        context.order.place_order("standard")
        context.order_success = True
    except ValueError:
        context.order_success = False

@then('The order should not be placed')
def step_order_should_not_be_placed(context):
    assert not context.order_success, "Order should not have been placed"

@then('The product availability should be {availability:d}')
def step_check_product_availability(context, availability):
    assert context.product.available_amount == availability, f"Expected availability {availability}, but got {context.product.available_amount}"
