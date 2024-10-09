from sqlalchemy import create_engine, insert, select, DateTime, update, or_
from tables import Base, Customers, Order, Drinks, Pizza, OrderDrink, Discount
from datetime import datetime
from decimal import Decimal
import random, string

engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)

class Discounts:

    def generate_discount_code(length = 10) -> str: # add a discount code delete functio nthat checks if the discount code is used bt the person
        characters = string.ascii_uppercase + string.digits
        discount_code = ''.join(random.choice(characters)for _ in range(length))
        return discount_code
    
    def check_pizza_count(customer_id: int) -> bool:
        with engine.connect() as conn:

            pizza_count_check = conn.execute(
                select(Customers).where(Customers.customer_id == customer_id)
            ).fetchone()

            if pizza_count_check is not None:
                pizza_count = pizza_count_check[0] 
                
                return pizza_count % 10 == 0
            
        return False
    
    def check_birthday(customer_id: int) -> bool:
        with engine.connect() as conn:

            todays_date = datetime.today().date()

            birthday_check = conn.execute(
                select(Customers).where(Customers.customer_id == customer_id)
            ).fetchone()

            if birthday_check and birthday_check.birthday.date() == todays_date:
                return True
            else:
                return False
    
    def add_discount_code(customer_id: int):
        with engine.connect() as conn:
            customer_check = conn.execute(
                select(Customers.c.pizza_discount_code, Customers.c.pizza_count)
                .where(Customers.c.customer_id == customer_id)
            ).fetchone()

            
            if customer_check is not None:
                pizza_discount_code = customer_check.pizza_discount_code
                pizza_count = customer_check.pizza_count
                
                if Discounts.check_pizza_count(customer_id) and pizza_discount_code is None:
                    # Generate a discount code
                    discount_code = Discounts.generate_discount_code()

                    stmt = (
                        update(Customers)
                        .where(Customers.c.customer_id == customer_id)
                        .values(pizza_discount_code=discount_code)
                    )
                    conn.execute(stmt)
                    conn.commit()

                    #return f"Discount code {discount_code} added to customer {customer_id}"

                elif pizza_discount_code is not None:
                    return f"Customer {customer_id} already has a discount code: {pizza_discount_code}"

            return f"Customer {customer_id} is not eligible for a discount code at this time."
            
    def birthday_message(customer_id:int):
        if Discounts.check_birthday(customer_id):
            print('Its your birthday! You are eligable for a free cheese pizza (vegan or regular) and a drink of your choice!')

    def pizza_discount_message(customer_id:int):
        if Discounts.check_pizza_count(customer_id):
            print('Youve ordered 10 pizzas! You are eligable for a 10% discount on your entire order!')

    def applyBirthdayDiscount(order_id: int, customer_id: int) -> Decimal:
        with engine.connect() as conn:
            # Check if today is the customer's birthday
            if Discounts.check_birthday(customer_id):
                
                order = conn.execute(
                    select(Order).where(Order.order_id == order_id)
                ).fetchone()

                if order:
                    current_total = order.order_total

                    pizza_price = conn.execute(
                        select(Pizza.pizza_price)
                        .where(or_(Pizza.pizza_name == 'Margherita Pizza', Pizza.pizza_name == 'Vegan Margherita Pizza'))
                        .order_by(Pizza.pizza_price.asc())
                        .limit(1)
                    ).fetchone()

                    # Fetch any drink price since all drinks are the same price
                    drink_price = conn.execute(
                        select(Drinks.drink_cost)
                        .limit(1)
                    ).fetchone()

                    if pizza_price and drink_price:
                        discount_amount = pizza_price.pizza_price + drink_price.drink_cost
                        new_total = current_total - discount_amount

                        conn.execute(
                            update(Order).where(Order.order_id == order_id).values(order_total=new_total)
                        )
                        conn.commit()

                        return new_total

        # If no discount is applied, return the original total or 0.00 if the order doesn't exist
        return current_total if order else Decimal('0.00')

    def applyPizzaCountDiscount(customer_id: int):
        with engine.connect() as conn:

            if Discounts.check_pizza_count(customer_id):
                
                customer_check = conn.execute(
                    select(Customers.pizza_discount_code)
                    .where(Customers.customer_id == customer_id)
                ).fetchone()

                if customer_check:
                    pizza_discount_code = customer_check.pizza_discount_code
                    
                    if pizza_discount_code is None:
                        
                        discount_code = Discounts.generate_discount_code()

                        stmt = (
                            update(Customers)
                            .where(Customers.customer_id == customer_id)
                            .values(pizza_discount_code=discount_code)
                        )
                        conn.execute(stmt)
                        conn.commit()

                        print(f"Discount code {discount_code} added to customer {customer_id}.")
                    else:
                        print(f"Customer {customer_id} already has a discount code: {pizza_discount_code}.")
                else:
                    print(f"Customer {customer_id} not found.")
            else:
                print(f"Customer {customer_id} has not yet ordered 10 pizzas.")

    def check_and_remove_discount_code(customer_id: int, discount_code: str):
        with engine.connect() as conn:
            
            discount_used_check = conn.execute(
                select(Discount.discount_used)
                .where(Discount.discount_code == discount_code)
            ).fetchone()

            if discount_used_check:
                discount_used = discount_used_check.discount_used
                
                if discount_used:
                    # update customers discount code to NULL (which is eneabled in the table declaration)
                    stmt = (
                        update(Customers)
                        .where(Customers.customer_id == customer_id)
                        .values(pizza_discount_code=None)
                    )
                    conn.execute(stmt)
                    conn.commit()

                    print(f"Discount code {discount_code} has been used. Customer {customer_id}'s code has been removed.")
                else:
                    print(f"Discount code {discount_code} has not been used.")
            else:
                print(f"Discount code {discount_code} does not exist.")


#Base.metadata.create_all(engine)