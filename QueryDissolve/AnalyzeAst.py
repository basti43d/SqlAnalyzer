import logging
import json
from .Repr import Repr, Entry


class AnalyzeAst:

    def __init__(self, path_to_ast = None):
        if path_to_ast is not None:
            self.set_ast(path_to_ast=path_to_ast)
        logging.debug('created AnalyzeAst object successfully')
    
    def set_ast(self, path_to_ast, name = None):
        self.path_to_ast = path_to_ast
        with open(path_to_ast, 'r') as f:
            ast = f.read()
        self.jast = json.loads(ast)
        self.name = name if name is not None else path_to_ast.split('\\')[-1].split('.')[0]
        self.repr = Repr()
        #self.relations = list()
        self.tlr = None
        self.tlr_resolved = None
        self.join_blocks = []
        logging.debug(f'initialized ast with {path_to_ast}')
    
    #input: select-object
    def __get_projections(self, obj, table_chain = ''):
        lst = []
        try:
            for eobj in obj['Projection']:
                if 'WildcardAdditionalOptions' in eobj:
                    #sollte nicht vorkommen
                    logging.error(f'wildcard operator in query {self.name}')
                    continue
                if 'Ident' in eobj['Expression']:
                    logging.error(f'invalid attribute format in query {self.name}')
                    continue
                obj = eobj['Expression']['Idents']
                tab = obj[0]['Value']
                col = obj[1]['Value']
                if 'Alias' in eobj:
                    alias = eobj['Alias']['Value']
                else:
                    alias = col
                e = Entry(tab, col, alias, table_chain)
                lst.append(e)
                #self.repr.append(e, make_parent_ref=True)
                #print('get_projections for ast in file ' + self.path + ': ' + str(e))
        except Exception as ex:
            logging.error('error in get_projections for ast in file ' + str(self.name) + ': ' + repr(ex))
        return lst
    
    def __enter_scope(self):
        self.repr.enter_scope()
    def __exit_scope(self):
        self.repr.exit_scope()
    
    def dissolve_query(self):
        logging.debug('starting dissolving query')
        #self.tlr = self.__get_top_level_projections()
        self.__dissolve_query_rec(self.jast['Query'])
        logging.debug('finished dissolving query')
        #projektionen aufloesen
        self.tlr_resolved = [self.repr.resolve_column_refs(proj) for proj in self.tlr]
        logging.debug('finished resolving top level projections')
    
    #query-object
    def __dissolve_query_rec(self, query_obj, table_name_chain = '', scope = 1):
        self.__enter_scope()
        proj = self.__get_projections(query_obj['Body']['Select'], table_name_chain)
        make_parent_ref = True
        if scope == 1:
            self.tlr = proj
            make_parent_ref = False
        self.repr.append_all(proj, make_parent_ref=make_parent_ref)
        from_obj = query_obj['Body']['Select']['From'][0]
        lst = self.__get_join_columns(from_obj, table_name_chain)
        self.__dissolve_from_clause(from_obj, table_name_chain, scope + 1)
        self.__dissolve_join_clauses(from_obj, table_name_chain, scope + 1)
        if lst != None:
            lst = self.repr.resolve_relations(lst)
            self.join_blocks += self.__rearange_join_blocks(lst)
        self.__exit_scope()
    
    def __rearange_join_blocks(self, lst):
        blocks = []
        coll = {}
        for tp in lst:
            key = self.__generate_key(tp[0][0], tp[1][0])
            if key in coll:
                pos = coll[key]
                blocks[pos].append(tp)
            else:
                coll[key] = len(blocks)
                blocks.append([tp])
        return blocks

    
    def __generate_key(self, rel1, rel2):
        return rel1 + '.' + rel2 if rel1 < rel2 else rel2 + '.' + rel1


    #from-object
    def __dissolve_from_clause(self, from_obj, table_name_chain, scope):
        #sub-query: relation-subquery-body-select
        if 'SubQuery' in from_obj['Relation']:
            #alias = None
            #al = obj['Relation']['Alias']
            #if al != 'null':
            #    alias = al['Name']['Value']
            alias = from_obj['Relation']['Alias']['Name']['Value']
            tc = table_name_chain + '.' + alias
            logging.debug(f'starting dissolving subquery {alias} (path {tc})')
            self.__dissolve_query_rec(from_obj['Relation']['SubQuery'], tc, scope + 1)
        #base-table: relation-name-values
        else:
            name = from_obj['Relation']['Name']['Values'][0]['Value']
            alias = name
            if from_obj['Relation']['Alias'] != None:
                alias = from_obj['Relation']['Alias']['Name']['Value']
            logging.debug(f'dissolved {table_name_chain} to base relation {name}')
            self.repr.append_base(table_name=name, table_alias=alias, table_chain=table_name_chain)
    
    def __get_join_columns(self, obj, table_name_chain):
        if obj['Joins'] == None:
            logging.debug(f'no join expressions found for f{table_name_chain}')
            return None
        rels = []
        logging.debug(f'extracting join expressions from {table_name_chain}')
        for join in obj['Joins']:
            #name-> subquery oder base-table
            #alias = join['Relation']['Alias']
            constr = join['JoinOperator']['JoinConstraint']['Expression']
            while 'Expression' in constr:
                constr = constr['Expression']
            lst = []
            self.__parse_join_expression_tree(constr, lst)
            for li in lst:
                e1 = Entry(li[0][0], li[0][1], li[0][1], table_name_chain)
                self.repr.append(e1, make_parent_ref=False)
                e2 = Entry(li[1][0], li[1][1], li[1][1], table_name_chain)
                self.repr.append(e2, make_parent_ref=False)
                rels.append((e1, e2))
                logging.debug(f'extracted valid expression {e1.identifier()} - {e2.identifier()}')
        return rels
    
    #join-object
    def __dissolve_join_clauses(self, join_obj, table_name_chain, scope):
        if join_obj['Joins'] == None:
            return
        for join in join_obj['Joins']:
            if 'SubQuery' in join['Relation']:
                alias = ''
                al = join['Relation']['Alias']
                if al != None:
                    alias = al['Name']['Value']
                self.__dissolve_query_rec(join['Relation']['SubQuery'], table_name_chain + '.' + alias, scope)
            else:
                name = join['Relation']['Name']['Values'][0]['Value']
                alias = name
                if join['Relation']['Alias'] != None:
                    alias = join['Relation']['Alias']['Name']['Value']
                self.repr.append_base(table_name=name, table_alias=alias, table_chain=table_name_chain) 

    
    #left-op-right-object
    def __check_leaf(self, obj):
        return False if 'Left' in obj['Left'] else True
    
    def __check_subexpression(self, obj):
        if 'Left' in obj and 'Expression' in obj['Left']: return True
        if 'Right' in obj and 'Expression' in obj['Right']: return True
        return False
    
    def __get_expression_operator(self, obj):
        return obj['Op']
    
    #left-op-right-object leaf
    def __parse_join_expression_node(self, left_op_right_obj):
        if 'Value' in left_op_right_obj['Right']:
            logging.debug(f'ignoring expression with constant {left_op_right_obj}')
            return None
        lt = left_op_right_obj['Left']['Idents'][0]['Value']
        lc = left_op_right_obj['Left']['Idents'][1]['Value']
        rt = left_op_right_obj['Right']['Idents'][0]['Value']
        rc = left_op_right_obj['Right']['Idents'][1]['Value']
        logging.debug(f'found key-expression {lt}.{lc} - {rt}.{rc}')
        return ((lt, lc), (rt, rc))

    
    #expression-object
    def __parse_join_expression_tree(self, expression_obj, lst):
        logging.debug('starting parsing join expression')
        if(self.__check_leaf(expression_obj) == False):
            if self.__get_expression_operator(expression_obj) != 14:
                #keine and-verknuepfung auf oberstem level -> kein key
                logging.debug(f'no \'and\'-operator on top level, no key expression')
                lst = None
                return
            self.__parse_join_expression_tree(expression_obj['Left'], lst)
        else:
            if self.__check_subexpression(expression_obj) == False:
                if self.__get_expression_operator(expression_obj) != 12:
                    #kein ==-verknuepfung -> kein key
                    logging.debug(f'no \'=\'-operator on top level, no key expression')
                    return
                tp = self.__parse_join_expression_node(expression_obj)
                if tp is not None and lst is not None:
                    lst.append(tp)
                return
            else:
                logging.debug(f'ignoring subexpression {expression_obj}')
                return
        
        #if self.__check_leaf(expression_obj['Right']) == True:
        #fuer rechten teilbaum muss die pruefung anders erfolgen, weil der parser
        #hier ein neues 'expression' objekt erstellt
        if 'Expression' not in expression_obj['Right']:
            if self.__get_expression_operator(expression_obj['Right']) != 12:
                #kein ==-verknuepfung -> kein key
                logging.debug(f'no \'=\'-operator on top level, no key expression')
                return
            tp = self.__parse_join_expression_node(expression_obj['Right'])
            if tp is not None and lst is not None:
                lst.append(tp)
                return
    
    def get_join_expressions(self, append_to : dict = None):
        blocks = []
        for rel_block in self.join_blocks:
            block = dict()
            block['rels'] = {'left': rel_block[0][0][0], 'right': rel_block[0][1][0]}
            lst = list()
            for rel in rel_block:
                exp = {'left': rel[0][1], 'right': rel[1][1]}
                lst.append(exp)
            block['cols'] = lst
            blocks.append(block)
        if append_to is not None:
            append_to[self.name] = blocks
        else:
            return blocks


    def get_top_level_relations(self, append_to : dict = None):
        columns = dict()
        for i in range(0, len(self.tlr)):
            col_name = self.tlr[i].alias
            columns[col_name] = {'table': self.tlr_resolved[i][0], 'column': self.tlr_resolved[i][1]}
        if append_to is not None:
            append_to[self.name] = columns
        else:
            return columns

    def print_H(self):
        self.repr.print_H()

    def print_ast(self):
        print(json.dumps(self.jast, indent=2))
    
        
