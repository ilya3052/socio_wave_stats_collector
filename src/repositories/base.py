from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Sequence

from sqlalchemy import select, Row, RowMapping
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session, model: Type[T]):
        self.session: Session = session
        self.model = model

    def get(self, id) -> Optional[T]:
        if not (obj := self.session.get(self.model, id)):
            raise ValueError('Объект не найден в базе данных')

        return obj

    def get_all(self) -> Sequence[Row[Any] | RowMapping | Any] | List[T]:
        return self.session.scalars(select(self.model)).all()

    def delete(self, id) -> None:
        if not (instance := self.session.get(self.model, id)):
            raise ValueError('Объект не найден в базе данных')
        self.session.delete(instance)
        self.session.commit()

    def add(self, instance: T) -> int:
        if instance is None:
            raise ValueError('Объект не найден, возможно, он не был создан')

        self.session.add(instance)
        self.session.commit()
        return instance.id

    def update(self, id, data: Dict) -> Optional[T]:
        if not (obj := self.session.get(self.model, id)):
            raise ValueError('Объект не найден в базе данных')

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        self.session.commit()
        return obj

    def commit(self) -> None:
        self.session.commit()

    def flush(self) -> None:
        self.session.flush()

    def refresh(self, instance: T) -> T:
        if instance is None:
            raise ValueError('Объект не существует')

        self.session.refresh(instance)
        return instance
