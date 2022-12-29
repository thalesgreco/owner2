from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from classes import *
from datetime import datetime

# Configure application
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pms.db")

# Custom filter
app.jinja_env.filters["usd"] = usd


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Homepage that shows Check-in/Check-outs today

@app.route("/")
@login_required
def index():
    """Show Dashboard"""
    user_id = session['user_id']
    today = datetime.now().date()  # Get today date

    # Get Bookings that Checkin today
    bookings_checkin = db.execute("SELECT bookings.id, bookings.active, bookings.property_id, "
                                  "properties.name, guests.first_name, "
                                  "bookings.lock_code, bookings.checkin, bookings.checkout, "
                                  "bookings.price, bookings.paid, "
                                  "users.first_name AS user_name, payments.id AS payment_id "
                                  "FROM bookings INNER JOIN properties "
                                  "ON bookings.property_id = properties.id "
                                  "INNER JOIN guests ON bookings.guest_id = guests.id "
                                  "INNER JOIN users ON bookings.user_id = users.id "
                                  "INNER JOIN payments ON payments.booking_id = bookings.id "
                                  "WHERE bookings.user_id = ? "
                                  "AND bookings.checkin = ?;", user_id, today)

    # Get Bookings that Checkin today
    bookings_checkout = db.execute("SELECT bookings.id, bookings.active, bookings.property_id, "
                                   "properties.name, guests.first_name, "
                                   "bookings.lock_code, bookings.checkin, bookings.checkout, "
                                   "bookings.price, bookings.paid, "
                                   "users.first_name AS user_name, payments.id AS payment_id "
                                   "FROM bookings INNER JOIN properties "
                                   "ON bookings.property_id = properties.id "
                                   "INNER JOIN guests ON bookings.guest_id = guests.id "
                                   "INNER JOIN users ON bookings.user_id = users.id "
                                   "INNER JOIN payments ON payments.booking_id = bookings.id "
                                   "WHERE bookings.user_id = ? "
                                   "AND bookings.checkout = ?;", user_id, today)
    return render_template("index.html", bookings_checkin=bookings_checkin, bookings_checkout=bookings_checkout)


@app.route("/finances")  # Overview of Payments showing Paid, Due and Cancelled Payments
@login_required
def finances_show():
    """Show FINANCES Dashboard"""
    rows = db.execute("SELECT * FROM payments WHERE company_id = ?;", session['company_id'])
    for row in range(0, len(rows)):
        rows[row]['due'] = rows[row]['last_amount'] - rows[row]['amount_paid']
    return render_template("finances.html", payments=rows)


@app.route("/finances/payments", methods=["GET", "POST"])  # Route to edit payments
@login_required
def payments_edit():
    """Show Dashboard"""
    user_company = session['company_id']

    payments = db.execute("SELECT guests.first_name, guests.last_name, guests.birth,"
                          "guests.email, guests.phone,"
                          "payments.id, payments.last_amount, payments.amount_paid, payments.method "
                          "FROM payments INNER JOIN bookings ON bookings.id = payments.booking_id "
                          "INNER JOIN guests ON guests.id = bookings.guest_id "
                          "WHERE payments.company_id = ?;", user_company)
    print("[LOG] [EDIT] Payments Access by " + session['username'])
    return render_template("edit_payment.html", payments=payments)


@app.route("/api/payments/edit", methods=["POST", "GET"])  # API Endpoint for Payments modifications
@login_required
def api_editing_payment():
    if request.method == "GET" and "id" in request.args:  # Get Property info in JSON format
        pay = request.args.get("id")
        try:
            pay = int(pay)
            details = Payment(pay)
            details = details.load()
            if pay > 0:
                pay = [details]
                return jsonify(pay)
        except:
            pay = {}
    else:
        pay = {}

    if request.method == 'POST':  # Update Payment info
        dict = {}
        payment_id = int(request.form.get("id"))
        dict['id'] = payment_id
        dict['method'] = request.form.get("method")
        dict['amount_paid'] = to_float(request.form.get("amount_paid"))
        dict['last_amount'] = to_float(request.form.get("last_amount"))
        payment = Payment(payment_id)  # Load basic information and permissions for the payment
        pay = payment.load()
        if payment_id > 0 and session['company_id'] == pay['company_id']:  # Verify if user have permission to edit this payment
            payment.update(dict)  # update payment
            if dict['amount_paid'] >= dict['last_amount']:  # verify if the whole amount was paid and set Booking as paid or no
                payment.paid(1)
            else:
                payment.paid(0)
    return redirect("/finances")


