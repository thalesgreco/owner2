
# Owner2 - Vacation Rental Booking Manager
Owner2 - Vacation Rental Booking Manager is part of the Final Project of Harvard CS50x 2022.
## Video Demo: https://www.youtube.com/watch?v=We_-kKJ5QPE
## Description
A web application built with Flask and SQLite3 that allows users and companies to manager Vacation Properties, Bookings/Reservations, Guests and Payments.
The web app routes are using API requests and JavaScript to deal with data. Providing integration with 3rd-Party Apps.

In the web application you can Add/Edit Properties, Bookings and Manage Payments.

## Requirements
1. Python 3.11
2. SQLite3
3. requirements.txt

## Installation
1. Clone this repository
2. Install the dependencies: pip install -r requirements.txt
3. Run the development server: flask run

## Files
### app.py
Contains all the urls routes and the control of API Requests/Responses.

### classes.py
Contains the Classes that deals with the Database Data like create, update and get the data.
Also includes some extra functions like to_int, to_float, usd and login_required.

### pms.sql
Contains the instruction queries to create a database that communicates with the Web App.

### pms.db
Already built blank database using the pms.sql and SQLite3.

### requirements.txt
Requirements file with necessary libraries to run the Web App.

### templates/layout.html
Basic template used for Login and Register Page without the Manager Navigator.

### templates/layout2.html
Layout for the Manager Webpages.

### templates/index.html
Shows the Bookings that will Check-in and Check-out Today in 2 tables.

### templates/login.html
Basic template with login form that sends a post request to sign in.

### templates/register.html
Basic template with a register form with Company and User informations to be send as POST.

### templates/properties.html
Shows an overview of the properties data added to the user's Company in a table with extra tools.

### templates/add_property.html
Template with a post form to insert a new property details into the database.
Includes some javascript to copy an already added property info and populates the form fields.

### templates/edit_property.html
Template with a POST form to change Properties Details, Amounts and to Delete/Hide property as well.
Includes some javascript to Insert selected property data into form fields.

### templates/bookings.html
Shows an overview of the bookings data added to the user's Company in a table with extra tools and shortcuts.

### templates/add_booking.html
Template with a post form to insert a new booking, guest and payment into the database.
Includes some javascript to copy booking property info and populates the form fields.
Also includes some JS to calculate Total Amount Price based in the check-in/check-out dates and the prices.

### templates/edit_booking.html
Template with a POST form to change booking details, guest details, amounts and to cancel booking as well.
Includes some javascript to Insert selected booking data into form fields.
Also includes some JS to calculate Total Amount Price based in the check-in/check-out dates and the prices.

### templates/finances.html
Shows an overview of the Booking's Payments like total amount, amount paid, amount due and status of payment.
Includes shortcut to edit booking and payment pages.
Also includes some JS to calculate the amount paid, due and total of all payments.

### templates/edit_payment.html
Template with a POST form to change Payment paid amount and payment method and to see Payer/Guest Details.
Includes some javascript to Insert selected payment data into form fields and to calculate amount due based on paid amount.

### templates/company.html
Basic template with a POST form to see and edit Company information. Contains JS to submit form as JSON and shows a message to user.

### templates/password.html
Basic template with a POST form to change password providing old password, new password and confirm new passowrd.

### static/styles.css
Contains the CSS for the layout.html and for the Lateral Navigator Menu.

### static/favicon.ico
A basic icon for the website.

## Usage
### First Steps
1. Navigate to the homepage (e.g. http://127.0.0.1:5000/) and click in "Register" to create a new account.
2. After successfully created a new account it will show the Login Page and you can Sign In with the new account.
### Homepage
The Homepage will show the Check-in and Check-out bookings for today when they are available.
### Add Property
Go to "Properties > Add Property" and add a new property to manage bookings.
### Add Booking
Go to "Bookings > Add Booking" to add a new Booking, Guest and Payment for a Added Property.
### Edit Payments
Go to "Payments > Edit Payments" to manage Amount Paid and Payment Method.
### Bookings, Properties and Payments Overview
You can see an Overview and Action Buttons of Properties, Bookings and Payments as well using the navigator on the side.
### Edit Booking
Go to "Bookings > Edit Bookings" to edit booking details, booking prices and to cancel a booking.
### Edit Properties
Go to "Properties > Edit Properties" to edit property details, property prices and to Disable a property.
### Edit Company Details
Go to "Company > Edit Company" to edit company details like name, address and contact information.
### Change Account Password
Go to "Change Password" to change the account password.
### Logout
You can logout clicking in "Logout" on the bottom of any page.


## Contact
Feel free to get in touch with me at thalesgreco@gmail.com if you have any questions or feedback.

## Link References

1. Harvard CS50x - https://cs50.harvard.edu/x/2022/
2. W3 Schools - https://www.w3schools.org/
3. StackOverFlow - https://www.stackoverflow.com/
4. FontAwesome - https://www.fontawesome.com/
5. Bootstrap CSS/JS - https://www.getbootstrap.com/
6. Bootstrap Sidebar Doc - https://bootstrapious.com/p/bootstrap-sidebar