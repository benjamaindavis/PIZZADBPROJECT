from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from tables import Customers, CustomerOrder
from datetime import datetime

engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)
Session = sessionmaker(bind=engine)

class orderInsertLogic:
    
    @staticmethod
    def insert_order(username: str, order_total: float, postal_code: str) -> bool:
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
