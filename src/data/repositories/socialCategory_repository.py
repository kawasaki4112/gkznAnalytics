from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import SocialCategory


class SocialCategoryRepository(CRUDRepository[SocialCategory]):
    def __init__(self):
        super().__init__(SocialCategory)

social_category_crud = SocialCategoryRepository()
