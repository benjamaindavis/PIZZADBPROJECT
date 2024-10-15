from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from tables import Customers, CustomerOrder, OrderPizza, OrderDessert, OrderDrink
from datetime import datetime

engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)
Session = sessionmaker(bind=engine)

class orderInsertLogic:
    @staticmethod
    def insert_order(
        username: str, order_total: float, postal_code: str,) -> bool:
        session = Session()  
        
        try:
            customer = session.execute(
                select(Customers).where(Customers.username == username)
            ).fetchone()

            if not customer:
                return False  
            session.execute(insert(CustomerOrder).values(
                username=username,
                order_total=order_total,
                postal_code=postal_code,
                order_datetime=datetime.now() 
            ))
            session.commit()
            return True 
        
        except Exception:
            session.rollback()  
            return False  

        finally:
            session.close()

    def insert_order_pizza(order_id: int, pizza_id: int, pizza_amount: int) -> bool:
        session = Session()

        try:
            orderpizza = session.execute(
                select(OrderPizza).where(OrderPizza.order_id == order_id)
            ).fetchone()

            if not orderpizza:
                return False  
            session.execute(insert(OrderPizza).values(
                pizza_id = pizza_id,
                order_id = order_id,
                pizza_amount = pizza_amount
            ))
            session.commit()
            return True 
    
        except Exception:
            session.rollback()  
            return False  

        finally:
            session.close()

        
    def insert_order_drink(order_id: int, drink_id: int, drink_amount: int) -> bool:
        session = Session()

        try:
            orderdrink = session.execute(
                select(OrderDrink).where(OrderDrink.order_id == order_id)
            ).fetchone()

            if not orderdrink:
                return False  
            session.execute(insert(OrderDrink).values(
                drink_id = drink_id,
                order_id = order_id,
                drink_amount = drink_amount
            ))
            session.commit()
            return True 
    
        except Exception:
            session.rollback()  
            return False  

        finally:
            session.close()

    def insert_order_dessert(order_id: int, dessert_id: int, dessert_amount: int) -> bool:    
        session = Session()

        try:
            orderdessert = session.execute(
                select(OrderDessert).where(OrderDessert.order_id == order_id)
            ).fetchone()

            if not orderdessert:
                return False  
            session.execute(insert(OrderDessert).values(
                dessert_id = dessert_id,
                order_id = order_id,
                dessert_amount = dessert_amount
            ))
            session.commit()
            return True 
    
        except Exception:
            session.rollback()  
            return False  

        finally:
            session.close()