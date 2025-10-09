from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import OrderItem


class OrderItemRepository(CRUDRepository[OrderItem]):
    def __init__(self):
        super().__init__(OrderItem)


order_item_crud = OrderItemRepository()