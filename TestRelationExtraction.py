import unittest
from QueryDissolve.Dissolver import Dissolver
from BuildRelations.RelationExtraction import RelationExtraction

from BuildRelations.BuildErm import LRel, RRel

db_connection_string = 'DRIVER={ODBC Driver 18 for SQL Server};Server=(localdb)\MSSQLLocalDb;database=testDb;'
path = 'c:\\users\\basti\\Desktop\\ba\\test_querys\\relations\\asts\\'

def setup(ast):
    res = Dissolver()
    res.load_single(ast)
    rels = res.get_dissolved()
    relex = RelationExtraction(relations=rels, connection_string=db_connection_string)
    relex.aggregate()
    relex.build_rels()
    return relex.erm.entities, relex.erm.relations

def compare_relations(rel, rel1, lrel, rrel, rel2, name):
    if rel[0] != rel1:
        if rel[1] != rel1:
            return False
        rel1, rel2 = rel2, rel1
        lrel, rrel = rrel, lrel
    if rel[0] != rel1:
        return False
    if rel[1] != lrel:
        return False
    if rel[2] != rrel:
        return False
    if rel[3] != rel2:
        return False
    if rel[4] != name:
        return False
    return True
    

class TestRelationExtraction(unittest.TestCase):

    #t5 = t8
    def test_same_entity_type(self):
        attr, rels = setup(path + 'q1.json')
        self.assertEqual(len(attr), 2, 'invalid number of entity types')
        self.assertTrue('t5' in attr, 'missing entity type')
        self.assertTrue('t8' in attr, 'missing entity type')
        self.assertEqual(len(rels), 1, 'invalid number of relations')
        self.assertTrue(
            compare_relations(rels[0], 't5', LRel.ONE, RRel.ONE, 't8', RelationExtraction.same_instance_identifier),
            'invalid relation'
        )

    #t8 intersect t9
    def test_new_entity_type(self):
        attr, rels = setup(path + 'q2.json')
        self.assertEqual(len(attr), 3, 'invalid number of entity types')
        self.assertTrue('t8' in attr, 'missing entity type')
        self.assertTrue('t9' in attr, 'missing entity type')
        self.assertTrue(RelationExtraction.new_entity_identifier in attr, 'missing entity type')
        self.assertEqual(len(rels), 2, 'invalid number of relations')
        rel1 = rels[0] if 't8' in rels[0] else rels[1]
        self.assertTrue(
            compare_relations(rel1, 't8', LRel.ZEROORMORE, RRel.ONE, RelationExtraction.new_entity_identifier, RelationExtraction.intersection_identifier),
            'invalid relation'
        )
        rel2 = rels[0] if 't9' in rels[0] else rels[1]
        self.assertTrue(
            compare_relations(rel2, 't9', LRel.ZEROORMORE, RRel.ONE, RelationExtraction.new_entity_identifier, RelationExtraction.intersection_identifier),
            'invalid relation'
        )

    #t7 < t5
    def test_specialization(self):
        attr, rels = setup(path + 'q3.json')
        self.assertEqual(len(attr), 2, 'invalid number of entity types')
        self.assertTrue('t7' in attr, 'missing entity type')
        self.assertTrue('t5' in attr, 'missing entity type')
        self.assertEqual(len(rels), 1, 'invalid number of relations')
        self.assertTrue(
            compare_relations(rels[0], 't7', LRel.ONE, RRel.ZEROORONE, 't5', RelationExtraction.specialization_identifier),
            'invalid relation'
        )


    #t1.id = t2.c
    def test_fk(self):
        attr, rels = setup(path + 'q4.json')
        self.assertEqual(len(attr), 2, 'invalid number of entity types')
        self.assertTrue('t1' in attr, 'missing entity type')
        self.assertTrue('t2' in attr, 'missing entity type')
        self.assertEqual(len(rels), 1, 'invalid number of relations')
        self.assertTrue(
            compare_relations(rels[0], 't1', LRel.ZEROORMORE, RRel.ONE, 't2', RelationExtraction.foreign_key_identifier),
            'invalid relation'
        )

    #t1, t7
    def no_intersection(self):
        attr, rels = setup(path + 'q5.json')
        self.assertEqual(len(attr), 0, 'invalid number of entity types')
        self.assertEqual(len(rels), 0, 'invalid number of relations')

    #t3, t4
    def test_empty(self):
        attr, rels = setup(path + 'q6.json')
        self.assertEqual(len(attr), 0, 'invalid number of entity types')
        self.assertEqual(len(rels), 0, 'invalid number of relations')
        
    #t6 < t2
    def test_weak_entity(self):
        attr, rels = setup(path + 'q7.json')
        self.assertEqual(len(attr), 2, 'invalid number of entity types')
        self.assertTrue('t6' in attr, 'missing entity type')
        self.assertTrue('t2' in attr, 'missing entity type')
        self.assertEqual(len(rels), 1, 'invalid number of relations')
        self.assertTrue(
            compare_relations(rels[0], 't2', LRel.ZEROORMORE, RRel.ONE, 't6', RelationExtraction.weak_entity_identifier),
            'invalid relation'
        )
    
    #t10.id_t8, t10.id_t9
    def test_regual_relationship(self):
        res = Dissolver()
        res.load_files([path + 'q8.json', path + 'q9.json'])
        rels = res.get_dissolved()
        relex = RelationExtraction(relations=rels, connection_string=db_connection_string)
        relex.aggregate()
        relex.build_rels()
        attr = relex.erm.entities
        rels = relex.erm.relations
        self.assertEqual(len(attr), 3, 'invalid number of entity types')
        self.assertTrue('t8' in attr, 'missing entity type')
        self.assertTrue('t9' in attr, 'missing entity type')
        self.assertTrue('t10' in attr, 'missing entity type')
        self.assertEqual(len(rels), 2, 'invalid number of relations')
        rel1 = rels[0] if 't9' in rels[0] else rels[1]
        self.assertTrue(
            compare_relations(rel1, 't9', LRel.ZEROORMORE, RRel.ONE, 't10', RelationExtraction.regular_relationship_identifier),
            'invalid relation'
        )
        rel2 = rels[0] if 't8' in rels[0] else rels[1]
        self.assertTrue(
            compare_relations(rel2, 't8', LRel.ZEROORMORE, RRel.ONE, 't10', RelationExtraction.regular_relationship_identifier),
            'invalid relation'
        )


if __name__ == '__main__': 
    unittest.main()