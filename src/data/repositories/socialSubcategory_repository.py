from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import SocialSubcategory


class SocialSubcategoryRepository(CRUDRepository[SocialSubcategory]):
    def __init__(self):
        super().__init__(SocialSubcategory)

social_subcategory_crud = SocialSubcategoryRepository()