@app.route("/bookings")  # Overview of User Bookings with action buttons
@login_required
def bookings_show():
    """Show Dashboard"""
    user_id = session['user_id']
    bookings_rows = db.execute("SELECT bookings.id, bookings.active, bookings.property_id, "
                               "properties.name, guests.first_name, "
                               "bookings.lock_code, bookings.checkin, bookings.checkout, "
                               "bookings.price, bookings.paid, "
                               "users.first_name AS user_name, payments.id AS payment_id "
                               "FROM bookings INNER JOIN properties "
                               "ON bookings.property_id = properties.id "
                               "INNER JOIN guests ON bookings.guest_id = guests.id "
                               "INNER JOIN users ON bookings.user_id = users.id "
                               "INNER JOIN payments ON payments.booking_id = bookings.id "
                               "WHERE bookings.user_id = ?", user_id)
    return render_template("bookings.html", bookings=bookings_rows)


@app.route("/bookings/edit", methods=["GET", "POST"])  # Manage and Edit bookings details, prices, guest details and cancel
@login_required
def bookings_edit():
    """Show Dashboard"""
    user_id = session['user_id']
    rows = db.execute("SELECT bookings.id, properties.name, "
                      "guests.first_name, "
                      "bookings.lock_code, bookings.checkin, bookings.checkout, "
                      "bookings.price, bookings.paid, users.first_name AS user_name "
                      "FROM bookings INNER JOIN properties ON bookings.property_id = properties.id "
                      "INNER JOIN guests ON bookings.guest_id = guests.id "
                      "INNER JOIN users ON bookings.user_id = users.id "
                      "WHERE bookings.user_id = ?;", user_id)
    bookings = []
    for row in rows:
        booking_name = row['name']
        bookings.append([row['id'], booking_name])
    print("[LOG] [EDIT] Bookings Access by " + session['username'])
    return render_template("edit_booking.html", bookings=bookings)


@app.route("/bookings/add", methods=["GET", "POST"])  # Add New Booking Webpage
@login_required
def bookings_add():
    """Show Dashboard"""
    props = []
    for i in session['properties']:  # Load Properties available for the user
        try:
            prop = Property(i).get_name()
            props.append([i, prop])
        except:
            continue
    print("[LOG] [ADD] Bookings Access by " + session['username'])
    return render_template("add_booking.html", props=props)


@app.route("/api/bookings/edit", methods=["POST", "GET"])  # API Endpoint for Change and Get Bookings Info
@login_required
def api_edit_booking():
    if request.method == "GET" and "b" in request.args:  # Get Booking information in JSON
        b = request.args.get("b")
        try:
            b = int(b)
            booking = Booking(b)
            details = booking.load()
            if b > 0 and booking.company_id == session['company_id']:  # Check if user has permission to edit booking
                b = [details]
                return jsonify(b)
        except:
            b = {}
    else:
        b = {}

    if request.method == 'POST':
        # parse the form data
        update_data = request.get_json()
        # get the booking and check the user's permission to update it
        try:
            booking_id = int(update_data['b'])
            update_data['id'] = booking_id
            booking = Booking(booking_id)

            if booking_id > 0 and session['user_id'] == booking.user_id:
                update_data['user_id'] = session['user_id']
                # update the booking
                response = Booking.update(booking_id, update_data)
                return response
            else:
                return jsonify({'status': 'denied'})
        except:
            return jsonify({'status': 'error'})

    if request.method == 'GET' and "cancel" in request.args:  # Cancel booking request
        b = request.args.get("cancel")
        try:
            b = int(b)
            booking = Booking(b)
            details = booking.load()
            if b > 0 and details['user_id'] == session['user_id']:
                db.execute("UPDATE payments "
                           "SET active = 0 "
                           "WHERE booking_id = ?;", b)
                db.execute("UPDATE bookings SET active = 0 WHERE id = ?;", b)
        except:
            print("[LOG] [BOOKING] ERROR CANCEL BOOKING")

    return redirect("/bookings")


