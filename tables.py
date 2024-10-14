from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey, insert
from sqlalchemy.types import Boolean, Numeric
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.mysql import DECIMAL

Base = declarative_base()
engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)

class Customers(Base): 
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50)) 
    gender = Column(String(10)) 
    username = Column(String(50), unique=True)  
    password = Column(String(100))  
    birthday = Column(DateTime)  
    pizza_count = Column(Integer)  
    postal_code = Column(String(10))  
    pizza_discount_code = Column(String(10), nullable=True)  

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
    pizza_price = Column(DECIMAL(5, 2))

class Drinks(Base):
    __tablename__ = 'drinks'

    drink_id = Column(Integer, primary_key=True, autoincrement=True)
    drink_type = Column(String(50), unique=True)
    drink_cost = Column(DECIMAL(5, 2))

class Desserts(Base):
    __tablename__ = 'desserts'

    dessert_id = Column(Integer, primary_key=True, autoincrement=True)
    dessert_type = Column(String(50), unique=True)
    dessert_cost = Column(DECIMAL(5, 2))

class Ingredients(Base): # no more vegan/ vegetarian
    __tablename__ = 'ingredients'

    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_name = Column(String(50))
    ingredient_cost = Column(DECIMAL(5, 2))

class CustomerOrder(Base):
    __tablename__ = 'customerorder'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey('customers.username'))
    order_total = Column(DECIMAL(7, 2))
    postal_code = Column(String(50))
    order_datetime = Column(DateTime) # drop db and ad alter

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
    postal_code_assigned = Column(String(10), nullable=False) 
    is_available = Column(Boolean, default=True)  
    next_available_time = Column(DateTime, nullable=True)  

    
#---------------------------------------
Base.metadata.create_all(engine)





