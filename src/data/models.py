import os, enum
from typing import Optional, Union
import pytz
from sqlalchemy import event, Float, String, Integer, BigInteger, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import uuid4, UUID

from datetime import datetime

tz = pytz.timezone(os.getenv("TIMEZONE", "Asia/Yakutsk"))

    
def tz_now_naive() -> datetime:
    return datetime.now(tz=tz).replace(tzinfo=None)

class BaseEntity(DeclarativeBase):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=tz_now_naive)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=tz_now_naive, onupdate=tz_now_naive)


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
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    social_subcategory_id: Mapped[UUID] = mapped_column(ForeignKey('social_subcategories.id', ondelete="SET NULL"), nullable=True)

    aoq: Mapped[list["AssessmentOfQuality"]] = relationship(back_populates="user")
    nps: Mapped[list["NetPromoterScore"]] = relationship(back_populates="user")
    socialsubcategory: Mapped["SocialSubcategory"] = relationship(back_populates="user", uselist=False)

class Service(BaseEntity):
    __tablename__ = 'services'

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    aoq: Mapped[list["AssessmentOfQuality"]] = relationship(back_populates="service", cascade="all, delete-orphan")

class SocialCategory(BaseEntity):
    __tablename__ = 'social_categories'

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    subcategories: Mapped[list["SocialSubcategory"]] = relationship(back_populates="category", cascade="all, delete-orphan")
    
    
class SocialSubcategory(BaseEntity):
    __tablename__ = 'social_subcategories'

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    category_id: Mapped[UUID] = mapped_column(ForeignKey('social_categories.id', ondelete="CASCADE"), nullable=False)

    category: Mapped["SocialCategory"] = relationship(back_populates="subcategories")
    user: Mapped[Optional["User"]] = relationship(back_populates="socialsubcategory", uselist=False)
    
class Specialist(BaseEntity):
    __tablename__ = 'specialists'

    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=True)
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=True)
    link: Mapped[str] = mapped_column(String(1000), nullable=True)
    
    aoq: Mapped[list["AssessmentOfQuality"]] = relationship(back_populates="specialist", cascade="all, delete-orphan")

class AssessmentOfQuality(BaseEntity):
    __tablename__ = 'assessments_of_quality'
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    specialist_id: Mapped[UUID] = mapped_column(ForeignKey('specialists.id'), nullable=False)
    service_id: Mapped[UUID] = mapped_column(ForeignKey('services.id', ondelete="SET NULL"), nullable=True)
    
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String(1000), nullable=True)

    user: Mapped["User"] = relationship(back_populates="aoq")
    nps: Mapped["NetPromoterScore"] = relationship(back_populates="aoq", uselist=False, cascade="all, delete-orphan")
    specialist: Mapped["Specialist"] = relationship(back_populates="aoq")
    service: Mapped[Optional["Service"]] = relationship()
    
class NetPromoterScore(BaseEntity):
    __tablename__ = 'net_promoter_scores'
    
    aoq_id: Mapped[UUID] = mapped_column(ForeignKey('assessments_of_quality.id'), unique=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)

    score: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="nps")
    aoq: Mapped["AssessmentOfQuality"] = relationship(back_populates="nps", uselist=False)
