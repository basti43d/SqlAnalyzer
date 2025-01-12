import logging
from QueryDissolve.Dissolver import Dissolver, AnalyzeAst, GlobalRefs
from BuildRelations.RelationExtraction import RelationExtraction


logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s')

connection_string = 'DRIVER={ODBC Driver 18 for SQL Server};Server=(localdb)\MSSQLLocalDb;database=testDb;'
#path = 'c:\\users\\basti\\Desktop\\ba\\test_querys\\relations\\asts\\'
path = 'c:\\users\\basti\\Desktop\\ba\\test_querys\\nested_querys\\asts\\q9.json'

ana = AnalyzeAst(path)
ana.dissolve_query()
jex = {}
tlr = {}
ana.get_join_expressions(jex)
ana.get_top_level_relations(tlr)


grf = GlobalRefs()
grf.load_from_dictionary(rels=jex, defs=tlr)
grf.dissolve()
rels = grf.dissolved


#res = Dissolver()
#res.load_files([path + 'q9.json'])
#rels = res.get_dissolved()
relex = RelationExtraction(relations=rels, connection_string=connection_string)
relex.aggregate()
relex.build_rels()
attr = relex.erm.entities
rels = relex.erm.relations
