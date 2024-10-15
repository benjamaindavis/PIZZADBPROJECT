from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from tables import Customers
import bcrypt

engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)
Session = sessionmaker(bind=engine)

class signUp:
    @staticmethod
    def hash_password(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    @staticmethod
    def signUp(full_name: str, username: str, password: str, birthday: str, postal_code: str):
        hashed_password = signUp.hash_password(password)

        session = Session()  
        try:
            
            existing_user = session.execute(
                select(Customers).where(Customers.username == username)
            ).fetchone()

            if existing_user:
                print("Username is taken!")
                return None

            
            session.execute(insert(Customers).values(
                full_name=full_name,
                username=username,
                password=hashed_password,
                birthday=birthday,
                pizza_count=0,
                postal_code=postal_code
            ))

            session.commit()  
            print("Signup successful!")
            return True  

        except Exception as e:
            session.rollback()  
            print(f"An error occurred: {e}")
            return False  

        finally:
            session.close()  
