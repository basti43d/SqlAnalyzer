import json
from Repr import Repr, Entry


class AnalyzeAst:

    def __init__(self, path_to_ast = None):
        if path_to_ast is not None:
            self.path_to_ast = path_to_ast
            self.set_ast(path_to_ast)
    
    def set_ast(self, ast, name = None):
        self.jast = json.loads(ast)
        self.name = name
        self.repr = Repr()
        self.relations = list()
        self.tlr = None
        self.tlp_resolved = None
    
    def __get_top_level_projections(self):
        return self.__get_projections(self.jast['Query']['Body']['Select'])


    #input: select-object
    def __get_projections(self, obj, table_chain = ''):
        lst = []
        try:
            for eobj in obj['Projection']:
                if 'WildcardAdditionalOptions' in eobj:
                    #sollte nicht vorkommen
                    raise Exception('keine querys mit wildcard (*) erlaubt')
                if 'Ident' in eobj['Expression']:
                    raise Exception('alle projections muessen die form t.c haben')
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
            print('error in get_projections for ast in file ' + str(self.name) + ': ' + repr(ex))
        return lst
    
    def print_relations(self):
        if len(self.relations) == 0:
            print('no relations found')
        else:
            for block in self.relations:
                for rel in block:
                    print(str(rel[0][0]) + '.' + 
                          str(rel[0][1]) + ' = ' + 
                          str(rel[1][0]) + '.' + 
                          str(rel[1][1]))
    
    def print_top_level_projections(self):
        for proj in self.tlr:
            print(proj)
    
    def print_H(self):
        self.repr.print_H()

    def print_ast(self):
        print(json.dumps(self.jast, indent=2))
    
    def __enter_scope(self):
        self.repr.enter_scope()
    def __exit_scope(self):
        self.repr.exit_scope()
    
    def test_dissolve(self):
        self.dissolve_query(self.jast['Query'])
        self.repr.print_H()
        print(self.relations)
    
    def dissolve_query(self):
        #top_level_projections
        self.tlr = self.__get_top_level_projections()
        self.__dissolve_query_rec(self.jast['Query'])
        #resolve top_level_columns
        #save self.relations
        #self.repr.print_H()
        self.tlr_resolved = [self.repr.resolve_column_refs(proj, 1) for proj in self.tlr]
    
    #query-object
    def __dissolve_query_rec(self, obj, table_name_chain = ''):
        self.__enter_scope()
        proj = self.__get_projections(obj['Body']['Select'], table_name_chain)
        self.repr.append_all(proj, make_parent_ref=True)
        lst = self.__get_join_columns(obj['Body']['Select']['From'][0], table_name_chain)
        self.__dissolve_from_clause(obj['Body']['Select']['From'][0], table_name_chain)
        self.__dissolve_join_clauses(obj['Body']['Select']['From'][0], table_name_chain)
        if lst != None:
            self.relations.append(self.repr.resolve_relations(lst))
        self.__exit_scope()


    #from-object
    def __dissolve_from_clause(self, obj, table_name_chain=''):
        #sub-query: relation-subquery-body-select
        if 'SubQuery' in obj['Relation']:
            alias = None
            al = obj['Relation']['Alias']
            if al != 'null':
                alias = al['Name']['Value']
            self.__dissolve_query_rec(obj['Relation']['SubQuery'], table_name_chain + '.' + alias)
        #base-table: relation-name-values
        else:
            name = obj['Relation']['Name']['Values'][0]['Value']
            alias = name
            if obj['Relation']['Alias'] != None:
                alias = obj['Relation']['Alias']['Name']['Value']
            self.repr.append_base(table_name=name, table_alias=alias, table_chain=table_name_chain)
    
    def __get_join_columns(self, obj, table_name_chain):
        if obj['Joins'] == None:
            return
        rels = []
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
                e2 = Entry(li[1][0], li[1][1], li[1][1], table_name_chain)
                self.repr.append(e1, make_parent_ref=False)
                self.repr.append(e2, make_parent_ref=False)
                rels.append((e1, e2))
        return rels
    
    #join-object
    def __dissolve_join_clauses(self, obj, table_name_chain):
        if obj['Joins'] == None:
            return
        for join in obj['Joins']:
            if 'SubQuery' in join['Relation']:
                alias = ''
                al = join['Relation']['Alias']
                if al != None:
                    alias = al['Name']['Value']
                self.__dissolve_query_rec(join['Relation']['SubQuery'], table_name_chain + '.' + alias)
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
    def __parse_join_expression_node(self, obj):
        if 'Value' in obj['Right']:
            return None
        lt = obj['Left']['Idents'][0]['Value']
        lc = obj['Left']['Idents'][1]['Value']
        rt = obj['Right']['Idents'][0]['Value']
        rc = obj['Right']['Idents'][1]['Value']
        return ((lt, lc), (rt, rc))

    
    #expression-object
    def __parse_join_expression_tree(self, obj, lst):
        if(self.__check_leaf(obj) == False):
            if self.__get_expression_operator(obj) != 14:
                #keine and-verknuepfung auf oberstem level -> kein key
                lst = None
                return
            self.__parse_join_expression_tree(obj['Left'], lst)
        else:
            if self.__check_subexpression(obj) == False:
                if self.__get_expression_operator(obj) != 12:
                    #kein ==-verknuepfung -> kein key
                    return
                tp = self.__parse_join_expression_node(obj)
                if tp is not None and lst is not None:
                    lst.append(tp)
                return
            else:
                return
        
        if self.__check_leaf(obj['Right']) == True:
            if self.__get_expression_operator(obj['Right']) != 12:
                #kein ==-verknuepfung -> kein key
                return
            tp = self.__parse_join_expression_node(obj['Right'])
            #kein vergleich mit konstante
            if tp is not None and lst is not None:
                lst.append(tp)
                return
    
    def append_join_expressions(self, dct : dict):
        blocks = list()
        for rel_block in self.relations:
            block = dict()
            lst = list()
            for rel in rel_block:
                exp = dict()
                exp['left'] = {'table' : rel[0][0], 'column': rel[0][1]}
                exp['right'] = {'table': rel[1][0], 'column': rel[1][1]}
                lst.append(exp)
            block['refs'] = lst
            blocks.append(block)
        dct[self.name] = blocks


    def append_top_level_relations(self, dct : dict):
        columns = dict()
        for i in range(0, len(self.tlr)):
            col_name = self.tlr[i].alias
            columns[col_name] = {'table': self.tlr_resolved[i][0], 'column': self.tlr_resolved[i][1]}
        dct[self.name] = columns

#path = './ast/ast9.txt'
#ana = AnalyzeAst(path)
#dct_rel = dict()
#dct_defs = dict()
#ana.print_ast()
#ana.dissolve_query()
#ana.append_join_expressions(dct_rel)
#ana.append_top_level_relations(dct_defs)

#with open('defs1.json', 'w') as f:
#    f.write(json.dumps(dct_defs, indent=2))

#with open('rels1.json', 'w') as f:
#    f.write(json.dumps(dct_rel, indent=2))