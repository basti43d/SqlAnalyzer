import unittest
from QueryDissolve.AnalyzeAst import AnalyzeAst

path = 'C:\\Users\\basti\\Desktop\\ba\\test_querys\\pk_joins\\asts\\'

def setup(path):
    ana = AnalyzeAst(path)
    ana.dissolve_query()
    return ana.join_blocks

class TestKeyExpressions(unittest.TestCase):

    def test_simple_join_expr(self):
        jex = setup(path + 'test1.json')
        self.assertEqual(len(jex), 1, 'invalid number of join blocks')
        self.assertEqual(len(jex[0]), 1, 'invalid number of subexpressions')
        self.assertEqual(jex[0][0][0][0], 't1', 'invalid relation extracted')
        self.assertEqual(jex[0][0][1][0], 't2', 'invalid relation extracted')
        self.assertEqual(jex[0][0][0][1], 'id', 'invalid column extracted')
        self.assertEqual(jex[0][0][1][1], 'id', 'invalid column extracted')
    

    def test_many_attributes(self):
        jex = setup(path + 'test2.json')
        self.assertEqual(len(jex), 1, 'invalid number of join blocks')
        self.assertEqual(len(jex[0]), 2, 'invalid number of subexpressions')
        for i, col in enumerate(['id1', 'id2']):
            self.assertEqual(jex[0][i][0][0], 't1', 'invalid relation extracted')
            self.assertEqual(jex[0][i][1][0], 't2', 'invalid relation extracted')
            self.assertEqual(jex[0][i][0][1], col, 'invalid column extracted')
            self.assertEqual(jex[0][i][1][1], col, 'invalid column extracted')
    

    def test_many_expressions(self):
        jex = setup(path + 'test3.json')
        self.assertEqual(len(jex), 2, 'invalid number of join blocks')
        self.assertEqual(len(jex[0]), 1, 'invalid number of join column pairs')
        self.assertEqual(len(jex[1]), 1, 'invalid number of join column pairs')
        self.assertEqual(jex[0][0][0][0], 't4', 'invalid relation extracted')
        self.assertEqual(jex[0][0][1][0], 't3', 'invalid relation extracted')
        self.assertEqual(jex[0][0][0][1], 'id1', 'invalid column extracted')
        self.assertEqual(jex[0][0][1][1], 'id2', 'invalid column extracted')
        self.assertEqual(jex[1][0][0][0], 't1', 'invalid relation extracted')
        self.assertEqual(jex[1][0][1][0], 't4', 'invalid relation extracted')
        self.assertEqual(jex[1][0][0][1], 'id', 'invalid column extracted')
        self.assertEqual(jex[1][0][1][1], 'id1', 'invalid column extracted')
    
    def test_subexpressions(self):
        jex = setup(path + 'test4.json')
        self.assertEqual(len(jex), 1, 'invalid number of join blocks')
        self.assertEqual(len(jex[0]), 2, 'invalid number of join column pairs')
        self.assertEqual(jex[0][0][0][0], 't1', 'invalid relation extracted')
        self.assertEqual(jex[0][0][1][0], 't2', 'invalid relation extracted')
        self.assertEqual(jex[0][0][0][1], 'id1', 'invalid column extracted')
        self.assertEqual(jex[0][0][1][1], 'id1', 'invalid column extracted')
        self.assertEqual(jex[0][1][0][0], 't1', 'invalid relation extracted')
        self.assertEqual(jex[0][1][1][0], 't2', 'invalid relation extracted')
        self.assertEqual(jex[0][1][0][1], 'id2', 'invalid column extracted')
        self.assertEqual(jex[0][1][1][1], 'id2', 'invalid column extracted')


    def test_invalid_operators(self):
        jex = setup(path + 'test5.json')
        self.assertEqual(len(jex), 1, 'invalid number of join blocks')
        self.assertEqual(len(jex[0]), 2, 'invalid number of join blocks')
        self.assertEqual(len(jex[0]), 2, 'invalid number of join blocks')
        self.assertEqual(jex[0][0][0][0], 't1', 'invalid relation extracted')
        self.assertEqual(jex[0][0][1][0], 't2', 'invalid relation extracted')
        self.assertEqual(jex[0][0][0][1], 'id1', 'invalid column extracted')
        self.assertEqual(jex[0][0][1][1], 'id1', 'invalid column extracted')
        self.assertEqual(jex[0][1][0][0], 't1', 'invalid relation extracted')
        self.assertEqual(jex[0][1][1][0], 't2', 'invalid relation extracted')
        self.assertEqual(jex[0][1][0][1], 'id2', 'invalid column extracted')
        self.assertEqual(jex[0][1][1][1], 'id2', 'invalid column extracted')
    
    def test_or_in_top_level(self):
        jex = setup(path + 'test6.json')
        self.assertEqual(len(jex), 0, 'invalid number of join blocks')
    
    def test_constants_in_expression(self):
        jex = setup(path + 'test7.json')
        self.assertEqual(len(jex), 1, 'invalid number of join blocks')
        self.assertEqual(len(jex[0]), 1, 'invalid number of join blocks')
        self.assertEqual(jex[0][0][0][0], 't1', 'invalid relation extracted')
        self.assertEqual(jex[0][0][1][0], 't2', 'invalid relation extracted')
        self.assertEqual(jex[0][0][0][1], 'id1', 'invalid column extracted')
        self.assertEqual(jex[0][0][1][1], 'id1', 'invalid column extracted')


if __name__ == '__main__':
    unittest.main()