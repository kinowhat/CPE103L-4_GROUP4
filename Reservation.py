class Reservation:

    def __init__(self, username, item_id, qty, pickup_date, status="pending"):
        self.username = username
        self.item_id = item_id
        self.qty = qty
        self.pickup_date = pickup_date
        self.status = status

    def to_dict(self):
        return {
            "username": self.username,
            "item_id": self.item_id,
            "qty": self.qty,
            "pickup_date": self.pickup_date,
            "status": self.status
        }
