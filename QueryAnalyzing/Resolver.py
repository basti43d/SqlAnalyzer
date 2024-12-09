import json
from GlobalRefs import GlobalRefs
from RelationExtraction.AnalyzeDB import AnalyzeDB
from AnalyzeAst import AnalyzeAst
from os import listdir 
from os.path import join

class Resolver:

    def __init__(self):
        self.ast_analyze = AnalyzeAst()
        self.reference_resolver = GlobalRefs()
        self.rels = dict()
        self.defs = dict()

    def load_from_db(self, connection_string):
        ad = AnalyzeDB(connection_string=connection_string)
        self.view_defs = ad.get_view_definitions()

    def load_from_directory(self, path_in, path_out):
        for file in listdir(path_in):
            with open(join(path_in, file)) as f:
                ast = f.read()
            name = file.split('.')[0]
            self.ast_analyze.set_ast(ast, name)
            self.ast_analyze.dissolve_query()
            self.ast_analyze.append_join_expressions(self.rels)
            self.ast_analyze.append_top_level_relations(self.defs)

            self.reference_resolver.load_from_dictionary(self.rels, self.defs)
            self.reference_resolver.dissolve(path_out)
    
    def dump_rels(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps(self.rels, indent=4))
    
    def dump_defs(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps(self.defs, indent=4))

r = Resolver()
path_ast = 'tests/view_relations/asts'
path = 'tests/view_relations/results/'
r.load_from_directory(path_ast, path + '/dissolved.json')
r.dump_rels(path + '/rels.json')
r.dump_defs(path + '/defs.json')
        