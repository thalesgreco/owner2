from cs50 import SQL
from flask import redirect, render_template, request, session, jsonify
from functools import wraps

db = SQL("sqlite:///pms.db")


class User:  # Class to deal with users data in DB
    def __init__(self, user_id):  # Start the Class loading user information from DB
        self.id = user_id
        table = db.execute("SELECT * FROM users WHERE id = ?;", self.id)
        table = table[0]
        self.username = table['username']
        self.first_name = table['first_name']
        self.last_name = table['last_name']
        self.company = table['company_id']
        self.admin = table['admin']
        self.properties = []  # Get user's company properties
        props = db.execute("SELECT id FROM properties WHERE company_id = ?", self.company)
        for prop in props:
            self.properties.append(prop['id'])


class Company:  # Class to manage Company in Database
    def __init__(self, company_id):
        self.id = company_id

    def load(self):  # Load Company info and return as dictionary
        table = db.execute("SELECT * FROM companies WHERE id = ?;", self.id)
        table = table[0]
        self.name = table['name']
        self.address = table['address']
        self.city = table['city']
        self.state = table['state']
        self.country = table['country']
        self.email = table['email']
        self.phone = table['phone']
        return table

    def properties(company_id):  # Load all Company's properties ids from database
        list = []
        ids = db.execute(
            "SELECT id FROM properties "
            "WHERE company_id = ?;", company_id
        )
        for id in ids:
            list.append(id['id'])
        return list  # return a list with props ids

    def update(company_id, data):  # Update Company Info in Database providing Id and Dict with data
        try:
            db.execute(
                "UPDATE companies SET name = ?, "
                "address = ?, state = ?, country = ?, "
                "email = ?, phone = ?, site = ? "
                "WHERE id = ?;",
                data['name'],
                data['address'],
                data['state'],
                data['country'],
                data['email'],
                data['phone'],
                data['site'],
                company_id
            )
            return jsonify({'status': 'success'})  # Return the status success in json if data was loaded correctly
        except:
            return jsonify({'status': 'error'})


