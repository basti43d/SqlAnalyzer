import unittest
from QueryDissolve.AnalyzeAst import AnalyzeAst
from QueryDissolve.GlobalRefs import GlobalRefs


class TestGlobalNameResolution(unittest.TestCase):

    def test_resolve_between_views(self):
        path = 'C:\\Users\\basti\\Desktop\\ba\\test_querys\\view_relations\\asts\\'
        ana = AnalyzeAst() 
        tlrs = {}
        jexs = {}
        for view in ['v1.json', 'v2.json']:
            ana.set_ast(path + view)
            ana.dissolve_query()
            ana.get_join_expressions(jexs)
            ana.get_top_level_relations(tlrs)
        gr = GlobalRefs()
        gr.load_from_dictionary(rels=jexs, defs=tlrs)
        gr.dissolve()
        dslvd = gr.dissolved 
        self.assertEqual(len(dslvd), 2, 'invalid view resolution')
        self.assertTrue('v1' in dslvd and 'v2' in dslvd, 'invalid view resolution')
        
        views = ['v1', 'v2']
        rel_pairs = [('t1', 't2'), ('t1', 't3')]        

        for view, rel_pair in zip(views, rel_pairs):
            rels = dslvd[view][0]['rels']
            self.assertEqual(rels['left'], rel_pair[0], 'invalid global name resolution for relation')
            self.assertEqual(rels['right'], rel_pair[1], 'invalid global name resolution for relation')
            col = dslvd[view][0]['cols'][0]['left']
            self.assertEqual(col, 'id', 'invalid global name resolution for column')
            col = dslvd[view][0]['cols'][0]['right']
            self.assertEqual(col, 'id', 'invalid global name resolution for column')

if __name__ == '__main__':
    unittest.main()