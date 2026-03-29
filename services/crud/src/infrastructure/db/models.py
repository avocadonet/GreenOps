from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from .postgres import constraint_naming_conventions


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=constraint_naming_conventions)
