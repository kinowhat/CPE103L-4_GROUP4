class Item:
    def __init__(self, name: str = "", quantity: int = 0, price: float = 0):
        self.name = name
        self.quantity = quantity
        self.price = price
        
    def setLowStockFlag(self):
        return self.quantity < 10
        
    def getName(self):
        return self.name
        
    def getQuantity(self):
        return self.quantity
        
    def getPrice(self):
        return self.price
        
    def setName(self, name):
        self.name = name
        
    def setQuantity(self, quantity):
        self.quantity = quantity
        
    def setPrice(self, price):
        self.price = price
    