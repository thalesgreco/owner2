CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    hash VARCHAR(80) NOT NULL,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(15),
    company_id INTEGER NOT NULL,
    admin INTEGER NOT NULL
);

CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(250) NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(4) NOT NULL,
    country VARCHAR(150),
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    site VARCHAR(150)
);

CREATE TABLE properties (
    id INTEGER PRIMARY KEY,
    name VARCHAR(150),
    beds INTEGER NOT NULL,
    baths FLOAT NOT NULL,
    text MEDIUMTEXT,
    address VARCHAR(250) NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(4) NOT NULL,
    country VARCHAR(150),
    lock_code INTEGER,
    gate_code INTEGER,
    extra_code INTEGER,
    wifi_name VARCHAR(100),
    wifi_password VARCHAR(100),
    airbnb VARCHAR(250),
    airbnb_ical VARCHAR(250),
    booking_ical VARCHAR(250),
    homeaway_ical VARCHAR(250),
    night_price FLOAT DEFAULT 0.0,
    clean_price FLOAT DEFAULT 0.0,
    extra_charges FLOAT DEFAULT 0.0,
    owner_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    visible BOOLEAN DEFAULT 1,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE owners (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(15) NOT NULL
);

CREATE TABLE guests (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    birth DATE NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    vip BOOL NOT NULL,
    card_id INTEGER
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    guest_id INTEGER NOT NULL,
    checkin DATE NOT NULL,
    checkout DATE NOT NULL,
    night_price FLOAT DEFAULT 0.0,
    clean_price FLOAT DEFAULT 0.0,
    extra_charges FLOAT DEFAULT 0.0,
    price FLOAT DEFAULT 0.0,
    paid BOOLEAN DEFAULT 0,
    lock_code INTEGER,
    gate_code INTEGER,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE cards (
    id INTEGER PRIMARY KEY,
    cc_number DOUBLE(18, 0) NOT NULL,
    cc_code INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    address VARCHAR(250) NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(4) NOT NULL,
    zip_code DOUBLE(10, 0) NOT NULL,
    country VARCHAR(150),
    phone VARCHAR(15) NOT NULL
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    card_id INTEGER DEFAULT 0,
    guest_id INTEGER NOT NULL,
    booking_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    cat_id INTEGER DEFAULT 0,
    last_amount FLOAT DEFAULT 0.0,
    amount_paid FLOAT DEFAULT 0.0,
    payday DATE DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(40) DEFAULT "Card",
    active BOOLEAN DEFAULT 1
);

CREATE INDEX users_x ON users(id, company_id);
CREATE INDEX companies_x ON companies(id);
CREATE INDEX properties_x ON properties(id, owner_id, company_id);
CREATE INDEX owners_x ON owners(id);
CREATE INDEX guests_x ON guests(id, card_id);
CREATE INDEX bookings_x ON bookings(id, user_id, property_id, guest_id);
CREATE INDEX cards_x ON cards(id);
CREATE INDEX payments_X ON payments(id, card_id, booking_id, company_id, cat_id);