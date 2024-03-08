#Copyright 2024, Robert Bresnik, Brez Apps, Inc., ARR
#Built for Cardiff Valero, Encinitas, CA
from flask import Flask, request, render_template, redirect, url_for
from models import init_db, Customer, Car, db_session
import os
import barcode
from barcode.writer import ImageWriter

app = Flask(__name__)
init_db()

BARCODE_PATH = 'static/barcodes'
os.makedirs(BARCODE_PATH, exist_ok=True)  # Ensure the barcode directory exists

def generate_barcode(license_plate):
    barcode_filename = f'{license_plate}.png'
    barcode_path = os.path.join(BARCODE_PATH, barcode_filename)
    Code128 = barcode.get_barcode_class('code128')
    barcode_instance = Code128(license_plate, writer=ImageWriter())
    barcode_instance.save(os.path.join(BARCODE_PATH, license_plate))  # This should match barcode_filename
    
    return barcode_filename  # Return just the filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Placeholder for actual license plate recognition logic
        license_plate = "ABC123"
        return redirect(url_for('customer_info', license_plate=license_plate))
    return render_template('index.html')

@app.route('/customer/<license_plate>', methods=['GET', 'POST'])
def customer_info(license_plate):
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        year = request.form['year']
        make = request.form['make']
        model = request.form['model']

        customer = db_session.query(Customer).filter_by(email=email).first()
        if not customer:
            customer = Customer(name=name, phone=phone, email=email)
            db_session.add(customer)
            db_session.commit()

        car = db_session.query(Car).filter_by(license_plate=license_plate).first()
        if not car:
            car = Car(year=year, make=make, model=model, license_plate=license_plate, customer_id=customer.id)
            db_session.add(car)
            db_session.commit()

        return redirect(url_for('print_receipt', license_plate=license_plate))

    return render_template('customer_info.html', license_plate=license_plate)

@app.route('/receipt/<license_plate>')
def print_receipt(license_plate):
    car = db_session.query(Car).filter_by(license_plate=license_plate).first()
    if not car:
        return "Car not found", 404

    customer = car.customer
    if not customer:
        return "Customer not found", 404

    barcode_filename = generate_barcode(license_plate)
    barcode_image_url = url_for('static', filename=os.path.join('barcodes/', barcode_filename))

    return render_template('receipt.html', customer=customer, car=car, barcode_image_url=barcode_image_url)

if __name__ == '__main__':
    app.run(debug=True)
