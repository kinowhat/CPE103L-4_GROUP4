class ReservationSystem:
    def __init__(self):
        self.reservation = None

    def reservationList(self, userName: str, productName: str, productQuantity: int, date: str):
        reservation = {"Name": userName, "Product": productName, "Qty": productQuantity, "Date": date}
        self.reservation = reservation

    def __str__(self):
        return f"Name = {self.reservation['Name']}\nProduct = {self.reservation['Product']}\nQty = {self.reservation['Qty']}\nDate = {self.reservation['Date']}"


store = ReservationSystem()
name = input("Enter name: ")
product = input("Enter product: ")
qty = int(input("Enter quantity: "))
date = input("Enter date: ")
store.reservationList(name, product, qty, date)
print(store)