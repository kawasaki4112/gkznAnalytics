import enum
from sqlalchemy import event, Float, String, Integer, BigInteger, DateTime, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import uuid4, UUID
from datetime import datetime


class BaseEntity(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modified_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@event.listens_for(BaseEntity, "before_update", propagate=True)
def _update_modified_on(mapper, connection, target):
    target.modified_on = datetime.utcnow()

# ENUMERATIONS
class OrderStatus(str, enum.Enum):
    PENDING = 'pending'
    PAID = 'paid'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


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
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)

    orders: Mapped[list["Order"]] = relationship('Order', back_populates='user')


class Category(BaseEntity):
    __tablename__ = 'categories'

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    products: Mapped[list["Product"]] = relationship('Product', back_populates='category')


class Product(BaseEntity):
    __tablename__ = 'products'

    photo: Mapped[str | None] = mapped_column(String(500))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey('categories.id'))

    category: Mapped[Category] = relationship('Category', back_populates='products')
    order_items: Mapped[list["OrderItem"]] = relationship('OrderItem', back_populates='product')


class Order(BaseEntity):
    __tablename__ = 'orders'

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id'))
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped[User] = relationship('User', back_populates='orders')
    items: Mapped[list["OrderItem"]] = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')


class OrderItem(BaseEntity):
    __tablename__ = 'order_items'

    order_id: Mapped[str] = mapped_column(String(36), ForeignKey('orders.id'))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey('products.id'))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    order: Mapped[Order] = relationship('Order', back_populates='items')
    product: Mapped[Product] = relationship('Product', back_populates='order_items')