@app.route("/api/bookings/add", methods=["POST"])  # API Endpoint to Add a Booking with POST method
@login_required
def api_add_booking():
    user_id = session['user_id']
    user_company = session['company_id']
    if request.method == 'POST':
        fields = [
            "checkin",
            "checkout",
            "night_price",
            "clean_price",
            "price",
            "extra_charges",
            "lock_code",
            "gate_code",
            "first_name",
            "last_name",
            "birth",
            "email",
            "phone",
            "vip"
        ]
        dict = {}
        #  New Booking
        dict['user_id'] = user_id
        dict['property_id'] = int(request.form.get("id"))
        dict['paid'] = 0
        dict['owner_id'] = 1
        dict['company_id'] = user_company
        dict['active'] = 1
        if dict['property_id'] not in session['properties']:
            return redirect("/properties/add")
        for field in fields:
            dict[field] = request.form.get(field)
        booking_id = Booking.add(dict)
        Payment.add(session['company_id'], booking_id, "Card")
    return redirect("/bookings")


@app.route("/properties")  # Overview of Properties for user company
@login_required
def properties_show():
    """Show Dashboard"""
    rows = db.execute("SELECT * FROM properties WHERE company_id = ?", session['company_id'])
    return render_template("properties.html", properties=rows)


@app.route("/properties/edit", methods=["GET", "POST"])  # Manage and Edit Properties Details
@login_required
def props_edit():
    props = []
    session['properties'] = Company.properties(session['company_id'])
    for i in session['properties']:
        try:
            prop = Property(i).get_name()
            props.append([i, prop])
        except:
            pass
    print("[LOG] [EDIT] Properties Access by " + session['username'])

    return render_template("edit_property.html", props=props)


@app.route("/properties/add", methods=["GET", "POST"])  # Webpage to Add a new property to Company's Properties
@login_required
def props_add():
    user_company = session['company_id']
    props = []
    session['properties'] = Company.properties(session['company_id'])
    for i in session['properties']:
        prop = Property(i).get_name()
        props.append([i, prop])
    print("[LOG] [ADD] Properties Access by " + session['username'])
    if "p" in request.args:
        p = request.args.get("p")
        try:
            p = int(p)
            details = Property(p)
            details = details.load()
            if p > 0 and details['company_id'] == user_company:
                p = [details]
                return jsonify(p)
        except:
            p = {}
    else:
        p = {}
    return render_template("add_property.html", props=props, p=p)


@app.route("/api/properties/add", methods=["POST"])  # API Endpoint to add a property to the system
@login_required
def api_add_property():
    id = session['user_id']
    user_company = session['company_id']
    if request.method == 'POST':
        fields = [
            "name",
            "beds",
            "baths",
            "address",
            "city",
            "state",
            "country",
            "lock_code",
            "gate_code",
            "extra_code",
            "wifi_name",
            "wifi_password",
            "airbnb_ical",
            "booking_ical",
            "homeaway_ical",
            "night_price",
            "clean_price",
            "extra_charges"
        ]
        dict = {}
        for field in fields:
            dict[field] = request.form.get(field)
        dict['owner_id'] = 1
        dict['company_id'] = user_company
        dict['visible'] = 1
        property_id = Property.add(dict)
        session['properties'].append(property_id)
    return redirect("/properties")


@app.route("/api/properties/edit", methods=["POST", "GET"])  # API Endpoint to manage and change informations of Properties
@login_required
def api_edit_property():
    id = session['user_id']
    user_company = session['company_id']
    if request.method == "GET" and "p" in request.args:  # Request to get Properties Information in JSON
        p = request.args.get("p")
        try:
            p = int(p)
            details = Property(p)
            details = details.load()
            if p > 0 and details['company_id'] == user_company:
                p = [details]
                return jsonify(p)
        except:
            p = {}
    else:
        p = {}

    if request.method == 'GET' and "delete" in request.args:  # Request to Delete a property
        p = request.args.get("delete")
        try:
            p = int(p)
            property = Property(p)
            details = property.load()
            if p > 0 and details['company_id'] == user_company:
                booking_ids = db.execute("SELECT id FROM bookings WHERE property_id = ?;", p)
                for booking_id in booking_ids:
                    db.execute("UPDATE payments "
                               "SET active = 0 "
                               "WHERE booking_id = ?;", booking_id['id'])
                db.execute("UPDATE bookings SET active = 0 WHERE property_id = ?;", p)
                db.execute("UPDATE properties "
                           "SET active = 0, visible = 0 "
                           "WHERE id = ?;", p)
        except:
            print("ERROR DELETE PROPERTY")

    if request.method == 'POST':  # Request to change Property Info
        fields = [
            "name",
            "beds",
            "baths",
            "address",
            "city",
            "state",
            "country",
            "lock_code",
            "gate_code",
            "extra_code",
            "wifi_name",
            "wifi_password",
            "airbnb_ical",
            "booking_ical",
            "homeaway_ical",
            "night_price",
            "clean_price"
        ]

        # Create an empty dict object
        dict = {}

        # Get the property ID from the form data
        property_id = int(request.form.get("id"))

        # Use a loop to iterate over the list of fields
        for field in fields:
            dict[field] = request.form.get(field)

        # Set the other information for the dict
        dict['owner_id'] = 1
        dict['company_id'] = user_company
        dict['visible'] = 1
        property = Property(property_id)
        property.update(dict)
    return redirect("/properties")


