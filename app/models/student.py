from sqlalchemy import Column, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import BaseModel

class Student(BaseModel):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    level_id = Column(UUID(as_uuid=True), ForeignKey("levels.id"), nullable=False)
    terminated = Column(Boolean, default=False, nullable=True)

    user = relationship("User", back_populates="student")
    level = relationship("Level", back_populates="students")
    groups = relationship("StudentGroup", back_populates="student")
    subscriptions = relationship("Subscription", back_populates="student")
    