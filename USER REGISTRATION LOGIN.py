import re

class UserValidator:
    def __init__(self):
        self.username_pattern = r'^[a-zA-Z][a-zA-Z]+@mymail\.mapua\.edu\.ph$'
        self.password_pattern = r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\d{10}$'

    def validate_username(self, username):
        return re.match(self.username_pattern, username)

    def validate_password(self, password):
        return re.match(self.password_pattern, password)


class UserDatabase:
    def __init__(self):
        self.users = {
            "admin@mymail.mapua.edu.ph": "is_admin"
        }

    def register_user(self, username, password):
        if username in self.users:
            print("User already exists.")
        else:
            self.users[username] = password
            print("User registered successfully.")

    def check_credentials(self, username, password):
        return username in self.users and self.users[username] == password

    def is_admin(self, username):
        return username == "admin@mymail.mapua.edu.ph"
        
class ReservationDatabase:
    def __init__(self):
        self.reservations = []

    def add_reservation(self, username, item, quantity):
        reservation = {
            "username": username,
            "item": item,
            "quantity": quantity
        }
        self.reservations.append(reservation)

    def view_user_reservations(self, username):
        found = False
        print("\n=== YOUR RESERVATION HISTORY ===")
        
        for r in self.reservations:
            if r["username"] == username:
                print(f"Item: {r['item']} | Quantity: {r['quantity']}")
                found = True

        if not found:
            print("No reservations found.")
            
class LoginSystem:
    def __init__(self):
        self.validator = UserValidator()
        self.database = UserDatabase()
        self.reservation_db = ReservationDatabase()
        
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

if __name__ == "__main__":
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