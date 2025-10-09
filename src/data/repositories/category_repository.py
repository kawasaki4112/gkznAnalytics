from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import Category


class CategoryRepository(CRUDRepository[Category]):
    def __init__(self):
        super().__init__(Category)


category_crud = CategoryRepository()