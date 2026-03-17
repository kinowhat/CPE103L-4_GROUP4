from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import re
import os

app = Flask(__name__)
CORS(app)

# ==========================
# DATABASE PATH
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "userDatabase.db")
print("FINAL DB PATH:", DB_PATH)


def connect_db():
    print("USING DB:", DB_PATH)
    return sqlite3.connect(DB_PATH)


# ==========================
# USER VALIDATOR
# ==========================
class UserValidator:
    def __init__(self):
        self.email_pattern = r'^[a-zA-Z0-9._%+-]+@mymail\.mapua\.edu\.ph$'
        self.password_pattern = r'^.{8,}$'

    def validate_email(self, email):
        return re.match(self.email_pattern, email)

    def validate_password(self, password):
        return re.match(self.password_pattern, password)


validator = UserValidator()


# ==========================
# SETUP DB
# ==========================
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

    try:
        cursor.execute("ALTER TABLE items ADD COLUMN image TEXT")
    except sqlite3.OperationalError:
        pass

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

    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, email, password, role)
        VALUES (1, 'admin', 'admin@mymail.mapua.edu.ph', 'is_admin', 'admin')
    """)

    cursor.execute("UPDATE users SET role='student' WHERE role='user'")

    conn.commit()
    conn.close()


setup_db()


# ==========================
# DEBUG ROUTES
# ==========================
@app.route('/debug_users')
def debug_users():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()

    conn.close()
    return jsonify({"users": users})


@app.route('/debug_reservations')
def debug_reservations():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reservations ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return jsonify({"reservations": rows})


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

    username = data['username']
    email = data['email']
    password = data['password']

    if not validator.validate_email(email):
        return jsonify({"message": "Invalid Mapua email format"}), 400

    if not validator.validate_password(password):
        return jsonify({"message": "Password must be at least 8 characters"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (username, email)
    )

    if cursor.fetchone():
        conn.close()
        return jsonify({"message": "Username or email already exists"}), 400

    cursor.execute(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
        (username, email, password, "student")
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Registration successful!"})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data['username']
    password = data['password']

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, role, email, password FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"role": None, "message": "User not found"}), 401

    db_username, db_role, db_email, db_password = user

    if db_role == "admin":
        if username == "admin" and password == db_password:
            return jsonify({
                "role": db_role,
                "username": db_username,
                "email": db_email
            })
        return jsonify({"role": None, "message": "Incorrect admin credentials"}), 401

    if password == db_password:
        return jsonify({
            "role": db_role,
            "username": db_username,
            "email": db_email
        })

    return jsonify({"role": None, "message": "Incorrect credentials"}), 401


# ==========================
# ITEM CRUD
# ==========================
@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.get_json()

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO items (name, price, qty, image) VALUES (?, ?, ?, ?)",
            (
                data['name'],
                float(data['price']),
                int(data['qty']),
                data['image']
            )
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Item added successfully!"})

    except Exception as e:
        print("ERROR IN /add_item:", e)
        return jsonify({"message": "Failed to add item"}), 500


@app.route('/get_items', methods=['GET'])
def get_items():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "qty": row[3],
            "image": row[4]
        })

    return jsonify({"items": items})


@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Item deleted successfully!"})

@app.route('/update_item', methods=['PUT'])
def update_item():
    data = request.get_json()

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE items
            SET name=?, price=?, qty=?, image=?
            WHERE id=?
            """,
            (
                data['name'],
                float(data['price']),
                int(data['qty']),
                data['image'],
                int(data['id'])
            )
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Item updated successfully!"})

    except Exception as e:
        print("ERROR IN /update_item:", e)
        return jsonify({"message": "Failed to update item"}), 500

# ==========================
# RESERVATION CRUD
# ==========================
@app.route('/add_reservation', methods=['POST'])
def add_reservation():
    data = request.get_json()

    try:
        username = data['username']
        item_id = int(data['item_id'])
        qty = int(data['qty'])
        pickup_date = data['pickup_date']
        status = "pending"

        conn = connect_db()
        cursor = conn.cursor()

        print("ADD RESERVATION DATA:", data)

        cursor.execute("SELECT qty FROM items WHERE id=?", (item_id,))
        item = cursor.fetchone()

        if not item:
            conn.close()
            return jsonify({"message": "Item not found"}), 404

        current_stock = item[0]

        if current_stock < qty:
            conn.close()
            return jsonify({"message": "Not enough stock"}), 400

        cursor.execute(
            "UPDATE items SET qty = qty - ? WHERE id=?",
            (qty, item_id)
        )

        cursor.execute(
            "INSERT INTO reservations (username, item_id, qty, pickup_date, status) VALUES (?, ?, ?, ?, ?)",
            (username, item_id, qty, pickup_date, status)
        )

        print("NEW RESERVATION ID:", cursor.lastrowid)

        conn.commit()
        conn.close()

        return jsonify({"message": "Reservation added successfully!"})

    except Exception as e:
        print("ERROR IN /add_reservation:", e)
        return jsonify({"message": "Failed to add reservation."}), 500


@app.route('/get_reservations/<username>', methods=['GET'])
def get_reservations(username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reservations.id,
               reservations.username,
               reservations.item_id,
               reservations.qty,
               reservations.pickup_date,
               reservations.status,
               items.name
        FROM reservations
        JOIN items ON reservations.item_id = items.id
        WHERE reservations.username = ?
        ORDER BY reservations.id DESC
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


@app.route('/get_all_reservations', methods=['GET'])
def get_all_reservations():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reservations.id,
               reservations.username,
               users.email,
               reservations.item_id,
               reservations.qty,
               reservations.pickup_date,
               reservations.status,
               items.name
        FROM reservations
        JOIN items ON reservations.item_id = items.id
        JOIN users ON reservations.username = users.username
        ORDER BY reservations.id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    reservations = []
    for row in rows:
        reservations.append({
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "item_id": row[3],
            "qty": row[4],
            "pickup_date": row[5],
            "status": row[6],
            "item_name": row[7]
        })

    return jsonify({"reservations": reservations})


@app.route('/update_reservation/<int:res_id>', methods=['PUT'])
def update_reservation(res_id):
    data = request.get_json()

    try:
        status = data['status']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE reservations SET status=? WHERE id=?",
            (status, res_id)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Reservation updated!"})

    except Exception as e:
        print("ERROR IN /update_reservation:", e)
        return jsonify({"message": "Failed to update reservation"}), 500


@app.route('/delete_reservation/<int:res_id>', methods=['DELETE'])
def delete_reservation(res_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM reservations WHERE id=?", (res_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Reservation deleted!"})

@app.route('/debug_items')
def debug_items():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, price, qty FROM items")
    rows = cursor.fetchall()

    conn.close()
    return jsonify({"items": rows})

# ==========================
# RUN APP
# ==========================
if __name__ == '__main__':
    app.run(debug=True)
