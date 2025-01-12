import json
from .GlobalRefs import GlobalRefs
from .AnalyzeAst import AnalyzeAst
from os import listdir 

class Dissolver:

    def __init__(self):
        self.ana = AnalyzeAst()
        self.global_ref = GlobalRefs()
        self.__reset()
    
    def __reset(self):
        self.rels = dict()
        self.defs = dict()
    

    def load_from_directory(self, path_in):
        files = [path_in + file for file in listdir(path_in)]
        self.load_files(files)
    
    def load_single(self, path):
        self.load_files([path])
    
    #fuer defs noch nach views filtern
    def load_files(self, files : list):
        self.__reset()
        for file in files:
            self.ana.set_ast(file)
            self.ana.dissolve_query()
            self.ana.get_join_expressions(self.rels)
            self.ana.get_top_level_relations(self.defs)
        self.global_ref.load_from_dictionary(self.rels, self.defs)
        self.global_ref.dissolve()

    
    def dump_rels(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps(self.rels, indent=4))
    
    def dump_defs(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps(self.defs, indent=4))
    
    def dump_dissolved(self, path):
        self.global_ref.write_dissolved(path)
    
    def get_dissolved(self):
        return self.global_ref.dissolved
