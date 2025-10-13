"""
SQLAlchemy database models.

Defines User and Generation tables matching the schema in PRD.md.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class User(Base):
    """
    User model for authentication and tracking.

    Note: Full implementation is post-MVP.
    For MVP, this table exists but is not actively used.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=True)
    api_token = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Generation(Base):
    """
    Generation model for tracking cat image generations.

    Stores repository analysis results and generated image metadata.
    """
    __tablename__ = "generations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_url = Column(Text, nullable=False)
    repo_owner = Column(String(255), nullable=True)
    repo_name = Column(String(255), nullable=True)
    primary_language = Column(String(100), nullable=True)
    repo_size_kb = Column(Integer, nullable=True)
    code_quality_score = Column(Numeric(3, 1), nullable=True)
    cat_attributes = Column(JSONB, nullable=True)
    analysis_data = Column(JSONB, nullable=True)
    image_path = Column(Text, nullable=True)
    image_prompt = Column(Text, nullable=True)
    story = Column(Text, nullable=True)
    meme_text_top = Column(String(100), nullable=True)
    meme_text_bottom = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes for performance (as per PRD.md requirements)
    __table_args__ = (
        Index('ix_generations_github_url', 'github_url'),
        Index('ix_generations_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Generation(id={self.id}, repo={self.repo_owner}/{self.repo_name})>"
