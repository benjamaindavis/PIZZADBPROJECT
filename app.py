from flask import Flask, render_template, request, redirect, flash, session
from sqlalchemy import create_engine, insert
from tables import CustomerOrder, OrderPizza, OrderDrink, OrderDessert, Pizza, Drinks, Desserts
from sqlalchemy.orm import sessionmaker
from signup import signUp
from login import login 
from datetime import datetime
from Discounts import Discounts

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bigboxofpizza'

engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)
Session = sessionmaker(bind=engine)

def format_item_name(name):  # for no more snake case in order reviews etc.
    return ' '.join(word.capitalize() for word in name.split('_'))

app.jinja_env.globals.update(format_item_name=format_item_name)

@app.route('/')
def login_page():
    return render_template('index.html')

@app.route('/mainmenu')
def mainmenu():
    if 'user_id' in session:
        order = session.get('order', {'pizzas': [], 'drinks': [], 'desserts': []})  # Get order or empty
        return render_template('mainmenu.html', order=order)  
    else:
        return redirect('/')

@app.route('/pizza_menu')
def pizza_menu():
    if 'user_id' in session: 
        return render_template('pizza_menu.html')  
    else:
        return redirect('/')

@app.route('/drink_menu')
def drink_menu():
    if 'user_id' in session:  
        return render_template('drink_menu.html')  
    else:
        return redirect('/')

@app.route('/dessert_menu')
def dessert_menu():
    if 'user_id' in session:  
        return render_template('dessert_menu.html')  
    else:
        return redirect('/')

@app.route('/add_pizza', methods=['POST'])
def add_pizza():
    pizza_name = request.form['pizza']
    pizza = session.query(Pizza).filter(Pizza.pizza_name == pizza_name).first()
    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}
    session['order']['pizzas'].append({'name': pizza_name, 'price': pizza.pizza_price})
    flash(f'Added {pizza_name} pizza to your order!', 'success')  
    return redirect('/mainmenu')  # Redirect to main menu to see updated order

@app.route('/add_drink', methods=['POST'])
def add_drink():
    drink_name = request.form['drink']
    drink = session.query(Drinks).filter(Drinks.drink_type == drink_name).first()
    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}
    session['order']['drinks'].append({'name': drink_name, 'price': drink.drink_cost})
    flash(f'Added {drink_name} to your order!', 'success')  
    return redirect('/mainmenu')  # Redirect to main menu to see updated order

@app.route('/add_dessert', methods=['POST'])
def add_dessert():
    dessert_name = request.form['dessert']
    dessert = session.query(Desserts).filter(Desserts.dessert_type == dessert_name).first()
    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}
    session['order']['desserts'].append({'name': dessert_name, 'price': dessert.dessert_cost})
    flash(f'Added {dessert_name} to your order!', 'success')  
    return redirect('/mainmenu')  # Redirect to main menu to see updated order

@app.route('/cart')
def cart():
    if 'order' in session:
        return render_template('cart.html', order=session['order'])
    else:
        flash('Your cart is empty!', 'info')
        return redirect('/mainmenu')

@app.route('/remove_item', methods=['POST'])
def remove_item():
    item_type = request.form['item_type']
    item_name = request.form['item_name']
    
    if 'order' in session:
        if item_type in session['order']:
            session['order'][item_type] = [item for item in session['order'][item_type] if item['name'] != item_name]
            flash(f'Removed {item_name} from your order!', 'success')
        else:
            flash(f'Item type {item_type} not found in order.', 'danger')
    return redirect('/cart')  # Redirect to cart after removal

@app.route('/order')
def order_summary():
    if 'order' in session:
        return render_template('order_summary.html', order=session['order'])
    else:
        return redirect('/mainmenu')

@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    user = login.login(username, password)

    if user:
        session['user_id'] = user.customer_id
        session['username'] = user.username 
        return redirect('/mainmenu') 
    else:
        flash('Invalid username or password!', 'danger')
        return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        birthday = request.form['birthday']
        postal_code = request.form['postal_code']

        if signUp.signUp(full_name, username, password, birthday, postal_code):
            flash('Sign up successful! You can now log in.', 'success')
            return redirect('/')  
        else:
            flash('Username is already taken. Try a different one.', 'danger')

    return render_template('signup.html')

