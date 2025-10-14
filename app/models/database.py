"""
SQLAlchemy database models.

Defines User and Generation tables matching the schema in PRD.md.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """
    User model for authentication and tracking.

    Supports username/password authentication with session management.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    api_token = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    generations = relationship("Generation", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Session(Base):
    """
    Session model for authentication tokens.

    Stores session tokens with expiration for user authentication.
    """
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="sessions")

    # Indexes for performance
    __table_args__ = (
        Index('ix_sessions_token', 'token'),
        Index('ix_sessions_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id})>"


class Generation(Base):
    """
    Generation model for tracking cat image generations.

    Stores repository analysis results and generated image metadata.
    Associated with user who created the generation.
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
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="generations")

    # Indexes for performance (as per PRD.md requirements)
    __table_args__ = (
        Index('ix_generations_github_url', 'github_url'),
        Index('ix_generations_created_at', 'created_at'),
        Index('ix_generations_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<Generation(id={self.id}, repo={self.repo_owner}/{self.repo_name})>"
