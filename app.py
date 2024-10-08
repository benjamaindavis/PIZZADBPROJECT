from flask import Flask, render_template, request, redirect, flash
from sqlalchemy import create_engine
from tables import Customers
from Sign_up import signUp
from login import login 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bigboxofpizza'

engine = create_engine('mysql+pymysql://root:toolbox@127.0.0.1:3306/PizzaShop', echo = True)

@app.route('/')
def login_page():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    user = login.login(username, password)

    if user:
        flash('Login successful!', 'success')
        return redirect('/')  # redircets page to home page (not made yet)
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

if __name__ == "__main__":
    app.run(debug=True)
