from flask import Flask, render_template, request, redirect, flash, session
from sqlalchemy import create_engine
from tables import Customers
from signup import signUp
from login import login 
from Discounts import Discounts

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bigboxofpizza'

engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)

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
    pizza = request.form['pizza']
    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}
    session['order']['pizzas'].append(pizza)
    flash(f'Added {pizza} pizza to your order!', 'success')  # Flash message
    return redirect('/mainmenu')  # Redirect to main menu to see updated order

@app.route('/add_drink', methods=['POST'])
def add_drink():
    drink = request.form['drink']
    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}
    session['order']['drinks'].append(drink)
    flash(f'Added {drink} to your order!', 'success')  # Flash message
    return redirect('/mainmenu')  # Redirect to main menu to see updated order

@app.route('/add_dessert', methods=['POST'])
def add_dessert():
    dessert = request.form['dessert']
    if 'order' not in session:
        session['order'] = {'pizzas': [], 'drinks': [], 'desserts': []}
    session['order']['desserts'].append(dessert)
    flash(f'Added {dessert} to your order!', 'success')  # Flash message
    return redirect('/mainmenu')  # Redirect to main menu to see updated order

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

@app.route('/remove_item', methods=['POST'])
def remove_item():
    item_type = request.form['item_type']
    item_name = request.form['item_name']
    
    if 'order' in session:
        if item_type in session['order']:
            session['order'][item_type] = [item for item in session['order'][item_type] if item != item_name]
    
    flash(f'Removed {item_name} from your order!', 'success')
    return redirect('/mainmenu')  # Redirect back to the main menu

def check_birthday_discounts():
    if 'user_id' in session:
        customer_id = session['user_id']
        Discounts.add_discount_code(customer_id)
        Discounts.birthday_message(customer_id)
        Discounts.pizza_discount_message(customer_id)

@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    session.pop('username', None) 
    flash('You have been logged out.', 'info')
    return redirect('/') 

@app.route('/finalize_order', methods=['POST'])
def finalize_order():
    session.pop('order', None)
    flash('Your order has been placed successfully!', 'success')
    return redirect('/mainmenu')

if __name__ == "__main__":
    app.run(debug=True)
