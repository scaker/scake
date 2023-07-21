
class Bar():
    def __init__(self, a, b=10):
        self.a = a
        self.b = b
    
    def sum(self, new_a=False, new_b=False):
        if new_a and new_b:
            return new_a + new_b
        else:
            return self.a + self.b
    
    def mul(self):
        return self.a * self.b

    def __call__(self, val=-3):
        x = self.sum()
        y = self.mul()
        return val + x + y
