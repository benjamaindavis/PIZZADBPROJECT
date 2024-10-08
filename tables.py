from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey, insert
from sqlalchemy.types import Boolean, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_engine('mysql+pymysql://root:toolbox@127.0.0.1:3306/PizzaShop', echo=True)

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

with engine.connect() as conn:
    conn.execute(
        insert(Pizza),#calculate margins
        [
            {'pizza_name': 'Marry Me Margherita', "pizza_price": 9.00}, # 4.00 for base, sauce is 2.00, cheese 3.00
            {'pizza_name': 'Perfect Pepperoni', "pizza_price": 10.99},
            {'pizza_name': 'Voluptuous Vegetarian', "pizza_price": 13.50},# peppers, mushrooms, red onions
            {'pizza_name': 'Angsty Anchovie', "pizza_price": 10.99},
            {'pizza_name': 'Sizzling Salami', "pizza_price": 10.99},
            {'pizza_name': 'Meatlovers', "pizza_price": 18.95}, # ham, bacon, salami, pepeproni, sausage (1.99 * 5)
            {'pizza_name': 'Kiss of the Sea', "pizza_price": 14.97}, # calamari, anchovies, prawns (1.99 * 3)
            {'pizza_name': 'BBQ Chicken', "pizza_price": 12.98},# bbq chicken, onions (1.99 * 2)
            {'pizza_name': 'Sexy Showarma', "pizza_price": 10.99},# showarma
            {'pizza_name': 'Salami-roni Pizza', "pizza_price": 12.98},# salami, pepperoni(1.99 * 2)
        ]
    )
    conn.execute(
        insert(Desserts), #calculate margins
        [
            {'dessert_type': 'Tiramisu', "dessert_cost": 4.99},
            {'dessert_type': 'Canoli', "dessert_cost": 5.99},
            {'dessert_type': 'Cheesecake', "dessert_cost": 5.99},
        ]
    )
    conn.execute(
        insert(Drinks),# calculate
        [
            {'drink_type': 'Water', "drink_cost": 2.99},
            {'drink_type': 'Coca Cola', "drink_cost": 3.99},
            {'drink_type': 'Pepsi', "drink_cost": 3.98},
            {'drink_type': 'Chocolate Milk', "drink_cost": 3.50},
            {'drink_type': 'Fanta', "drink_cost": 3.97},
        ]
    )
    conn.execute(
        insert(Ingredients),
        [
            {'ingredient_name': 'Cheese', "ingredient_cost": 2.00},
            {'ingredient_name': 'Crust', "ingredient_cost": 5.00},
            {'ingredient_name': 'Tomato sauce', "ingredient_cost": 2.00},
            {'ingredient_name': 'Pineapple', "ingredient_cost": 1.99},
            {'ingredient_name': 'Anchovies', "ingredient_cost": 1.99},
            {'ingredient_name': 'Pepperoni', "ingredient_cost": 1.99},
            {'ingredient_name': 'Salami', "ingredient_cost": 1.99},
            {'ingredient_name': 'Mushrooms', "ingredient_cost": 1.50},
            {'ingredient_name': 'Peppers', "ingredient_cost": 1.50},
            {'ingredient_name': 'Red Onions', "ingredient_cost": 1.50},
            {'ingredient_name': 'Onions', "ingredient_cost": 1.50},
            {'ingredient_name': 'Jalapenos', "ingredient_cost": 1.50},
            {'ingredient_name': 'Sausage', "ingredient_cost": 1.99},
            {'ingredient_name': 'Ham', "ingredient_cost": 1.99},
            {'ingredient_name': 'Prawns', "ingredient_cost": 1.99},
            {'ingredient_name': 'BBQ Chicken', "ingredient_cost": 1.99},
            {'ingredient_name': 'Shawarma', "ingredient_cost": 1.99},
            
        ]
    )
    conn.commit()