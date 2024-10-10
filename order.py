from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy import engine
from tables import Customers, CustomerOrder, OrderPizza, OrderDrink, OrderDessert, Pizza, Drinks, Desserts, PizzaIngredients, Ingredients, DeliveryPersonnel

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

class OrderProcessing:
    
    def __init__(self, customer_id):
        self.customer_id = customer_id
    
    def place_order(self, pizzas, drinks=None, desserts=None, delivery_address=None):
        # Ensure the order includes at least one pizza
        if not pizzas:
            raise ValueError("Order must include at least one pizza.")
        
        # Calculate total price
        order_total = 0
        for pizza_id, amount, toppings in pizzas:
            pizza = session.query(Pizza).filter(Pizza.pizza_id == pizza_id).first()
            pizza_price = pizza.pizza_price
            
            # Add topping costs to the pizza price
            for topping_id in toppings:
                topping = session.query(Ingredients).filter(Ingredients.ingredient_id == topping_id).first()
                pizza_price += topping.ingredient_cost
            
            # Add to order total
            order_total += pizza_price * amount
        
        # Add drinks and desserts if any
        if drinks:
            for drink_id, amount in drinks:
                drink = session.query(Drinks).filter(Drinks.drink_id == drink_id).first()
                order_total += drink.drink_cost * amount
        
        if desserts:
            for dessert_id, amount in desserts:
                dessert = session.query(Desserts).filter(Desserts.dessert_id == dessert_id).first()
                order_total += dessert.dessert_cost * amount
        
        # Create the customer order
        new_order = CustomerOrder(
            customer_id=self.customer_id,
            order_total=order_total,
            delivery_address=delivery_address,
            cancel_time=False,
            delivery_time_minutes=30  # Estimated delivery time
        )
        session.add(new_order)
        session.commit()  # Commit so the order_id is generated

        # Add pizzas and toppings to the order
        for pizza_id, amount, toppings in pizzas:
            session.add(OrderPizza(order_id=new_order.order_id, pizza_id=pizza_id, pizza_amount=amount))
            
            # Add the toppings to the PizzaIngredients table
            for topping_id in toppings:
                session.add(PizzaIngredients(pizza_id=pizza_id, ingredient_id=topping_id))
        
        if drinks:
            for drink_id, amount in drinks:
                session.add(OrderDrink(order_id=new_order.order_id, drink_id=drink_id, drink_amount=amount))
        
        if desserts:
            for dessert_id, amount in desserts:
                session.add(OrderDessert(order_id=new_order.order_id, dessert_id=dessert_id, dessert_amount=amount))
        
        session.commit()

        return f"Order placed successfully! Your total is ${order_total:.2f}. Estimated delivery time: 30 minutes."

    def confirm_order(self, order_id):
        """
        Confirm the order for the customer, showing order details and delivery time.
        """
        order = session.query(CustomerOrder).filter(CustomerOrder.order_id == order_id).first()
        if not order:
            return f"No order found with ID {order_id}."
        
        # Fetch pizzas, drinks, and desserts for the order
        pizzas = session.query(OrderPizza).filter(OrderPizza.order_id == order_id).all()
        drinks = session.query(OrderDrink).filter(OrderDrink.order_id == order_id).all()
        desserts = session.query(OrderDessert).filter(OrderDessert.order_id == order_id).all()

        # Display order confirmation
        confirmation_details = f"Order ID: {order_id}\n"
        confirmation_details += f"Total: ${order.order_total:.2f}\n"
        confirmation_details += "Pizzas:\n"
        for pizza in pizzas:
            pizza_info = session.query(Pizza).filter(Pizza.pizza_id == pizza.pizza_id).first()
            confirmation_details += f"{pizza_info.pizza_name} (x{pizza.pizza_amount})\n"
            
            # Fetch and display toppings
            toppings = session.query(PizzaIngredients).filter(PizzaIngredients.pizza_id == pizza.pizza_id).all()
            if toppings:
                confirmation_details += "Toppings:\n"
                for topping in toppings:
                    topping_info = session.query(Ingredients).filter(Ingredients.ingredient_id == topping.ingredient_id).first()
                    confirmation_details += f"- {topping_info.ingredient_name}\n"
        
        if drinks:
            confirmation_details += "Drinks:\n"
            for drink in drinks:
                drink_info = session.query(Drinks).filter(Drinks.drink_id == drink.drink_id).first()
                confirmation_details += f"{drink_info.drink_type} (x{drink.drink_amount})\n"
        
        if desserts:
            confirmation_details += "Desserts:\n"
            for dessert in desserts:
                dessert_info = session.query(Desserts).filter(Desserts.dessert_id == dessert.dessert_id).first()
                confirmation_details += f"{dessert_info.dessert_type} (x{dessert.dessert_amount})\n"
        
        confirmation_details += f"Estimated delivery time: {order.delivery_time_minutes} minutes\n"
        return confirmation_details

    def restaurant_monitoring(self):
        pending_orders = session.query(CustomerOrder).filter(CustomerOrder.cancel_time == False).all()
        if not pending_orders:
            return "No pending orders."

        display = "Pending Orders:\n"
        for order in pending_orders:
            pizzas = session.query(OrderPizza).filter(OrderPizza.order_id == order.order_id).all()
            display += f"Order ID: {order.order_id}, Delivery Address: {order.delivery_address}\n"
            display += "Pizzas:\n"
            for pizza in pizzas:
                pizza_info = session.query(Pizza).filter(Pizza.pizza_id == pizza.pizza_id).first()
                display += f"{pizza_info.pizza_name} (x{pizza.pizza_amount})\n"
                
                # Fetch and display toppings
                toppings = session.query(PizzaIngredients).filter(PizzaIngredients.pizza_id == pizza.pizza_id).all()
                if toppings:
                    display += "Toppings:\n"
                    for topping in toppings:
                        topping_info = session.query(Ingredients).filter(Ingredients.ingredient_id == topping.ingredient_id).first()
                        display += f"- {topping_info.ingredient_name}\n"
            
            display += "\n"
        
        return display

