from .Entry import Entry
from .Ref import Ref
import logging
import pickle


class Repr:

    H : dict
    B : dict

    def __init__(self):
        self.reset()
    
    def reset(self):
        self.H = dict()
        self.B = dict()
        self.scope = 0
    
    def enter_scope(self):
        self.scope += 1
        logging.debug(f'entered scope {self.scope}')
    
    def exit_scope(self):
        logging.debug(f'exited scope {self.scope}')
        self.scope -= 1
    
    def append(self, entry : Entry, make_parent_ref : bool = False):
        key = entry.key_identifier()
        if key in self.H:
            logging.debug(f'key {key} already in H')
            return key
        self.H[key] = Ref(entry)
        logging.debug(f'inserted {key} into H')
        if make_parent_ref is True:
            key1 = entry.key_parent()
            if self.scope > 0 and key1 in self.H:
                self.H[key1].set_key_next(key)
                logging.debug(f'made reference to parent {key1} for {key} in H')
        return key
    
    def append_all(self, entrys : list[Entry], make_parent_ref : bool):
        for entry in entrys:
            self.append(entry, make_parent_ref)
    
    #for base-tables
    def append_base(self, table_name, table_alias, table_chain):
        key = table_chain + '.' + table_alias
        self.B[key] = table_name
        logging.debug(f'appended {key} to B')

    def resolve_column_refs(self, entry : Entry):
        key = entry.key_identifier()
        key1 = key
        while self.H[key].key_next is not None:
            key = self.H[key].key_next
        col = self.H[key].entry.column
        key = self.H[key].entry.key_base()
        logging.debug(f'resolved {key1} to base column {col} in relation {self.B[key]}')
        return (self.B[key], col)


    def resolve_relations(self, relations : list[tuple[Entry]]):
        l = []
        for relation in relations:
            entry0 = self.resolve_column_refs(relation[0])
            entry1 = self.resolve_column_refs(relation[1])
            l.append((entry0, entry1))
        return l
    
    def save_resolved_columns(self, path, name):
        dct = {}
        for key in self.H:
            ref = self.H[key].entry.identifier()
            resolved = self.resolve_column_refs(key, 0).identifier()
            dct[ref] = resolved
        with open(path + '\\' + name + '.pkl', 'wb') as f:
            pickle.dump(dct, f)
    
    def print_H(self):
        print('\n'.join([E + ' | ' + str(self.H[E]) for E in self.H]))
    

    def test(self):
        repr = Repr()

        e1 = Entry('t1', 'x', 'x')
        repr.append(e1)
        e2 = Entry('t2', 'y', 'y')
        repr.append(e2)
        repr.enter_scope()
        e3 = Entry('t3', 'a', 'x', '.t1')
        repr.append(e3, make_parent_ref=True)
        repr.exit_scope()
        repr.enter_scope()
        e4 = Entry('t4', 'b', 'y', '.t2')
        repr.append(e4, make_parent_ref=True)
        repr.exit_scope()

        repr.append_base('t5', 't3', '.t1')
        repr.append_base('t6', 't4', '.t2')

        repr.print_H()
        print(repr.B)

        relations = [(e1, e2), (e3, e4)]
        r = repr.resolve_relations(relations=relations)
        for e in r:
            print(str(e[0]), str(e[1]))


 