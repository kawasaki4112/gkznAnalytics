from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import Product


class ProductRepository(CRUDRepository[Product]):
    def __init__(self):
        super().__init__(Product)


product_crud = ProductRepository()
