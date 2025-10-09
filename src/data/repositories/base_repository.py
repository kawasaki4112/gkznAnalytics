from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy import select, update, delete

from src.data.db import async_session

ModelType = TypeVar("ModelType")
Filter = Dict[str, Any]
Update = Dict[str, Any]


class CRUDRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, **data: Any) -> ModelType:
        """
        Создает новый объект модели и возвращает его.
        """
        async with async_session() as session:
            async with session.begin():
                instance = self.model(**data)
                session.add(instance)
            await session.refresh(instance)
            return instance

    async def get(
        self,
        id: Any = None,
        **filters: Any
    ) -> Optional[ModelType]:
        """
        Возвращает один объект по ID или фильтрам.
        """
        async with async_session() as session:
            stmt = select(self.model)
            if id is not None:
                stmt = stmt.where(self.model.id == id)
            if filters:
                stmt = stmt.filter_by(**filters)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_list(
        self,
        **filters: Any
    ) -> List[ModelType]:
        """
        Возвращает список объектов, подходящих под фильтры.
        """
        async with async_session() as session:
            stmt = select(self.model).filter_by(**filters)
            result = await session.execute(stmt)
            return result.scalars().all()
        

    async def update(
        self,
        filters: Filter,
        updates: Update
    ) -> int:
        """
        Обновляет поля объектов, подходящих под фильтры.
        Возвращает число затронутых строк.
        """
        async with async_session() as session:
            async with session.begin():
                stmt = (
                    update(self.model)
                    .filter_by(**filters)
                    .values(**updates)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(stmt)
            return result.rowcount

    async def delete(self, **filters: Any) -> int:
        """
        Удаляет объекты, подходящие под фильтры.
        Возвращает число удалённых строк.
        """
        async with async_session() as session:
            async with session.begin():
                stmt = (
                    delete(self.model)
                    .filter_by(**filters)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(stmt)
            return result.rowcount
