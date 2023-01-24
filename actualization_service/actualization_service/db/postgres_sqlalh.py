import asyncio
from typing import Tuple, Union, Dict
import uuid

import backoff
from loguru import logger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, create_engine, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


from ..core.config import PostgresSettings


settings = PostgresSettings()

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_NAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class PostgresWriterCyberleninka(Base):
    """ Model for Cyberleninka"""
    __tablename__ = 'demo_cyberleninka'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    cyberleninka_id = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=False)
    science_magazine_name = Column(String, nullable=False)
    science_magazine_url = Column(String, nullable=False)
    annotation = Column(String, nullable=False)
    annotation_en = Column(String)
    article_text = Column(String, nullable=False)
    field_of_sciences = Column(String, nullable=False)

    keywords = Column(String, nullable=False)
    tags = Column(String, nullable=False)
    similar_topics = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    pdf_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))


def add(cyberleninka):
    db = SessionLocal()
    db.add(cyberleninka)
    db.commit()
    db.refresh(cyberleninka)
    db.close()
    return cyberleninka




