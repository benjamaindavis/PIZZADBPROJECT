from sqlalchemy import create_engine, insert, select
from tables import Customers
import bcrypt

engine = create_engine('mysql+pymysql://root:toolbox@127.0.0.1:3306/PizzaShop', echo=True)

class login:
    def hash_password(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    def verify_password(user_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def login(username:str, password:str):
        with engine.connect() as conn:
            #fetch user by username
            user_record = conn.execute(
                select(Customers).where(Customers.username == username)
            ).fetchone()

            if user_record:
                if login.verify_password(password, user_record.password):
                    print("Login successful!")
                    return user_record 
                else:
                    print("Invalid password!")
                    return None
            else:
                print("User not found! Please create an account!")
                return None