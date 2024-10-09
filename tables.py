from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey, insert
from sqlalchemy.types import Boolean, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)

class Customers(Base): 
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50))  # Identification
    username = Column(String(50), unique=True)  # Login info
    password = Column(String(100))  # Longer for hashing
    birthday = Column(DateTime)  # For discounts
    pizza_count = Column(Integer)  # For discounts
    postal_code = Column(String(10))  # Address data
    pizza_discount_code = Column(String(10), nullable=True)  # Optional discount code

class Discount(Base):
    __tablename__ = 'discounts'

    discount_id = Column(Integer, primary_key=True, autoincrement=True)
    discount_code = Column(Integer)
    discount_type = Column(String(10))
    discount_used = Column(Boolean)

class Pizza(Base): # no more vegan or vegetarian options
    __tablename__ = 'pizza'

    pizza_id = Column(Integer, primary_key=True, autoincrement=True)
    pizza_name = Column(String(50))
    pizza_price = Column(Numeric(5, 2))

class Drinks(Base):
    __tablename__ = 'drinks'

    drink_id = Column(Integer, primary_key=True, autoincrement=True)
    drink_type = Column(String(50), unique=True)
    drink_cost = Column(Numeric(5, 2))

class Desserts(Base):
    __tablename__ = 'desserts'

    dessert_id = Column(Integer, primary_key=True, autoincrement=True)
    dessert_type = Column(String(50), unique=True)
    dessert_cost = Column(Numeric(5, 2))

class Ingredients(Base): # no more vegan/ vegetarian
    __tablename__ = 'ingredients'

    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_name = Column(String(50))
    ingredient_cost = Column(Numeric(5, 2))

class CustomerOrder(Base):
    __tablename__ = 'customerorder'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    order_total = Column(Numeric(7, 2))
    delivery_address = Column(String(50))
    cancel_time = Column(Boolean)  # True if customer cancels (5 min limit)
    delivery_time_minutes = Column(Integer)

class OrderPizza(Base):
    __tablename__ = 'orderpizza'

    order_id = Column(Integer, ForeignKey('customerorder.order_id'), primary_key=True)
    pizza_id = Column(Integer, ForeignKey('pizza.pizza_id'), primary_key=True)
    pizza_amount = Column(Integer)

class OrderDrink(Base):
    __tablename__ = 'orderdrink'

    order_id = Column(Integer, ForeignKey('customerorder.order_id'), primary_key=True)
    drink_id = Column(Integer, ForeignKey('drinks.drink_id'), primary_key=True)
    drink_amount = Column(Integer)

class OrderDessert(Base):
    __tablename__ = 'orderdessert'

    order_id = Column(Integer, ForeignKey('customerorder.order_id'), primary_key=True)
    dessert_id = Column(Integer, ForeignKey('desserts.dessert_id'), primary_key=True)
    dessert_amount = Column(Integer)

class PizzaIngredients(Base):
    __tablename__ = 'pizzaingredients'

    pizza_id = Column(Integer, ForeignKey('pizza.pizza_id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.ingredient_id'), primary_key=True)

class DeliveryPersonnel(Base):
    __tablename__ = 'delivery_personnel'

    personnel_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50), nullable=False)
    postal_code_assigned = Column(String(10), nullable=False)  # Assigned area of delivery
    is_available = Column(Boolean, default=True)  # Whether the person is available for delivery
    next_available_time = Column(DateTime, nullable=True)  # When they'll be available next
#---------------------------------------
Base.metadata.create_all(engine)

