from flask import Flask, render_template, request
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from tables import CustomerOrder, Customers 

app = Flask(__name__)

engine = create_engine('mysql+pymysql://root:toolbox@localhost/PizzaShop', echo=True)
Session = sessionmaker(bind=engine)

@app.route('/')
def earnings_report_form():
    return render_template('earnings_report_form.html') 
@app.route('/generate_report', methods=['POST'])
def generate_earnings_report():
    region = request.form.get('region')
    gender = request.form.get('gender')
    min_age = request.form.get('min_age')
    max_age = request.form.get('max_age')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    
    session = Session()
    
    current_date = datetime.now()
    
    query = session.query(
        func.sum(CustomerOrder.order_total).label('total_earnings'),
        func.count(CustomerOrder.order_id).label('total_orders')
    ).join(Customers, Customers.customer_id == CustomerOrder.customer_id)
    
    if region:
        query = query.filter(Customers.postal_code == region)
    
    if gender:
        query = query.filter(Customers.gender == gender)
    
    if min_age:
        min_birthdate = current_date - timedelta(days=int(min_age) * 365)
        query = query.filter(Customers.birthday <= min_birthdate)
    
    if max_age:
        max_birthdate = current_date - timedelta(days=int(max_age) * 365)
        query = query.filter(Customers.birthday >= max_birthdate)
    
    if start_date:
        query = query.filter(CustomerOrder.order_date >= start_date)
    
    if end_date:
        query = query.filter(CustomerOrder.order_date <= end_date)
    
    result = query.one()
    total_earnings = result.total_earnings or 0
    total_orders = result.total_orders or 0
    
    return render_template('report_results.html', total_earnings=total_earnings, total_orders=total_orders)

if __name__ == '__main__':
    app.run(debug=True)
