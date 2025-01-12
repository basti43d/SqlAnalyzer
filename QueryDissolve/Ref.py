from .Entry import Entry

class Ref:

    def __init__(self, entry : Entry):
        self.entry = entry
        self.key_next = None
    
    def set_key_next(self, ref):
        self.key_next = ref
    
    def __str__(self):
        nxt = 'None' if self.key_next is None else self.key_next
        return self.entry.__str__() + ' -> ' + nxt 