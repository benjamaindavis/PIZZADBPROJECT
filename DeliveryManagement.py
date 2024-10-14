from datetime import datetime, timedelta
from tables import DeliveryPersonnel, CustomerOrder  # Assuming the correct path is 'tables'
from sqlalchemy import func

class DeliveryManagement: 
    def __init__(self, session):  # Fixed __init__ method
        self.session = session

    def update_order_status(self, order_id, new_status):
        order = self.session.query(CustomerOrder).filter_by(order_id=order_id).first()
        if order:
            order.status = new_status
            self.session.commit()

    def cancel_order(self, order_id):
        order = self.session.query(CustomerOrder).filter_by(order_id=order_id).first()

        if order:
            current_time = datetime.now()
            cancel_limit = current_time - timedelta(minutes=5)

            if order.delivery_time and order.delivery_time >= cancel_limit:
                order.cancel_time = current_time
                order.status = 'Cancelled'
                self.session.commit()
                return f"Order {order_id} has been cancelled."
            else:
                return f"Cannot cancel Order {order_id}. Cancellation time has passed."
        return f"Order {order_id} not found."

    def assign_delivery_person(self, order_id):
        order = self.session.query(CustomerOrder).filter_by(order_id = order_id).first()

        if not order:
            return f"Order {order_id} not found"
        
        personnel = self.session.query(DeliveryPersonnel).filter_by(
            postal_code_assigned = order.delivery_address, is_available = True
        ).order_by(func.random()).first()  # Assigning random available delivery person
        
        if not personnel:
            return f"No available delivery personnel for Postal Code {order.delivery_address}"
        
        personnel.is_available = False
        personnel.next_available_time = datetime.now() + timedelta(minutes = 30)
        order.status = 'Out for Delivery'
        self.session.commit()
        return f"Delivery person {personnel.full_name} assigned to Order {order_id}."

    def check_delivery_personnel_availability(self):
        current_time = datetime.now()
        personnel = self.session.query(DeliveryPersonnel).filter(
            DeliveryPersonnel.next_available_time <= current_time
        ).all()
        
        for person in personnel:
            person.is_available = True
            person.next_available_time = None

        self.session.commit()

    def batch_delivery(self, postal_code, max_pizzas = 3, window_minutes = 3):
        current_time = datetime.now()
        batch_limit = current_time - timedelta(minutes = window_minutes)

        orders = self.session.query(CustomerOrder).filter(
            CustomerOrder.delivery_address == postal_code,
            CustomerOrder.status == 'Being Prepared',
            CustomerOrder.delivery_time >= batch_limit
        ).all()
        
        if len(orders) > max_pizzas:
            orders = orders[:max_pizzas]  # Limit 3 pizzas per batch

        for order in orders:
            self.assign_delivery_person(order.order_id)

        return f"{len(orders)} orders grouped for delivery in postal code {postal_code}."



    