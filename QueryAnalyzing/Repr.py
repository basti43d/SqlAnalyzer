import pickle

class Entry:
    def __init__(self, table_ref, column, alias, table_chain=''):
        self.table_ref = table_ref
        self.column = column
        self.alias = alias
        self.table_chain = table_chain
    
    def __str__(self):
        tc = None if self.table_chain == '' else self.table_chain
        return '(' + str(self.table_ref) + ', ' + str(self.column) + ', ' + str(self.alias) + ', ' + str(tc) + ')'
    
    def identifier(self):
        return str(self.table_ref) + '.' + str(self.column)
    
    def key_identifier(self):
        #return str(self.table_ref) + '.' + str(self.column)
        return str(self.table_chain) + '.' + self.table_ref + '.' + str(self.column)
    
    def key_base(self):
        return str(self.table_chain) + '.' + self.table_ref
    
    def key_parent(self):
        #bis rechts - 1
        return str(self.table_chain) + '.' + str(self.alias)
    
    def generate_key(table, column, table_chain):
        return table_chain + '.' + str(table) + '.' + str(column)

class Ref:

    def __init__(self, entry : Entry):
        self.entry = entry
        self.key_next = None
    
    def set_key_next(self, ref):
        self.key_next = ref
    
    def __str__(self):
        nxt = 'None' if self.key_next is None else self.key_next
        return self.entry.__str__() + ' -> ' + nxt 
    


class Repr:

    H : list[dict]
    B : dict

    def __init__(self):
        self.reset()
    
    def reset(self):
        self.H = list()
        self.H.append(dict())
        self.B = dict()
        self.scope = 0
    
    def enter_scope(self):
        self.scope += 1
        if len(self.H) <= self.scope:
            self.H.append(dict())
    
    def exit_scope(self):
        self.scope -= 1
    
    def append(self, entry : Entry, make_parent_ref : bool):
        key = entry.key_identifier()
        if key in self.H[self.scope]:
            return key

        self.H[self.scope][key] = Ref(entry)

        if make_parent_ref is True:
            key1 = entry.key_parent()
            if self.scope > 0 and key1 in self.H[self.scope - 1]:
                self.H[self.scope - 1][key1].set_key_next(key)
        return key
    
    def append_all(self, entrys : list[Entry], make_parent_ref : bool):
        for entry in entrys:
            self.append(entry, make_parent_ref)
    
    #for base-tables
    def append_base(self, table_name, table_alias, table_chain):
        key = table_chain + '.' + table_alias
        self.B[key] = table_name

    def resolve_column_refs(self, entry : Entry, sc):
        key = entry.key_identifier()
        while self.H[sc][key].key_next is not None:
            key = self.H[sc][key].key_next
            sc += 1
        col = self.H[sc][key].entry.column
        key = self.H[sc][key].entry.key_base()
        return (self.B[key], col)


    def resolve_relations(self, relations : list[tuple[Entry]]):
        l = []
        for relation in relations:
            entry0 = self.resolve_column_refs(relation[0], self.scope)
            entry1 = self.resolve_column_refs(relation[1], self.scope)
            l.append((entry0, entry1))
        return l
    
    def save_resolved_columns(self, path, name):
        dct = {}
        for key in self.H[0]:
            ref = self.H[0][key].entry.identifier()
            resolved = self.resolve_column_refs(key, 0).identifier()
            dct[ref] = resolved
        with open(path + '\\' + name + '.pkl', 'wb') as f:
            pickle.dump(dct, f)
    
    def save_resolved_relations(self, relations : list[tuple[tuple[str, str]]]):
        pass

        
    def print_H(self):
        print('\n\n'.join(['\n'.join([E + ' | ' + str(T[E]) for E in T]) for T in self.H]))
    

    def test():
        repr = Repr()

        e = Entry('t1', 'x', 'x')
        repr.append(e)
        e = Entry('t2', 'y', 'y')
        repr.append(e)
        repr.enter_scope()
        e = Entry('t3', 'a', 'x', 't1')
        repr.append(e)
        repr.exit_scope()
        repr.enter_scope()
        e = Entry('t4', 'b', 'y', 't2')
        repr.append(e)
        repr.exit_scope()

        repr.print_H()

        relations = [(('t1', 'x'), ('t2', 'y'))]
        r = repr.resolve_relations(relations=relations)
        for e in r:
            print(str(e[0]), str(e[1]))


 