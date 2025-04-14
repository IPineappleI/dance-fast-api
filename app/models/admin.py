from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Admin(BaseModel):
    __tablename__ = "admins"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Связи
    user = relationship("User", back_populates="admin") 