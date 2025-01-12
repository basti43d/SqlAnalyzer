import logging
import json
import copy

class GlobalRefs:

    def __init__(self):
        self.dissolved = None
    
    def load_from_files(self, path_to_rels, path_to_defs):
        with open(path_to_rels, 'r') as f:
            self.rels = json.loads(f.read())
        logging.debug(f'imported relations from {path_to_rels}')
        with open(path_to_defs, 'r') as f:
            self.defs = json.loads(f.read())
        logging.debug(f'imported definitions from {path_to_rels}')

    def load_from_dictionary(self, rels, defs):
        self.rels = rels
        logging.debug('imported relations from dictionary')
        self.defs = defs
        logging.debug('imported definitions from dictionary')

    def dissolve(self):
        self.dissolved = copy.deepcopy(self.rels)
        for view_obj in self.dissolved:
            for join_block in self.dissolved[view_obj]:
                rel1 = join_block['rels']['left']
                rel2 = join_block['rels']['right']
                rels = [rel1, rel2]
                rels_last = [None, None]
                for join_col_pair in join_block['cols']:
                        for i, pos in enumerate(['left', 'right']):
                            col = join_col_pair[pos]
                            rel_n, col_n = self.__lookup_ref(rels[i], col)
                            if rels_last[i] == None:
                                rels_last[i] = rel_n
                            elif rels_last[i] != rel_n:
                                join_col_pair[f'{pos}{i}'] = rel_n
                                logging.info(f'{rels[i]} of join-block of {rels[i]} : {rels[1 - i]} leads to different relations {rel_n} and {rels_last[i]}')
                            join_col_pair[pos] = col_n
                            logging.debug(f'reduced {rel1}.{col} to {rel_n}.{col_n}')
                join_block['rels']['left'] = rels_last[0]
                join_block['rels']['right'] = rels_last[1]
        
    def write_dissolved(self, path):
        n_rels = json.dumps(self.dissolved, indent=4)
        with open(path, 'w') as f:
            f.write(n_rels)
    
    #zusaetzliche liste mit allen relationen oder views verwenden
    #->referenzen auf andere db erkennen
    def __lookup_ref(self, table, column):
        while table in self.defs:
            table2 = self.defs[table][column]["table"]
            column = self.defs[table][column]["column"]
            table = table2
        return table, column

