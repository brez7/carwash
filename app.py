from flask import Flask, request, render_template, redirect, url_for, current_app
from models import db_session, Customer, Car, init_db
import os
import barcode
from barcode.writer import ImageWriter
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__)

# Initialize the database
init_db()

BARCODE_PATH = 'static/barcodes'
os.makedirs(BARCODE_PATH, exist_ok=True)  # Ensure the barcode directory exists

def generate_barcode(license_plate):
    barcode_filename = f'{license_plate}.png'
    barcode_path = os.path.join(BARCODE_PATH, barcode_filename)
    Code128 = barcode.get_barcode_class('code128')
    barcode_instance = Code128(license_plate, writer=ImageWriter())
    barcode_instance.save(barcode_path)
    
    return barcode_filename  # Return just the filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        license_plate = request.form.get('license_plate')
        if license_plate:
            return redirect(url_for('customer_info', license_plate=license_plate))
    return render_template('index.html')

@app.route('/customer/<license_plate>', methods=['GET', 'POST'])
def customer_info(license_plate):
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        year = request.form.get('year')
        make = request.form.get('make')
        model = request.form.get('model')

        try:
            # Check if customer exists
            customer = db_session.query(Customer).filter_by(email=email).first()
            if not customer:
                customer = Customer(name=name, phone=phone, email=email)
                db_session.add(customer)
                db_session.flush()  # Ensure the customer has an ID for the new car

            # Check if a car with the given license plate already exists
            car = db_session.query(Car).filter_by(license_plate=license_plate).first()
            if car:
                # Update existing car and customer info
                car.year = year
                car.make = make
                car.model = model
                car.customer = customer  # Associate the car with the (possibly new) customer
            else:
                # Create a new car entry
                car = Car(year=year, make=make, model=model, license_plate=license_plate, customer=customer)
                db_session.add(car)
            
            # Commit transaction
            db_session.commit()
            return redirect(url_for('print_receipt', license_plate=license_plate))

        except SQLAlchemyError as e:
            db_session.rollback()
            app.logger.error(f"SQLAlchemy Error: {e}")
            return f"Database error occurred: {e}", 500
        except Exception as e:
            db_session.rollback()
            app.logger.error(f"Unexpected Error: {e}")
            return f"An unexpected error occurred: {e}", 500

    else:  # Handle GET request
        car = db_session.query(Car).filter_by(license_plate=license_plate).first()
        existing_car_info = {}
        if car:
            existing_car_info = {
                "name": car.customer.name,
                "phone": car.customer.phone,
                "email": car.customer.email,
                "year": car.year,
                "make": car.make,
                "model": car.model
            }
        return render_template('customer_info.html', license_plate=license_plate, existing_car_info=existing_car_info)

@app.route('/<license_plate>')
def print_receipt(license_plate):
    try:
        car = db_session.query(Car).filter_by(license_plate=license_plate).first()
        if not car:
            raise ValueError("Car not found")

        customer = car.customer
        if not customer:
            raise ValueError("Customer not found")

        barcode_filename = generate_barcode(license_plate)
        barcode_image_url = url_for('static', filename=os.path.join('barcodes/', barcode_filename))

        return render_template('receipt.html', customer=customer, car=car, barcode_image_url=barcode_image_url)
    except Exception as e:
        current_app.logger.error(f"Error when printing receipt: {e}")
        return str(e), 404

if __name__ == '__main__':
    app.run(debug=True)