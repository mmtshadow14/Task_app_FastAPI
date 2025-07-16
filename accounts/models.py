from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from core.database import Base


# class UserModel(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     username = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#
#     is_active = Column(Boolean, default=False)
#
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
#
#     tasks = relationship("TaskModel", back_populates="users")
