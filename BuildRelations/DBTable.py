import logging

class DBTable:
    def __init__(self, rel_name, columns, pk_columns):
        self.rel_name = rel_name
        self.columns = columns
        self.pk_columns = pk_columns
        self.pk_ref_relations = [0 for _ in self.pk_columns]
        logging.debug(f'got schema of relation {rel_name} with PK {pk_columns}')
    
    def is_pk(self, columns):
        return True if set(columns) == set(self.pk_columns) else False
    
    def is_part_of_pk(self, columns):
        if len(columns) >= len(self.pk_columns):
            return False
        for elm in columns:
            if elm not in self.pk_columns:
                return False
        return True
    
    def add_pk_col(self, col, rel):
        for i, pkc in enumerate(self.pk_columns):
            if pkc == col:
                if self.pk_ref_relations[i] != 0:
                    pass
                else:
                    self.pk_ref_relations[i] = rel
                    logging.debug(f'column {col} of relation {rel} was found as attribute of PK for relation {self.rel_name}')

    def add_pk_cols(self, cols, rel):
        for col in cols:
            self.add_pk_col(col, rel)