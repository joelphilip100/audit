from typing import TypeVar, Generic, Type, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], id_field: str = "id"):
        self.model = model
        self.id_field = id_field

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        try:
            db.add(obj_in)
            db.commit()
            db.refresh(obj_in)
        except IntegrityError as e:
            db.rollback()
            raise e
        return obj_in

    def get_all(self, db: Session) -> List[ModelType]:
        return db.query(self.model).all()

    def get_by_field(self, db: Session, field_name: str, id_: str) -> ModelType | None:
        if not hasattr(self.model, field_name):
            raise AttributeError(f"{self.model.__name__} has no field '{field_name}'")
        field = getattr(self.model, field_name)
        return db.query(self.model).filter(field == id_).first()

    def delete(self, db: Session, db_obj: ModelType) -> None:
        db.delete(db_obj)
        db.commit()

    def update(self, db: Session, db_obj: UpdateSchemaType) -> ModelType:
        db.commit()
        db.refresh(db_obj)
        return db_obj
