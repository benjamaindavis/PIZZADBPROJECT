from flask import Flask, render_template, request, redirect, flash, session
from sqlalchemy import create_engine, insert
from tables import Customers, CustomerOrder, OrderPizza, OrderDrink, OrderDessert, Pizza, Drinks, Desserts
from sqlalchemy.orm import sessionmaker
from signup import signUp
from login import login 
from datetime import datetime
from Discounts import Discounts
from orderinsertlogic import orderInsertLogic

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

@app.route('/deliverypage')
def delivery_page():
    if 'user_id' in session:
        return render_template('deliverypage.html')
    else:
        return redirect('/')

# Add pizza to the cart and redirect to main menu
@app.route('/add_pizza', methods=['POST'])
def add_pizza():
    db_session = Session()
    pizza_name = request.form['pizza']
    pizza = db_session.query(Pizza).filter(Pizza.pizza_name == pizza_name).first()

    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}

    session['order']['pizzas'].append({'name': pizza_name, 'price': pizza.pizza_price})
    session.modified = True  # Mark session as modified

    db_session.close()
    return redirect('/mainmenu')

# Add drink to the cart
@app.route('/add_drink', methods=['POST'])
def add_drink():
    db_session = Session()
    drink_name = request.form['drink']
    drink = db_session.query(Drinks).filter(Drinks.drink_type == drink_name).first()

    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}

    session['order']['drinks'].append({'name': drink_name, 'price': drink.drink_cost})
    session.modified = True

    db_session.close()
    return redirect('/mainmenu')

# Add dessert to the cart
@app.route('/add_dessert', methods=['POST'])
def add_dessert():
    db_session = Session()
    dessert_name = request.form['dessert']
    dessert = db_session.query(Desserts).filter(Desserts.dessert_type == dessert_name).first()

    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}

    session['order']['desserts'].append({'name': dessert_name, 'price': dessert.dessert_cost})
    session.modified = True

    db_session.close()
    return redirect('/mainmenu')

# Show the cart page
@app.route('/cart')
def cart():
    if 'order' in session:
        order = session['order']
        
        # Total cost
        total_cost = round(sum(float(item['price']) for item in order['pizzas'] + order['drinks'] + order['desserts']), 2)        
        
        return render_template('cart.html', order=order, total_cost=total_cost)
    else:
        flash('Your cart is empty!', 'info')
        return redirect('/mainmenu')

@app.route('/remove_item', methods=['POST'])
def remove_item():
    item_type = request.form['item_type']
    item_name = request.form['item_name']

    if 'order' in session and item_type in session['order']:
        for item in session['order'][item_type]:
            if item['name'] == item_name:
                session['order'][item_type].remove(item)
                session.modified = True
                flash(f'Removed {format_item_name(item_name)} from your order!', 'success')
                break
        else:
            flash('Item not found in your cart.', 'danger')
    else:
        flash('Item not found in your cart.', 'danger')

    return redirect('/cart')

@app.route('/finalize_order', methods=['POST'])
def finalize_order(): # MAYBE ADD THE orderpizza, orderdrink, and orderdessert INSERTIONG HERE AFTER THE ORDER IS EENT IN??????
    if 'user_id' in session:
        total_cost = round(sum(float(item['price']) for item in session['order']['pizzas'] +
                              session['order']['drinks'] + session['order']['desserts']), 2)
        print(total_cost)
        postal_code = session.get('postal_code') 
        print(postal_code)
        print(session['username'])
        # Insert the order into the database
        if orderInsertLogic.insert_order(session['username'], total_cost, postal_code):
            flash('Order successfully placed!', 'success')
            session.pop('order', None)
            return redirect('/deliverypage')  # Redirect to delivery page
        else:
            flash('Failed to place the order. Please try again.', 'danger')

    return redirect('/mainmenu')

@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']
    user = login.login(username, password)

    if user:
        session['user_id'] = user.customer_id
        session['username'] = user.username
        session['postal_code'] = user.postal_code  # Store the user's postal code in the session
        flash('Successfully logged in!', 'success')
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
            # Store postal code and username in session
            session['username'] = username
            session['postal_code'] = postal_code
            flash('Sign up successful! You can now log in.', 'success')
            return redirect('/')
        else:
            flash('Username is already taken. Try a different one.', 'danger')

    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
