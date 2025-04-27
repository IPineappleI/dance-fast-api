from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import *


class Admin(BaseModel):
    __tablename__ = 'admins'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)

    user = relationship('User', uselist=False, back_populates='admin')
