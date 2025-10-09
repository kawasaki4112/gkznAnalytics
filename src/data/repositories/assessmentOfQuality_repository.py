from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import AssessmentOfQuality


class AssessmentOfQualityRepository(CRUDRepository[AssessmentOfQuality]):
    def __init__(self):
        super().__init__(AssessmentOfQuality)


user_crud = AssessmentOfQualityRepository()
