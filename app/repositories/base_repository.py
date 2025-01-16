from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.ext.declarative import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic Repository providing basic CRUD operations.
    
    Args:
        model: The SQLAlchemy model class
        db: SQLAlchemy database session
    
    Attributes:
        model: The SQLAlchemy model class
        db: SQLAlchemy database session
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: UUID) -> Optional[ModelType]:
        """
        Retrieve a record by id.
        
        Args:
            id: UUID of the record to retrieve
            
        Returns:
            Optional[ModelType]: The found record or None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Retrieve all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[ModelType]: List of found records
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, schema: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            schema: Pydantic schema containing the data
            
        Returns:
            ModelType: The created record
        """
        db_obj = self.model(**jsonable_encoder(schema))
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: UUID, schema: UpdateSchemaType) -> Optional[ModelType]:
        """
        Update a record by id.
        
        Args:
            id: UUID of the record to update
            schema: Pydantic schema containing the update data
            
        Returns:
            Optional[ModelType]: The updated record or None
        """
        db_obj = self.get(id)
        if db_obj:
            obj_data = jsonable_encoder(db_obj)
            update_data = schema.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: UUID) -> bool:
        """
        Delete a record by id.
        
        Args:
            id: UUID of the record to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False