@app.route("/company/edit")  # Webpage to change Company Details
@login_required
def company_edit():
    """Show Dashboard"""
    company_details = Company(session['company_id'])
    company_details = company_details.load()
    print("[LOG] [EDIT] Company Access by " + session['username'])
    if session['admin'] >= 1:
        return render_template("company.html", company=company_details)
    return redirect('/')


@app.route("/api/company/edit", methods=['POST'])  # API Endpoint to change Company Information and return JSON Status
@login_required
def api_company_edit():
    """Show Dashboard"""
    if request.method == 'POST':  # Get JSON Request with information to modify
        data = request.get_json()
        if int(data['id']) == session['company_id']:
            response = Company.update(data['id'], data)
            return response
        else:
            return jsonify({'status': 'denied'})
    company_details = Company(session['company_id'])
    company_details = company_details.load()
    if session['admin'] >= 1:
        return render_template("company.html", company=company_details)
    return redirect('/')


@app.route("/login", methods=["GET", "POST"])  # Login Webpage and Sign In verification
def login():
    """Show Dashboard"""
 # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users "
                          "WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Create object for user logged
        logged = User(session['user_id'])
        session['username'] = logged.username
        session['first_name'] = logged.first_name
        session['last_name'] = logged.last_name
        session['company_id'] = logged.company
        session['admin'] = logged.admin
        session['properties'] = logged.properties
        print(session)
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])  # Register Webpage and SignUp form submit
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username") or not request.form.get("first_name") or not request.form.get("last_name"):
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("address") or not request.form.get("city") or not request.form.get("state") or not request.form.get("country"):
            return render_template("register.html")

        elif not request.form.get("password"):
            return render_template("register.html")

        elif not request.form.get("email"):
            return render_template("register.html")

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html")

        # Query database for username
        search_user = db.execute("SELECT * FROM users "
                                 "WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(search_user) != 0:
            return render_template("register.html")

        # Create new user in DB
        password = generate_password_hash(request.form.get("confirmation"))
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        company = request.form.get("company")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get("country")
        email = request.form.get("email")
        phone = request.form.get("phone")
        admin = 1

        db.execute(
            "INSERT INTO companies("
            "name, address, city, state, country, "
            "email, phone) "
            "VALUES(?, ?, ?, ?, ?, ?, ?)",
            company, address, city, state, country,
            email, phone
        )

        company_id = db.execute("SELECT id FROM companies "
                                "WHERE name IS ?", company)

        db.execute("INSERT INTO users("
                   "username, hash, "
                   "first_name, last_name, "
                   "email, phone, "
                   "company_id, admin) "
                   "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                   username, password,
                   first_name, last_name,
                   email, phone,
                   company_id[0]['id'], admin
                   )

        # Redirect user to home page
        return redirect("/login")

    return render_template("register.html")


@app.route("/account/password", methods=["GET", "POST"])  # Webpage to change the Account Password
@login_required
def password():
    """Change user password"""
    if request.method == "POST":
        # Ensure old password was submitted
        if not request.form.get("password"):
            return render_template("password.html")

        # Ensure new password and confirmation was submitted
        elif not request.form.get("newpassword") or not request.form.get("confirmation"):
            return render_template("password.html")

        rows = db.execute("SELECT hash FROM users WHERE id = ?", session['user_id'])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], request.form.get("password")):
            return render_template("password.html")

        elif request.form.get("newpassword") != request.form.get("confirmation"):
            return render_template("password.html")

        # Create new password for the user
        newpassword = generate_password_hash(request.form.get("confirmation"))
        db.execute("UPDATE users SET hash = ? WHERE id = ?", newpassword, session['user_id'])
        return redirect("/")
    return render_template("password.html")


@app.route("/logout")  # Route that Logout user session and redirect to the main page
def logout():
    """Log user out"""

    # Forget any user_id
    try:
        session.clear()
    except:
        session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/readme")
def readme():
    #url = app.send_static_file('README.md')
    return app.send_static_file('README.md')