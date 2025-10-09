from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import Order


class OrderRepository(CRUDRepository[Order]):
    def __init__(self):
        super().__init__(Order)


order_crud = OrderRepository()