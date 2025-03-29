import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta, timezone
from services import ShippingService
from app.eshop import ShoppingCart, Order, Product


@pytest.fixture
def mock_shipping_service():
    mock_repo = Mock()
    mock_publisher = Mock()
    return ShippingService(mock_repo, mock_publisher), mock_repo, mock_publisher


def test_create_shipping_success(mock_shipping_service):
    shipping_service, mock_repo, mock_publisher = mock_shipping_service
    mock_repo.create_shipping.return_value = "test_shipping_id"
    cart = ShoppingCart()
    cart.add_product(Product(10, "Product", 50), 1)
    order = Order(cart, shipping_service)

    shipping_id = order.place_order("Нова Пошта", datetime.now(timezone.utc) + timedelta(minutes=5))

    assert shipping_id == "test_shipping_id"
    mock_repo.create_shipping.assert_called()
    mock_publisher.send_new_shipping.assert_called_with("test_shipping_id")


def test_create_shipping_invalid_type(mock_shipping_service):
    shipping_service, _, _ = mock_shipping_service
    cart = ShoppingCart()
    cart.add_product(Product(10, "Product", 50), 1)
    order = Order(cart, shipping_service)

    with pytest.raises(ValueError, match="Shipping type is not available"):
        order.place_order("Невідомий тип", datetime.now(timezone.utc) + timedelta(minutes=5))


def test_create_shipping_due_date_in_past(mock_shipping_service):
    shipping_service, _, _ = mock_shipping_service
    cart = ShoppingCart()
    cart.add_product(Product(10, "Product", 50), 1)
    order = Order(cart, shipping_service)

    with pytest.raises(ValueError, match="Shipping due datetime must be greater than datetime now"):
        order.place_order("Нова Пошта", datetime.now(timezone.utc) - timedelta(minutes=1))


def test_shipping_status_change_on_creation(mock_shipping_service):
    shipping_service, mock_repo, mock_publisher = mock_shipping_service
    mock_repo.create_shipping.return_value = "test_shipping_id"

    cart = ShoppingCart()
    cart.add_product(Product(10, "Product", 50), 1)
    order = Order(cart, shipping_service)
    order.place_order("Нова Пошта", datetime.now(timezone.utc) + timedelta(minutes=5))

    mock_repo.update_shipping_status.assert_called_with("test_shipping_id", shipping_service.SHIPPING_IN_PROGRESS)


def test_message_sent_to_sqs_on_creation(mock_shipping_service):
    shipping_service, mock_repo, mock_publisher = mock_shipping_service
    mock_repo.create_shipping.return_value = "test_shipping_id"

    cart = ShoppingCart()
    cart.add_product(Product(10, "Product", 50), 1)
    order = Order(cart, shipping_service)
    order.place_order("Нова Пошта", datetime.now(timezone.utc) + timedelta(minutes=5))

    mock_publisher.send_new_shipping.assert_called_with("test_shipping_id")


def test_mock_publisher_side_effect(mock_shipping_service):
    shipping_service, mock_repo, mock_publisher = mock_shipping_service
    mock_repo.create_shipping.return_value = "test_shipping_id"
    mock_publisher.send_new_shipping.side_effect = Exception("SQS failure")

    cart = ShoppingCart()
    cart.add_product(Product(10, "Product", 50), 1)
    order = Order(cart, shipping_service)

    with pytest.raises(Exception, match="SQS failure"):
        order.place_order("Нова Пошта", datetime.now(timezone.utc) + timedelta(minutes=5))


def test_process_shipping_batch(mock_shipping_service):
    shipping_service, mock_repo, mock_publisher = mock_shipping_service
    mock_publisher.poll_shipping.return_value = ["test_shipping_id_1", "test_shipping_id_2"]
    mock_repo.get_shipping.return_value = {"due_date": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()}
    mock_repo.update_shipping_status.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    result = shipping_service.process_shipping_batch()

    assert len(result) == 2
    mock_repo.update_shipping_status.assert_called()



def test_fail_shipping_if_due_date_passed(mock_shipping_service):
    shipping_service, mock_repo, _ = mock_shipping_service
    mock_repo.get_shipping.return_value = {"due_date": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()}
    mock_repo.update_shipping_status.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    response = shipping_service.process_shipping("test_shipping_id")

    mock_repo.update_shipping_status.assert_called_with("test_shipping_id", shipping_service.SHIPPING_FAILED)



def test_mock_calls_tracking(mock_shipping_service):
    shipping_service, mock_repo, mock_publisher = mock_shipping_service
    mock_repo.create_shipping.return_value = "test_shipping_id"

    cart = ShoppingCart()
    cart.add_product(Product(10, "Product", 50), 1)
    order = Order(cart, shipping_service)
    order.place_order("Нова Пошта", datetime.now(timezone.utc) + timedelta(minutes=5))

    assert mock_repo.create_shipping.call_count == 1
    assert mock_publisher.send_new_shipping.call_count == 1
    assert mock_repo.update_shipping_status.call_count == 1


def test_complete_shipping(mock_shipping_service):
    shipping_service, mock_repo, _ = mock_shipping_service
    mock_repo.get_shipping.return_value = {"due_date": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()}
    mock_repo.update_shipping_status.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    response = shipping_service.process_shipping("test_shipping_id")

    mock_repo.update_shipping_status.assert_called_with("test_shipping_id", shipping_service.SHIPPING_COMPLETED)

