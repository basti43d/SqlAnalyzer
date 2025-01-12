import unittest
from QueryDissolve.AnalyzeAst import AnalyzeAst

def setup(ast : str):
    path = 'C:\\Users\\basti\\Desktop\\ba\\test_querys\\nested_querys\\asts\\' + ast
    ana = AnalyzeAst(path_to_ast=path)
    ana.dissolve_query()
    jex = ana.get_join_expressions()
    tlr = ana.get_top_level_relations()
    return jex, tlr


class TestAst(unittest.TestCase):

    msg_inv_jex = 'invalid join-expressions'
    msg_inv_tlr = 'invalid top level relation'
    msg_inv_name_res = 'invalid local name resolution in top level relations'


    def test_top_level_relation_extraction(self):
        jex, tlr = setup('q2.json')

        #test join expressions
        self.assertEqual(len(jex), 0, self.msg_inv_jex)

        #test top level relations
        self.assertEqual(len(tlr), 1, self.msg_inv_tlr) 
        self.assertTrue('a' in tlr, )
        pair = tlr['a']
        self.assertEqual(pair['table'], 't1', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'a', self.msg_inv_name_res)
    
    def test_simple_join_expression(self):
        jex, tlr = setup('q3.json')

        #test join expressions
        self.assertEqual(len(jex), 1, self.msg_inv_jex)
        rel1 = jex[0]['rels']['left']
        rel2 = jex[0]['rels']['right']
        self.assertTrue(rel1 == 't1' and rel2 == 't2', self.msg_inv_name_res)
        cols = jex[0]['cols']
        self.assertEqual(len(cols), 1, self.msg_inv_jex)
        col1 = cols[0]['left']
        col2 = cols[0]['right']
        self.assertTrue(col1 == 'a' and col2 == 'b', self.msg_inv_name_res)

        #test top level relations
        self.assertEqual(len(tlr), 2, self.msg_inv_tlr)
        self.assertTrue('a' in tlr and 'b' in tlr, self.msg_inv_tlr)
        pair = tlr['a']
        self.assertEqual(pair['table'], 't1', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'a'), self.msg_inv_name_res
        pair = tlr['b']
        self.assertEqual(pair['table'], 't2', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'b', self.msg_inv_name_res)
    
    def test_query_alias_resolution(self):
        #test join expressions
        jex, tlr = setup('q4.json')

        #test join expressions
        self.assertEqual(len(jex), 0, self.msg_inv_jex)

        #test top level relations
        self.assertEqual(len(tlr), 1, self.msg_inv_tlr) 
        self.assertTrue('a' in tlr, self.msg_inv_tlr)
        pair = tlr['a']
        self.assertEqual(pair['table'], 't1', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'a', self.msg_inv_name_res)
    
    def test_join_with_subquery(self):
        jex, tlr = setup('q5.json')

        #test join expressions
        self.assertEqual(len(jex), 1, self.msg_inv_jex)
        rel1 = jex[0]['rels']['left']
        rel2 = jex[0]['rels']['right']
        self.assertTrue(rel1 == 't1' and rel2 == 't2', self.msg_inv_name_res)
        cols = jex[0]['cols']
        self.assertEqual(len(cols), 1, self.msg_inv_jex)
        col1 = cols[0]['left']
        col2 = cols[0]['right']
        self.assertTrue(col1 == 'a' and col2 == 'b', self.msg_inv_name_res)

        #test top level relations
        self.assertEqual(len(tlr), 2, self.msg_inv_tlr)
        self.assertTrue('a' in tlr and 'b' in tlr, self.msg_inv_tlr)
        pair = tlr['a']
        self.assertEqual(pair['table'], 't1', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'a', self.msg_inv_name_res)
        pair = tlr['b']
        self.assertEqual(pair['table'], 't2', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'b', self.msg_inv_name_res)

    def test_from_with_subquery(self):
        jex, tlr = setup('q6.json')

        #test join expressions
        self.assertEqual(len(jex), 1, self.msg_inv_jex)
        rel1 = jex[0]['rels']['left']
        rel2 = jex[0]['rels']['right']
        self.assertTrue(rel1 == 't1' and rel2 == 't2', self.msg_inv_name_res)
        cols = jex[0]['cols']
        self.assertEqual(len(cols), 2, self.msg_inv_jex)
        col1 = cols[0]['left']
        col2 = cols[0]['right']
        self.assertTrue(col1 == 'a' and col2 == 'b', self.msg_inv_name_res)
        col1 = cols[1]['left']
        col2 = cols[1]['right']
        self.assertTrue(col1 == 'c' and col2 == 'd', self.msg_inv_name_res)

        #test top level relations
        self.assertEqual(len(tlr), 2, self.msg_inv_tlr)
        self.assertTrue('a' in tlr and 'b' in tlr, self.msg_inv_tlr)
        pair = tlr['a']
        self.assertEqual(pair['table'], 't1', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'a', self.msg_inv_name_res)
        pair = tlr['b']
        self.assertEqual(pair['table'], 't2', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'b', self.msg_inv_name_res)
    
    def test_subquery_with_same_alias(self):
        jex, tlr = setup('q7.json')

        #test join expressions
        self.assertEqual(len(jex), 1, self.msg_inv_jex)
        rel1 = jex[0]['rels']['left']
        rel2 = jex[0]['rels']['right']
        self.assertTrue(rel1 == 't8' and rel2 == 't5', self.msg_inv_name_res)
        cols = jex[0]['cols']
        self.assertEqual(len(cols), 1, self.msg_inv_jex)
        col1 = cols[0]['left']
        col2 = cols[0]['right']
        self.assertTrue(col1 == 'id' and col2 == 'id', self.msg_inv_name_res)

        #test top level relations
        self.assertEqual(len(tlr), 1, self.msg_inv_tlr)
        self.assertTrue('a' in tlr, self.msg_inv_tlr)
        pair = tlr['a']
        self.assertEqual(pair['table'], 't5', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'a', self.msg_inv_name_res)
    
    def test_column_and_table_alias(self):
        jex, tlr = setup('q8.json')

        #test join expressions
        self.assertEqual(len(jex), 1, self.msg_inv_jex)
        rel1 = jex[0]['rels']['left']
        rel2 = jex[0]['rels']['right']
        self.assertTrue(rel1 == 't1' and rel2 == 't2', self.msg_inv_name_res)
        cols = jex[0]['cols']
        self.assertEqual(len(cols), 1, self.msg_inv_jex)
        col1 = cols[0]['left']
        col2 = cols[0]['right']
        self.assertTrue(col1 == 'a' and col2 == 'c', self.msg_inv_name_res)

        #test top level relations
        self.assertEqual(len(tlr), 2, self.msg_inv_tlr)
        self.assertTrue('a' in tlr and 'c' in tlr, self.msg_inv_tlr)
        pair = tlr['a']
        self.assertEqual(pair['table'], 't1', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'a', self.msg_inv_name_res)
        pair = tlr['c']
        self.assertEqual(pair['table'], 't2', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'c', self.msg_inv_name_res)
    
    def test_same_alias_for_tlr_and_jex(self):
        jex, tlr = setup('q9.json')

        #test join expressions
        self.assertEqual(len(jex), 2, self.msg_inv_jex)
        rel1 = jex[0]['rels']['left']
        rel2 = jex[0]['rels']['right']
        self.assertTrue(rel1 == 't8' and rel2 == 't9', self.msg_inv_name_res)
        cols = jex[0]['cols']
        self.assertEqual(len(cols), 1, self.msg_inv_jex)
        col1 = cols[0]['left']
        col2 = cols[0]['right']
        self.assertTrue(col1 == 'id' and col2 == 'id', self.msg_inv_name_res)

        rel1 = jex[1]['rels']['left']
        rel2 = jex[1]['rels']['right']
        self.assertTrue(rel1 == 't8' and rel2 == 't5', self.msg_inv_name_res)
        cols = jex[1]['cols']
        self.assertEqual(len(cols), 1, self.msg_inv_jex)
        col1 = cols[0]['left']
        col2 = cols[0]['right']
        self.assertTrue(col1 == 'id' and col2 == 'id', self.msg_inv_name_res)

        #test top level relations
        self.assertEqual(len(tlr), 2, self.msg_inv_tlr)
        self.assertTrue('id' in tlr and 'a' in tlr, self.msg_inv_tlr)
        pair = tlr['id']
        self.assertEqual(pair['table'], 't8', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'id', self.msg_inv_name_res)
        pair = tlr['a']
        self.assertEqual(pair['table'], 't5', self.msg_inv_name_res)
        self.assertEqual(pair['column'], 'a', self.msg_inv_name_res)

    def test_many_joins(self):
        jex, tlr = setup('q10.json')

        #test join expressions
        self.assertEqual(len(jex), 3, self.msg_inv_jex)
        rel_pairs = [('t1', 't2'), ('t1', 't3'), ('t3', 't4')]
        for i, rel_pair in enumerate(rel_pairs):
            rel1 = jex[i]['rels']['left']
            rel2 = jex[i]['rels']['right']
            self.assertTrue(rel1 == rel_pair[0] and rel2 == rel_pair[1], self.msg_inv_name_res)
            cols = jex[i]['cols']
            self.assertEqual(len(cols), 1, self.msg_inv_jex)
            col1 = cols[0]['left']
            col2 = cols[0]['right']
            self.assertTrue(col1 == 'id' and col2 == 'id', self.msg_inv_name_res)


        #test top level relations
        tabs = ['t1', 't2', 't3', 't4']
        cols = ['a', 'b', 'c', 'd']

        for tab, col in zip(tabs, cols): 
            pair = tlr[col]
            self.assertEqual(pair['table'], tab, self.msg_inv_name_res)
            self.assertEqual(pair['column'], col, self.msg_inv_name_res)



if __name__ == '__main__':
    unittest.main()
