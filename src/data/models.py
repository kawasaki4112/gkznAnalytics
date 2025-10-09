import enum
from sqlalchemy import event, Float, String, Integer, BigInteger, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import uuid4, UUID
from datetime import datetime


class BaseEntity(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@event.listens_for(BaseEntity, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    target.modified_at = datetime.utcnow()

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

    aoq: Mapped[list["AssessmentOfQuality"]] = relationship(back_populates="user")
    nps: Mapped[list["NetPromoterScore"]] = relationship(back_populates="user")

    
class Specialist(BaseEntity):
    __tablename__ = 'specialists'
    
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)

    aoq: Mapped[list["AssessmentOfQuality"]] = relationship(back_populates="specialist", cascade="all, delete-orphan")

class AssessmentOfQuality(BaseEntity):
    __tablename__ = 'assessments_of_quality'
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    specialist_id: Mapped[UUID] = mapped_column(ForeignKey('specialists.id'), nullable=False)
    
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(1000))

    user: Mapped["User"] = relationship(back_populates="aoq")
    nps: Mapped["NetPromoterScore"] = relationship(back_populates="aoq", uselist=False, cascade="all, delete-orphan")
    specialist: Mapped["Specialist"] = relationship(back_populates="aoq")
    
class NetPromoterScore(BaseEntity):
    __tablename__ = 'net_promoter_scores'
    
    aoq_id: Mapped[UUID] = mapped_column(ForeignKey('assessments_of_quality.id'), unique=True)
    
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(1000))

    user: Mapped["User"] = relationship(back_populates="nps")
    aoq: Mapped["AssessmentOfQuality"] = relationship(back_populates="nps", uselist=False)
