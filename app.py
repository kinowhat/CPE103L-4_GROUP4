from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def connect_db():
    return sqlite3.connect("userDatabase.db")

def setup_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('user', 'user123', 'user')")
    cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, price REAL, qty INTEGER, image TEXT)")
    conn.commit()
    conn.close()

setup_db()  


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'role': user[0]}
    else:
        return {'role': None}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (email, password))
        conn.commit()
        conn.close()
        return {'message': 'Registered successfully!'}
    except sqlite3.IntegrityError:
        return {'message': 'Email already exists!'}
    
@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.get_json()
    name = data['name']
    price = data['price']
    qty = data['qty']
    image = data['image']
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, price, qty, image) VALUES (?, ?, ?, ?)", (name, price, qty, image))
        conn.commit()
        conn.close()
        return {'message': 'Registered successfully!'}
    except sqlite3.IntegrityError:
        return {'message': 'Item already exists!'}

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
            "image": row[4],
        })
    return jsonify({"items": items})



if __name__ == '__main__':
    app.run(debug=True)