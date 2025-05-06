from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    email = Column(String(255), unique=True, nullable=False, index=True)
    email_confirmed = Column(Boolean, nullable=False, default=False)
    receive_email = Column(Boolean, nullable=False, default=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    phone_number = Column(String, unique=True, nullable=False)
    terminated = Column(Boolean, nullable=False, default=False)

    admin = relationship('Admin', uselist=False, back_populates='user')
    student = relationship('Student', uselist=False, back_populates='user')
    teacher = relationship('Teacher', uselist=False, back_populates='user')
