from datetime import date

class ReservationList:
    def __init__(self):
        self.reservation = None

    def reservationList(self, userName: str, productName: str, productQuantity: int, date: str):
        reservation = {"Name": userName, "Product": productName, "Qty": productQuantity, "Date": date}
        self.reservation = reservation

    def __str__(self):
        return f"Name = {self.reservation['Name']}\nProduct = {self.reservation['Product']}\nQty = {self.reservation['Qty']}\nDate = {self.reservation['Date']}"

store = ReservationList()
name = input("Enter name: ")
product = input("Enter product: ")
qty = int(input("Enter quantity: "))


today = date.today().strftime("%Y-%m-%d")

store.reservationList(name, product, qty, today)

print("\n--- Reservation Details ---")
print(store)
