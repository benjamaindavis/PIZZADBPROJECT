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
        username: str, order_total: float, postal_code: str,
        pizza_id: int, order_id: int, pizza_amount: int,
        drink_id: int, drink_amount: int,
        dessert_id: int, dessert_amount: int) -> bool:
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

            orderpizza = session.execute(
                select(OrderPizza).where(OrderPizza.pizza_id == pizza_id)
            ).fetchone()

            if not orderpizza:
                return False
            session.execute(insert(OrderPizza).values(
                order_id = order_id,
                pizza_id = pizza_id,
                pizza_amount = pizza_amount
            ))


            session.commit()
            return True 
        
            
            

        except Exception:
            session.rollback()  
            return False  

        finally:
            session.close()
