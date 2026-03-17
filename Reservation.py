class Reservation:
    def __init__(self, username="", item_id=0, qty=0, pickup_date="", status="pending"):
        self.username = username
        self.item_id = item_id
        self.qty = qty
        self.pickup_date = pickup_date
        self.status = status

    # GETTERS
    def getUsername(self):
        return self.username

    def getItemId(self):
        return self.item_id

    def getQty(self):
        return self.qty

    def getPickupDate(self):
        return self.pickup_date

    def getStatus(self):
        return self.status

    # SETTERS
    def setUsername(self, username):
        self.username = username

    def setItemId(self, item_id):
        self.item_id = item_id

    def setQty(self, qty):
        self.qty = int(qty)

    def setPickupDate(self, pickup_date):
        self.pickup_date = pickup_date

    def setStatus(self, status):
        self.status = status
