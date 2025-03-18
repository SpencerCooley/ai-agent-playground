# this flie conatins all models related to file management.

from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

# a fully matured asset has been both finalized and processed. 
class Asset(Base):
    __tablename__ = 'asset'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bucket_name: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str] = mapped_column(String(400), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False)
    preserved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # a boolean to determine if this is an asset we are keeping, or if it something that will need to be cleanded up. 
    processed = Column(MutableDict.as_mutable(JSONB)) # a place to save processed metadata. all file types will have a different metadata schema.
    associations = Column(MutableDict.as_mutable(JSONB))