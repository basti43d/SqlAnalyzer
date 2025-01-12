import logging

class Entry:
    def __init__(self, table_ref, column, alias, table_chain = ''):
        self.table_ref = table_ref
        self.column = column
        self.alias = alias
        self.table_chain = table_chain
        logging.debug(f'created entry {self}')
    
    def __str__(self):
        tc = None if self.table_chain == '' else self.table_chain
        return '(' + str(self.table_ref) + ', ' + str(self.column) + ', ' + str(self.alias) + ', ' + str(tc) + ')'
    
    def identifier(self):
        return str(self.table_ref) + '.' + str(self.column)
    
    def key_identifier(self):
        #return str(self.table_ref) + '.' + str(self.column)
        return str(self.table_chain) + '.' + str(self.table_ref) + '.' + str(self.column)
    
    def key_base(self):
        return str(self.table_chain) + '.' + str(self.table_ref)
    
    def key_parent(self):
        #bis rechts - 1
        return str(self.table_chain) + '.' + str(self.alias)
    
    def generate_key(table, column, table_chain):
        return str(table_chain) + '.' + str(table) + '.' + str(column)