class Booking:  # Class to deal with Booking data in Database
    def __init__(self, booking_id):  # Initialize Class with user allowed to manage the booking
        self.id = booking_id
        user_ids = db.execute("SELECT user_id FROM bookings WHERE id = ?;", self.id)
        self.user_id = user_ids[0]['user_id']
        return

    def load(self):  # Load Booking information from DB and return as dict
        rows = db.execute("SELECT bookings.id, properties.name, "
                          "properties.company_id, bookings.night_price, bookings.clean_price, "
                          "guests.card_id, guests.first_name, guests.last_name, guests.birth, "
                          "guests.email, guests.phone, guests.vip, "
                          "bookings.lock_code, bookings.checkin, bookings.checkout, "
                          "bookings.price, bookings.extra_charges, bookings.paid, "
                          "bookings.active, users.first_name AS user_name "
                          "FROM bookings INNER JOIN properties ON bookings.property_id = properties.id "
                          "INNER JOIN guests ON bookings.guest_id = guests.id "
                          "INNER JOIN users ON bookings.user_id = users.id "
                          "WHERE bookings.id = ?;", self.id)
        rows = rows[0]
        table = db.execute("SELECT * FROM bookings WHERE id = ?;", self.id)
        table = table[0]
        self.property_id = table['property_id']
        self.company_id = rows['company_id']
        table['property_name'] = rows['name']
        table['night_price'] = rows['night_price']
        table['clean_price'] = rows['clean_price']
        self.guest_id = table['guest_id']
        table['first_name'] = rows['first_name']
        table['last_name'] = rows['last_name']
        table['birth'] = rows['birth']
        table['email'] = rows['email']
        table['phone'] = rows['phone']
        table['vip'] = rows['vip']
        self.card_id = rows['card_id']
        self.price = table['price']
        self.checkin = table['checkin']
        self.checkout = table['checkout']
        self.paid = table['paid']
        self.lock_code = table['lock_code']
        self.gate_code = table['gate_code']
        self.user_id = table['user_id']
        table['user_name'] = rows['user_name']
        return table

    def update(booking_id, table):  # Update booking information in DB providing booking id and dict with information to update
        try:  # Check some table info that should be number and converts to the right format
            table['user_id'] = to_int(table['user_id'])
            table['lock_code'] = to_int(table['lock_code'])
            table['gate_code'] = to_int(table['gate_code'])
            table['night_price'] = to_float(table['night_price'])
            table['clean_price'] = to_float(table['clean_price'])
            table['price'] = to_float(table['price'])
            table['extra_charges'] = to_float(table['extra_charges'])

            # UPDATE BOOKING INFO IN DB
            db.execute(
                "UPDATE bookings "
                "SET user_id = ?,"
                "checkin = ?, checkout = ?,"
                "lock_code = ?, gate_code = ?,"
                "night_price = ?, clean_price = ?, extra_charges = ?, "
                "price = ?, paid = 0 "
                "WHERE id = ?;",
                table['user_id'],
                table['checkin'],
                table['checkout'],
                table['lock_code'],
                table['gate_code'],
                table['night_price'],
                table['clean_price'],
                table['extra_charges'],
                table['price'],
                int(booking_id)
            )
            db.execute(  # Update Payments table with new amounts
                "UPDATE payments "
                "SET last_amount = ?, payday = CURRENT_TIMESTAMP "
                "WHERE booking_id = ?;",
                table['price'], int(booking_id)
            )

            # UPDATE GUEST INFO
            guest_ids = db.execute("SELECT guest_id FROM bookings "
                                   "WHERE user_id= ? AND id = ?;",
                                   table['user_id'], booking_id
                                   )
            guest = guest_ids[0]['guest_id']
            table['vip'] = to_int(table['vip'])

            db.execute("UPDATE guests SET "
                       "first_name = ?, last_name = ?, birth = ?,"
                       "email = ?, phone = ?, vip = ? "
                       "WHERE id = ?;",
                       table['first_name'], table['last_name'], table['birth'],
                       table['email'], table['phone'],
                       table['vip'], guest
                       )
            return jsonify({'status': 'success'})  # Return the Status of the update in JSON
        except:
            return jsonify({'status': 'error'})

    def add(table):  # Creates a new booking passing a dict with data as argument

        #  Check for the types of info and set the right one to insert into DB
        table['user_id'] = to_int(table['user_id'])
        table['property_id'] = to_int(table['property_id'])
        table['lock_code'] = to_int(table['lock_code'])
        table['gate_code'] = to_int(table['gate_code'])
        table['night_price'] = to_float(table['night_price'])
        table['clean_price'] = to_float(table['clean_price'])
        table['extra_charges'] = to_float(table['extra_charges'])
        table['price'] = to_float(table['price'])
        table['vip'] = to_int(table['vip'])

        db.execute(  # Execute query to create a new Guest into database
            "INSERT INTO guests("
            "first_name, last_name, birth,"
            "email, phone, vip)"
            "VALUES(?, ?, ?, ?, ?, ?);",
            table['first_name'], table['last_name'], table['birth'],
            table['email'], table['phone'], table['vip']
        )
        guest_id = db.execute(  # Execute the query to get the new guest ID
            "SELECT id FROM guests "
            "WHERE first_name = ? "
            "AND birth = ? "
            "AND email= ?;",
            table['first_name'], table['birth'], table['email']
        )
        guest_id = guest_id[0]['id']  # Get the guest id and save into var

        db.execute(  # Execute the query to create a new booking into DB
            "INSERT INTO bookings("
            "user_id, property_id, guest_id,"
            "checkin, checkout,"
            "lock_code, gate_code,"
            "night_price, clean_price, extra_charges, "
            "price, paid) "
            "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            table['user_id'], table['property_id'], guest_id,
            table['checkin'], table['checkout'],
            table['lock_code'], table['gate_code'],
            table['night_price'], table['clean_price'], table['extra_charges'],
            table['price'], table['paid']
        )
        #  Gets the created booking ID
        booking_id = db.execute("SELECT id FROM bookings "
                                "WHERE guest_id = ? "
                                "AND checkin = ?;", guest_id, table['checkin'])
        booking_id = booking_id[0]['id']
        return booking_id  # Return the new booking id

    def property(self):  # Get booking property data from Class Property and return the dict with data
        prop = Property(self.property_id).load()
        return prop


class Payment:  # Class to manage Payments in Database
    def __init__(self, payment_id):
        self.id = payment_id  # Initialize it will just return with id var
        return

    def load(self):  # load payments info and return dict with payment information
        payment = db.execute("SELECT guests.first_name, guests.last_name, guests.birth,"
                             "guests.email, guests.phone,"
                             "payments.id, payments.company_id, "
                             "payments.last_amount, payments.amount_paid, payments.method "
                             "FROM payments INNER JOIN bookings ON bookings.id = payments.booking_id "
                             "INNER JOIN guests ON guests.id = bookings.guest_id "
                             "WHERE payments.id = ?;", self.id)
        payment = payment[0]
        return payment

    def update(self, table):  # save changes of payment info into DB with dict as argument
        method = table['method']
        try:
            amount_paid = float(table['amount_paid'])
        except:
            amount_paid = 0
        db.execute("UPDATE payments SET "
                   "method = ?, amount_paid = ?, payday = CURRENT_TIMESTAMP "
                   "WHERE id = ?;", method, amount_paid, self.id)
        return self.id

    def paid(self, state):  # Change column Paid in the Booking from this payment to 0 or 1
        booking_id = db.execute("SELECT booking_id FROM payments WHERE id = ? LIMIT 1;", self.id)
        booking_id = booking_id[0]
        db.execute("UPDATE bookings SET paid = ? WHERE id = ?;", state, booking_id['booking_id'])

    def add(company_id, booking_id, method):  # Create a new roll in Payments with new Booking Payment info. Used when create a new booking
        table = db.execute("SELECT bookings.price, bookings.guest_id, guests.card_id FROM bookings "
                           "INNER JOIN guests ON bookings.guest_id = guests.id "
                           "WHERE bookings.id = ?", booking_id)
        table = table[0]
        card_id = table["card_id"]
        last_amount = table["price"]
        guest_id = table["guest_id"]
        db.execute("INSERT INTO payments(booking_id, company_id, guest_id, card_id, last_amount, method) "
                   "VALUES(?, ?, ?, ?, ?, ?);", booking_id, company_id, guest_id, card_id, last_amount, method)
        payment_id = db.execute("SELECT id FROM payments "
                                "WHERE booking_id = ? AND company_id = ?;", booking_id, company_id)
        payment_id = payment_id[0]['id']
        return payment_id  # Return the new payment ID


