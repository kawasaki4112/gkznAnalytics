import enum
from sqlalchemy import event, Float, String, Integer, BigInteger, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import uuid4, UUID
from datetime import datetime


class BaseEntity(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modified_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=func.utcnow)

class UserRole(str, enum.Enum):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    BANNED = 'banned'


# MODELS
class User(BaseEntity):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    assessment_of_qualities: Mapped[list["AssessmentOfQuality"]] = relationship(back_="user")
    net_promoter_scores: Mapped[list["NetPromoterScore"]] = relationship(back_populates="user")
    
    
class Specialist(BaseEntity):
    __tablename__ = 'specialists'
    
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)

    assessment_of_quality: Mapped[list["AssessmentOfQuality"]] = relationship(backref="specialist")
    net_promoter_scores: Mapped[list["NetPromoterScore"]] = relationship(back_populates="specialist")

    
class AssessmentOfQuality(BaseEntity):
    __tablename__ = 'assessments_of_quality'
    
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # Assuming quality is rated on a scale of 1-10
    comment: Mapped[str | None] = mapped_column(String(1000))  # Optional comment field
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    specialist_id: Mapped[str] = mapped_column(ForeignKey("specialists.id"), nullable=False)
    
    user: Mapped["User"] = relationship(backref="assessments_of_quality")
    specialist_id: Mapped[UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))  # ID of the specialist being rated

    net_promoter_score: Mapped["NetPromoterScore"] = relationship(
        back_populates="assessment_of_quality", uselist=False
    )
    
class NetPromoterScore(BaseEntity):
    __tablename__ = 'net_promoter_scores'
    
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # Score from 0 to 10
    comment: Mapped[str | None] = mapped_column(String(1000))  # Optional comment field

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    specialist_id: Mapped[str] = mapped_column(ForeignKey("specialists.id"), nullable=False)
    assessment_of_quality_id: Mapped[str] = mapped_column(
        ForeignKey("assessments_of_quality.id"), unique=True, nullable=False
    )
        
    user: Mapped["User"] = relationship(backref="net_promoter_scores")
    assessment_of_quality: Mapped["AssessmentOfQuality"] = relationship(
        back_populates="net_promoter_score"
    )