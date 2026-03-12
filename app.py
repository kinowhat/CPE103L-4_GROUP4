from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from Item import Item
from Reservation import Reservation




app = Flask(__name__)
CORS(app)

LOW_STOCK_THRESHOLD = 5   # add this

def connect_db():
    return sqlite3.connect("userDatabase.db")

def setup_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            qty INTEGER,
            image TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            username TEXT,
            item_id INTEGER,
            qty INTEGER,
            pickup_date TEXT,
            status TEXT
        )
    """)


    cursor.execute(
        "INSERT OR IGNORE INTO users (username, email, password, role) VALUES ('admin', 'admin@gmail.com', 'admin123', 'admin')"
    )
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, email, password, role) VALUES ('user', 'user@gmail.com', 'user123', 'user')"
    )


    conn.commit()
    conn.close()

setup_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data['username']
    email = data['email']
    password = data['password']

    conn = connect_db()
    cursor = conn.cursor()

    # Check if username or email already exists
    cursor.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (username, email)
    )
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return jsonify({"message": "Username or email already exists"}), 400

    # Automatically assign role = student
    cursor.execute(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
        (username, email, password, "student")
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Registration successful!"})


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/user')
def user_page():
    return render_template('user.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'role': user[0]})
    return jsonify({'role': None})

@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.get_json()
    name = data['name']
    price = data['price']
    qty = data['qty']
    image = data['image']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (name, price, qty, image) VALUES (?, ?, ?, ?)",
        (name, price, qty, image)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Item added successfully!'})

@app.route('/get_items', methods=['GET'])
def get_items():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE qty > 0")
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        item_obj = Item(row[1], row[3], row[2])

        items.append({
            "id": row[0],
            "name": item_obj.getName(),
            "price": item_obj.getPrice(),
            "qty": item_obj.getQuantity(),
            "image": row[4],
            "low_stock": item_obj.setLowStockFlag()
        })

    return jsonify({"items": items})

@app.route('/update_item', methods=['PUT'])
def update_item():
    data = request.get_json()
    item_id = data['id']
    name = data['name']
    price = data['price']
    qty = data['qty']
    image = data['image']

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE items SET name=?, price=?, qty=?, image=? WHERE id=?",
        (name, price, qty, image, item_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": f"Item {item_id} updated successfully!"})

@app.route('/add_reservation', methods=['POST'])
def add_reservation():
    data = request.get_json()           
    username = data['username']
    item_id = data['item_id']
    qty = data['qty']
    pickup_date = data['pickup_date']
    reservation = Reservation(username, item_id, qty, pickup_date)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reservations (username, item_id, qty, pickup_date, status) VALUES (?, ?, ?, ?, ?)",
        (username, item_id, qty, pickup_date, "pending")
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Reservation added successfully!"})

@app.route('/get_reservations/<username>', methods=['GET'])
def get_reservations(username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reservations.id, reservations.username, reservations.item_id,
               reservations.qty, reservations.pickup_date, reservations.status, items.name
        FROM reservations
        JOIN items ON reservations.item_id = items.id
        WHERE reservations.username = ?
          AND reservations.status IN ('pending', 'approved')
        ORDER BY reservations.pickup_date ASC
    """, (username,))

    rows = cursor.fetchall()
    conn.close()

    reservations = []
    for row in rows:
        reservations.append({
            "id": row[0],
            "username": row[1],
            "item_id": row[2],
            "qty": row[3],
            "pickup_date": row[4],
            "status": row[5],
            "item_name": row[6]
        })

    return jsonify({"reservations": reservations})

    
if __name__ == '__main__':
    app.run(debug=True)

