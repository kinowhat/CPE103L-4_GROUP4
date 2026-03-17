from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from Item import Item
from Reservation import Reservation

app = Flask(__name__)
CORS(app)


# ==========================
# DATABASE CONNECTION
# ==========================
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


# ==========================
# PAGES
# ==========================
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin')
def admin_page():
    return render_template('admin.html')


@app.route('/user')
def user_page():
    return render_template('user.html')


# ==========================
# AUTH
# ==========================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (data['username'], data['email'])
    )

    if cursor.fetchone():
        conn.close()
        return jsonify({"message": "Username or email already exists"}), 400

    cursor.execute(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
        (data['username'], data['email'], data['password'], "student")
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Registration successful!"})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE username=? AND password=?",
        (data['username'], data['password'])
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"role": user[0]})

    return jsonify({"role": None})


# ==========================
# ITEM CRUD
# ==========================
@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.get_json()

    item = Item()
    item.setName(data['name'])
    item.setPrice(data['price'])
    item.setQuantity(data['qty'])

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO items (name, price, qty, image) VALUES (?, ?, ?, ?)",
        (item.getName(), item.getPrice(), item.getQuantity(), data['image'])
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Item added successfully!"})


@app.route('/get_items', methods=['GET'])
def get_items():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()

    items = []

    for row in rows:
        item = Item()
        item.setName(row[1])
        item.setPrice(row[2])
        item.setQuantity(row[3])

        items.append({
            "id": row[0],
            "name": item.getName(),
            "price": item.getPrice(),
            "qty": item.getQuantity(),
            "image": row[4],
            "low_stock": item.setLowStockFlag()
        })

    return jsonify({"items": items})


@app.route('/update_item', methods=['PUT'])
def update_item():
    data = request.get_json()

    item = Item()
    item.setName(data['name'])
    item.setPrice(data['price'])
    item.setQuantity(data['qty'])

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE items SET name=?, price=?, qty=?, image=? WHERE id=?",
        (item.getName(), item.getPrice(), item.getQuantity(), data['image'], data['id'])
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Item updated successfully!"})


@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Item deleted successfully!"})


# ==========================
# RESERVATION CRUD
# ==========================
@app.route('/add_reservation', methods=['POST'])
def add_reservation():
    data = request.get_json()

    reservation = Reservation()
    reservation.setUsername(data['username'])
    reservation.setItemId(data['item_id'])
    reservation.setQty(data['qty'])
    reservation.setPickupDate(data['pickup_date'])
    reservation.setStatus("pending")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT qty FROM items WHERE id=?", (reservation.getItemId(),))
    item = cursor.fetchone()

    if not item:
        conn.close()
        return jsonify({"message": "Item not found"}), 404

    if item[0] < reservation.getQty():
        conn.close()
        return jsonify({"message": "Not enough stock"}), 400

    cursor.execute(
        "UPDATE items SET qty = qty - ? WHERE id=?",
        (reservation.getQty(), reservation.getItemId())
    )

    cursor.execute(
        "INSERT INTO reservations (username, item_id, qty, pickup_date, status) VALUES (?, ?, ?, ?, ?)",
        (
            reservation.getUsername(),
            reservation.getItemId(),
            reservation.getQty(),
            reservation.getPickupDate(),
            reservation.getStatus()
        )
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
    """, (username,))

    rows = cursor.fetchall()
    conn.close()

    reservations = []

    for row in rows:
        reservation = Reservation()
        reservation.setUsername(row[1])
        reservation.setItemId(row[2])
        reservation.setQty(row[3])
        reservation.setPickupDate(row[4])
        reservation.setStatus(row[5])

        reservations.append({
            "id": row[0],
            "username": reservation.getUsername(),
            "item_id": reservation.getItemId(),
            "qty": reservation.getQty(),
            "pickup_date": reservation.getPickupDate(),
            "status": reservation.getStatus(),
            "item_name": row[6]
        })

    return jsonify({"reservations": reservations})


@app.route('/update_reservation/<int:res_id>', methods=['PUT'])
def update_reservation(res_id):
    data = request.get_json()

    reservation = Reservation()
    reservation.setStatus(data['status'])

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE reservations SET status=? WHERE id=?",
        (reservation.getStatus(), res_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Reservation updated!"})


@app.route('/delete_reservation/<int:res_id>', methods=['DELETE'])
def delete_reservation(res_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM reservations WHERE id=?", (res_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Reservation deleted!"})

@app.route('/get_all_reservations', methods=['GET'])
def get_all_reservations():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reservations.id, reservations.username, reservations.item_id,
               reservations.qty, reservations.pickup_date, reservations.status, items.name
        FROM reservations
        JOIN items ON reservations.item_id = items.id
        ORDER BY reservations.pickup_date ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    reservations = []

    for row in rows:
        reservation = Reservation()
        reservation.setUsername(row[1])
        reservation.setItemId(row[2])
        reservation.setQty(row[3])
        reservation.setPickupDate(row[4])
        reservation.setStatus(row[5])

        reservations.append({
            "id": row[0],
            "username": reservation.getUsername(),
            "item_id": reservation.getItemId(),
            "qty": reservation.getQty(),
            "pickup_date": reservation.getPickupDate(),
            "status": reservation.getStatus(),
            "item_name": row[6]
        })

    return jsonify({"reservations": reservations})

# ==========================
# RUN APP
# ==========================
if __name__ == '__main__':
    app.run(debug=True)