class Property:  # A Class to manage Properties in Database
    def __init__(self, property_id):  # if initialized will just have id of property
        self.id = property_id
        return

    def get_name(self):  # Get the name of property and return the string name
        name = db.execute("SELECT name FROM properties WHERE id = ?;", self.id)
        name = name[0]['name']
        return name

    def load(self):  # Load property Details from DB and return the data as dict
        table = db.execute("SELECT * FROM properties WHERE id = ?;", self.id)
        table = table[0]
        return table

    def update(self, table):  # Save property info changes into the DB
        #  Check if information are correct and set the right var type to be updated
        table['beds'] = to_int(table['beds'])
        table['baths'] = to_float(table['baths'])
        table['lock_code'] = to_int(table['lock_code'])
        table['gate_code'] = to_int(table['gate_code'])
        table['extra_code'] = to_int(table['extra_code'])
        table['owner_id'] = to_int(table['owner_id'])
        table['company_id'] = to_int(table['company_id'])
        table['visible'] = to_int(table['visible'])
        db.execute(  # Execute Query to update the DB
            "UPDATE properties "
            "SET name = ?, beds = ?, baths = ?,"
            "address = ?, city = ?, state = ?, country = ?,"
            "lock_code = ?, gate_code = ?, extra_code = ?, "
            "wifi_name = ?, wifi_password = ?,"
            "airbnb_ical = ?, booking_ical = ?, homeaway_ical = ?,"
            "night_price = ?, clean_price = ?,"
            "owner_id = ?, company_id = ?, visible = ? "
            "WHERE id = ?;",
            table['name'], table['beds'], table['baths'],
            table['address'], table['city'], table['state'], table['country'],
            table['lock_code'], table['gate_code'], table['extra_code'],
            table['wifi_name'], table['wifi_password'],
            table['airbnb_ical'], table['booking_ical'], table['homeaway_ical'],
            table['night_price'], table['clean_price'],
            table['owner_id'], table['company_id'], table['visible'], int(self.id)
        )
        id = db.execute("SELECT id FROM properties "
                        "WHERE company_id = ? AND name = ?;",
                        table['company_id'], table['name']
                        )
        return id[0]['id']  # Return Property ID if everythings runs OK

    def add(table):  # Add a new property row into DB passing data in parameter and return the new property ID

        #  check if information is right and set the right type to be saved
        table['beds'] = to_int(table['beds'])
        table['baths'] = to_float(table['baths'])
        table['lock_code'] = to_int(table['lock_code'])
        table['gate_code'] = to_int(table['gate_code'])
        table['extra_code'] = to_int(table['extra_code'])
        table['night_price'] = to_float(table['night_price'])
        table['clean_price'] = to_float(table['clean_price'])
        table['extra_charges'] = to_float(table['extra_charges'])
        table['owner_id'] = to_int(table['owner_id'])
        table['company_id'] = to_int(table['company_id'])
        table['visible'] = to_int(table['visible'])

        db.execute(  # Execute the SQL query to create a new property
            "INSERT INTO properties("
            "name, beds, baths,"
            "address, city, state, country,"
            "lock_code, gate_code, extra_code, "
            "wifi_name, wifi_password,"
            "airbnb_ical, booking_ical, homeaway_ical,"
            "night_price, clean_price, extra_charges,"
            "owner_id, company_id, visible)"
            "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            table['name'], table['beds'], table['baths'],
            table['address'], table['city'], table['state'], table['country'],
            table['lock_code'], table['gate_code'], table['extra_code'],
            table['wifi_name'], table['wifi_password'],
            table['airbnb_ical'], table['booking_ical'], table['homeaway_ical'],
            table['night_price'], table['clean_price'], table['extra_charges'],
            table['owner_id'], table['company_id'], table['visible']
        )

        # Get the new property ID
        id = db.execute("SELECT id FROM properties "
                        "WHERE company_id = ? AND name = ? "
                        "AND address = ? LIMIT 1;",
                        table['company_id'], table['name'], table['address']
                        )
        return id[0]['id']  # Return the new property ID


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default