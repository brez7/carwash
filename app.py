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
        # Placeholder for actual license plate recognition logic
        license_plate = "ABC123"
        return redirect(url_for('customer_info', license_plate=license_plate))
    return render_template('index.html')

@app.route('/customer/<license_plate>', methods=['GET', 'POST'])
def customer_info(license_plate):
    if request.method == 'POST':
        try:
            # Fetch form data
            name = request.form.get('name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            year = request.form.get('year')
            make = request.form.get('make')
            model = request.form.get('model')

            # Fetch or create the customer
            customer = db_session.query(Customer).filter_by(email=email).first()
            if not customer:
                customer = Customer(name=name, phone=phone, email=email)
                db_session.add(customer)
                db_session.flush()  # Prepare the customer ID if a new customer is added

            # Check if a car with the given license plate already exists
            car = db_session.query(Car).filter_by(license_plate=license_plate).first()
            if car:
                # Car exists; optionally update or skip
                # Example: Update car's customer if needed
                # car.customer_id = customer.id
                pass
            else:
                # Create a new car record
                car = Car(year=year, make=make, model=model, license_plate=license_plate, customer_id=customer.id)
                db_session.add(car)

            # Commit the transaction
            db_session.commit()
            return redirect(url_for('print_receipt', license_plate=license_plate))
        except SQLAlchemyError as e:
            db_session.rollback()
            app.logger.error(f"SQLAlchemy Error: {e}")
            return str(e), 500
        except Exception as e:
            db_session.rollback()
            app.logger.error(f"Unexpected Error: {e}")
            return str(e), 500
        

    return render_template('customer_info.html', license_plate=license_plate)

@app.route('/receipt/<license_plate>')
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