@app.route('/finalize_order', methods=['GET', 'POST'])
def finalize_order():
    if request.method == 'GET':
        if 'order' in session:
            return render_template('finalize_order.html', order=session['order'])
        else:
            flash('Your cart is empty. Add items to your order.', 'info')
            return redirect('/mainmenu')
    elif request.method == 'POST':
        if 'user_id' in session and 'order' in session:
            customer_id = session['user_id']
            order = session['order']
            delivery_address = request.form.get('delivery_address', 'Default Address')  # Get delivery address from form
            save_order_to_db(customer_id, order, delivery_address)
            session.pop('order', None)  # Clear the session order after finalizing
            flash('Your order has been placed successfully!', 'success')
            return redirect('/delivery')  # Redirect to the delivery page
        else:
            flash('You need to be logged in and have items in your cart to place an order.', 'error')
            return redirect('/mainmenu')

@app.route('/delivery')
def delivery():
    return render_template('delivery.html')  # Render the delivery page

def save_order_to_db(customer_id, order, delivery_address):
    connection = engine.connect()
    transaction = connection.begin()
    try:
        # Calculate the total order price
        total_price = 0.0
        for item_type, items in order.items():
            for item in items:
                if item_type == 'pizzas':
                    pizza = connection.execute(
                        Pizza.__table__.select().where(Pizza.pizza_name == item['name'])
                    ).fetchone()
                    total_price += pizza.pizza_price
                elif item_type == 'drinks':
                    drink = connection.execute(
                        Drinks.__table__.select().where(Drinks.drink_type == item['name'])
                    ).fetchone()
                    total_price += drink.drink_cost
                elif item_type == 'desserts':
                    dessert = connection.execute(
                        Desserts.__table__.select().where(Desserts.dessert_type == item['name'])
                    ).fetchone()
                    total_price += dessert.dessert_cost

        # Insert a new CustomerOrder entry
        customer_order_stmt = insert(CustomerOrder).values(
            customer_id=customer_id,
            order_total=total_price,
            delivery_address=delivery_address,
            cancel_time=False,
            order_datetime=datetime.now()
        )
        result = connection.execute(customer_order_stmt)
        order_id = result.inserted_primary_key[0]

        # Insert items into the respective order tables
        for item_type, items in order.items():
            for item in items:
                if item_type == 'pizzas':
                    pizza = connection.execute(
                        Pizza.__table__.select().where(Pizza.pizza_name == item['name'])
                    ).fetchone()
                    order_pizza_stmt = insert(OrderPizza).values(
                        order_id=order_id,
                        pizza_id=pizza.pizza_id,
                        pizza_amount=1  # Assuming 1 pizza per entry in the order
                    )
                    connection.execute(order_pizza_stmt)
                elif item_type == 'drinks':
                    drink = connection.execute(
                        Drinks.__table__.select().where(Drinks.drink_type == item['name'])
                    ).fetchone()
                    order_drink_stmt = insert(OrderDrink).values(
                        order_id=order_id,
                        drink_id=drink.drink_id,
                        drink_amount=1  # Assuming 1 drink per entry in the order
                    )
                    connection.execute(order_drink_stmt)
                elif item_type == 'desserts':
                    dessert = connection.execute(
                        Desserts.__table__.select().where(Desserts.dessert_type == item['name'])
                    ).fetchone()
                    order_dessert_stmt = insert(OrderDessert).values(
                        order_id=order_id,
                        dessert_id=dessert.dessert_id,
                        dessert_amount=1  # Assuming 1 dessert per entry in the order
                    )
                    connection.execute(order_dessert_stmt)

        transaction.commit()  # Commit the transaction
    except Exception as e:
        transaction.rollback()  # Rollback on error
        print(f"Error occurred: {e}")
    finally:
        connection.close()  # Always close the connection

if __name__ == '__main__':
    app.run(debug=True)
