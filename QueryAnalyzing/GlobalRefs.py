import json
import copy

class GlobalRefs:

    def __init__(self):
        self.cache = dict()
    
    def load_from_files(self, path_to_rels, path_to_defs):
        with open(path_to_rels, 'r') as f:
            self.rels = json.loads(f.read())
        with open(path_to_defs, 'r') as f:
            self.defs = json.loads(f.read())

    def load_from_dictionary(self, rels, defs):
        self.rels = rels
        self.defs = defs

    def dissolve(self, path_to_copy):
        cp = copy.deepcopy(self.rels)
        for view_obj in cp:
            for join_block in cp[view_obj]:
                for join_rel in join_block['refs']:
                    for pos in ['left', 'right']:
                        tab = join_rel[pos]['table']
                        col = join_rel[pos]['column']
                        key = tab + '.' + col
                        if key in self.cache:
                            n_tab = self.cache[key][0]
                            n_col = self.cache[key][1]
                        else:
                            r = self.lookup_ref(tab, col)
                            if r is None:
                                continue
                            n_tab = r[0]
                            n_col = r[1]
                            self.cache[key] = (n_tab, n_col)
                        join_rel[pos]['table'] = n_tab
                        join_rel[pos]['column'] = n_col
        n_rels = json.dumps(cp, indent=4)
        with open(path_to_copy, 'w') as f:
            f.write(n_rels)
    
    #!kann in anderer datenbank sein
    def lookup_ref(self, table, column):
        if not table in self.defs:
            return None
        while table in self.defs:
            table2 = self.defs[table][column]["table"]
            column = self.defs[table][column]["column"]
            table = table2
        return (table, column)

#gr = GlobalRefs('rels.json', 'defs.json', None) 
#gr.dissolve('n_rels.json')
    
