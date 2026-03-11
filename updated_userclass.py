import re
import sqlite3


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("mapua_bookstore.db")
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                username
                                TEXT
                                UNIQUE,
                                password
                                TEXT
                            )
                            """)

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS reservations
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                username
                                TEXT,
                                item
                                TEXT,
                                quantity
                                INTEGER
                            )
                            """)

        self.cursor.execute("""
                            INSERT
                            OR IGNORE INTO users(username,password)
        VALUES('admin@mymail.mapua.edu.ph','is_admin')
                            """)

        self.conn.commit()


class UserValidator:
    def __init__(self):
        self.username_pattern = r'^[a-zA-Z][a-zA-Z]+@mymail\.mapua\.edu\.ph$'
        self.password_pattern = r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\d{10}$'

    def validate_username(self, username):
        return re.match(self.username_pattern, username)

    def validate_password(self, password):
        return re.match(self.password_pattern, password)


class UserDatabase:
    def __init__(self, db):
        self.db = db

    def register_user(self, username, password):
        try:
            self.db.cursor.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (username, password)
            )
            self.db.conn.commit()
            print("User registered successfully.")
        except sqlite3.IntegrityError:
            print("User already exists.")

    def check_credentials(self, username, password):
        self.db.cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        return self.db.cursor.fetchone() is not None

    def is_admin(self, username):
        return username == "admin@mymail.mapua.edu.ph"


class ReservationDatabase:
    def __init__(self, db):
        self.db = db

    def add_reservation(self, username, item, quantity):

        self.db.cursor.execute(
            "INSERT INTO reservations(username,item,quantity) VALUES (?,?,?)",
            (username, item, quantity)
        )

        self.db.conn.commit()

    def view_user_reservations(self, username):

        self.db.cursor.execute(
            "SELECT item, quantity FROM reservations WHERE username=?",
            (username,)
        )

        reservations = self.db.cursor.fetchall()

        print("\n=== YOUR RESERVATION HISTORY ===")

        if reservations:
            for r in reservations:
                print(f"Item: {r[0]} | Quantity: {r[1]}")
        else:
            print("No reservations found.")


class LoginSystem:
    def __init__(self):

        self.validator = UserValidator()

        self.db_manager = DatabaseManager()

        self.database = UserDatabase(self.db_manager)

        self.reservation_db = ReservationDatabase(self.db_manager)

    def register(self):

        print("\n=== MAPUA BOOKSTORE REGISTRATION SYSTEM ===")

        username = input("Enter new username: ")
        password = input("Enter new password: ")

        if not self.validator.validate_username(username):
            print("Invalid username format.")

        elif not self.validator.validate_password(password):
            print("Invalid password format.")

        else:
            self.database.register_user(username, password)

    def make_reservation(self, username):

        print("\n=== MAKE RESERVATION ===")

        item = input("Enter item name: ")
        quantity = input("Enter quantity: ")

        self.reservation_db.add_reservation(username, item, quantity)

        print("Reservation successful.")

    def login(self):

        print("\n=== MAPUA BOOKSTORE LOGIN SYSTEM ===")

        username = input("Enter username: ")
        password = input("Enter password: ")

        if not self.validator.validate_username(username):
            print("Invalid username or password format.")

        elif not self.validator.validate_password(password):
            print("Invalid password or password format.")

        elif self.database.check_credentials(username, password):

            print("Login successful!")

            while True:

                print("\n=== USER MENU ===")
                print("1 - Make Reservation")
                print("2 - View Reservation History")
                print("3 - Logout")

                choice = input("Choose option: ")

                if choice == "1":
                    self.make_reservation(username)

                elif choice == "2":
                    self.reservation_db.view_user_reservations(username)

                elif choice == "3":
                    print("Logging out...")
                    break

                else:
                    print("Invalid choice.")

        else:
            print("Incorrect credentials.")


if _name_ == "_main_":

    system = LoginSystem()

    while True:

        print("\n=== MAPUA BOOKSTORE ===")
        print("1 - Register")
        print("2 - Login")
        print("3 - Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            system.register()

        elif choice == "2":
            system.login()

        elif choice == "3":
            print("Exiting system...")
            break

        else:
            print("Invalid choice. Please try again.")
