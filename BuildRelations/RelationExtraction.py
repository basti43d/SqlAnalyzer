import logging
from AnalyzeDB import AnalyzeDB
from .BuildErm import BuildErm, LRel, RRel
from .ColPair import ColPair
from .DBTable import DBTable
from .Querys import Querys
from IPython.display import Image


class RelationExtraction:

    same_instance_identifier='same'
    specialization_identifier='special'
    new_entity_identifier='new'
    weak_entity_identifier='weak'
    regular_relationship_identifier='regular'
    foreign_key_identifier='foreign'
    intersection_identifier = 'intersection'
    
    def __init__(self, connection_string, relations = None):
        self.db = AnalyzeDB(connection_string=connection_string)
        self.__init_tables()
        self.set_relations(relations=relations)
        logging.debug('RelationExtraction Object created successfully')
    
    
    def set_relations(self, relations):
        self.relations = relations
        self.pairs = {}
        self.erm = BuildErm()


    def __init_tables(self):
        self.db.get_tables()
        self.db_tables = {}
        for table in self.db.tables:
            cols, pks = self.db.get_table_desc(table=table)
            #vorerst nur name
            tn = table.split('.')[1]
            self.db_tables[tn] = DBTable(tn, cols, pks)
        logging.debug('initialized all relations from database successfully')
    
    def __get_query_values(self, rel1, cols1, rel2, cols2):
        q1 = Querys.build_query_a(rel1, cols1, rel2, cols2)
        q2 = Querys.build_query_a(rel2, cols2, rel1, cols1)
        q3 = Querys.build_query_b(rel1)
        q4 = Querys.build_query_b(rel2)
        return self.db.execute_scalars([q1, q2, q3, q4])
    
    def aggregate(self):
        for tab in self.relations:
            for ausdr in self.relations[tab]:
                rel1 = ausdr['rels']['left']
                rel2 = ausdr['rels']['right']
                rels = (rel1, rel2) if rel1 < rel2 else (rel2, rel1)
                cols1 = []
                cols2 = []
                for tp in ausdr['cols']:
                    cols1.append(tp['left'])
                    cols2.append(tp['right'])
                if rel2 <= rel1:
                    cols1, cols2 = cols2, cols1
                colp = ColPair(cols1, cols2)
                if rels in self.pairs:
                    if self.pairs[rels] != colp:
                        logging.error(f'error aggregating relations {rel1} and {rel2}, \
                                        columns {colp} do not match with {self.pairs[rels]}')
                else:
                    self.pairs[rels] = colp
                    self.db_tables[rel1].add_pk_cols(cols2, rel2)
                    self.db_tables[rel2].add_pk_cols(cols1, rel1)
    
    
    def print_pairs(self):
        for key in self.pairs:
            print(key)
            print(self.pairs[key])
    
    
    def build_rels(self):
        logging.debug('starting building relations')
        i = 0
        for key in self.pairs:
            i += 1
            rel1 = key[0]
            if rel1 not in self.db_tables:
                logging.error(f'cant find relation {rel1} in DB-Tables')
            rel2 = key[1]
            if rel2 not in self.db_tables:
                logging.error(f'cant find relation {rel2} in DB-Tables')
            cols1 = self.pairs[key].cols1
            cols2 = self.pairs[key].cols2
            if self.db_tables[rel1].is_pk(cols1) == True:
                if self.db_tables[rel2].is_pk(cols2) == True:
                    logging.info(f'{rel1} and {rel2} joined with PKs')
                    self.check_case_PK_to_PK(rel1, cols1, rel2, cols2)
                elif self.db_tables[rel2].is_part_of_pk(cols2) == True:
                    logging.info(f'{rel1} and {rel2} joined with PK and part of PK')
                    self.check_case_PK_to_pPK(rel1, cols1, rel2, cols2)
                else:
                    logging.info(f'{rel1} and {rel2} joined with PK and non part of PK')
                    self.check_case_PK_to_nPK(rel1, cols1, rel2, cols2)
            elif self.db_tables[rel2].is_pk(cols2) == True:
                if self.db_tables[rel1].is_part_of_pk(cols1) == True:
                    logging.info(f'{rel1} and {rel2} joined with part of PK and PK')
                    self.check_case_PK_to_pPK(rel2, cols2, rel1, cols1)
                else:
                    logging.info(f'{rel1} and {rel2} joined with non part of PK and PK')
                    self.check_case_PK_to_nPK(rel2, cols2, rel1, cols1)
            else:
                logging.info(f'{rel1} and {rel2} joined with non PK {cols1} and {cols2}')
                self.check_case_nPK_to_nPK(rel1, cols2, rel2, cols2)
        logging.debug(f'finished interpreting {i} join-expressions')
    

    def check_case_PK_to_PK(self, rel1, cols1, rel2, cols2):
        n = self.__get_query_values(rel1, cols1, rel2, cols2)
        if(n[2] == 0 or n[3] == 0):
            logging.debug(f'{rel1} or {rel2} are empty, no information gained')
            pass
        elif n[0] == n[2] and n[1] == n[3]:
            logging.debug(f'{rel1} and {rel2} have no common values, invalid join')
        elif n[0] == 0 and n[1] == 0:
            logging.debug(f'{rel1} and {rel2} have the same instances')
            self.erm.add_relation((rel1, 
                                   LRel.ONE, 
                                   RRel.ONE, 
                                   rel2, 
                                   RelationExtraction.same_instance_identifier))
        elif n[0] == 0 and n[1] > 0:
            logging.debug(f'{rel1} is a specialisation of {rel2}')
            self.erm.add_relation((rel1, 
                                   LRel.ONE, 
                                   RRel.ZEROORONE, 
                                   rel2, 
                                   RelationExtraction.specialization_identifier))
        elif n[1] == 0 and n[0] > 0:
            logging.debug(f'{rel2} is a specialisation of {rel1}')
            self.erm.add_relation((rel2, 
                                   LRel.ONE, 
                                   RRel.ZEROORONE, 
                                   rel1, 
                                   RelationExtraction.specialization_identifier))
        elif n[0] > 0 and n[1] > 0:
            logging.debug(f'{rel1} and {rel2} have a non empty intersection')
            self.erm.add_relation((rel1, 
                                   LRel.ZEROORMORE, 
                                   RRel.ONE, 
                                   RelationExtraction.new_entity_identifier, 
                                   RelationExtraction.intersection_identifier))
            self.erm.add_relation((rel2, 
                                   LRel.ZEROORMORE, 
                                   RRel.ONE, 
                                   RelationExtraction.new_entity_identifier, 
                                   RelationExtraction.intersection_identifier))


    def check_case_PK_to_pPK(self, rel_pk, cols_pk, rel_ppk, cols_ppk):
        rr = set()
        for i, related_rel in enumerate(self.db_tables[rel_ppk].pk_ref_relations):
            if related_rel == 0:
                nfc = self.db_tables[rel_ppk].pk_columns[i]
                logging.debug(f'no value found for pk-column {nfc} in relation {rel_ppk}, weak entity detected')
                self.erm.add_relation((rel_pk, 
                                       LRel.ZEROORMORE, 
                                       RRel.ONE, 
                                       rel_ppk, 
                                       RelationExtraction.weak_entity_identifier))
                return
            else:
                logging.debug(f'found value for pk_column in {related_rel}')
                rr.add(related_rel)
        related_rels =  ', '.join(rr)
        logging.debug(f'multi-valued relation detected in relation {rel_ppk} with relations {related_rels}')
        for rel in rr:
            self.erm.add_relation((rel, 
                                   LRel.ZEROORMORE, 
                                   RRel.ONE,
                                   rel_ppk,
                                   RelationExtraction.regular_relationship_identifier))



    def check_case_PK_to_nPK(self, rel_pk, cols_pk, rel_npk, cols_npk):
        logging.debug(f'foreign key for {rel_pk} detected in {rel_npk}')
        self.erm.add_relation((rel_pk,
                               LRel.ZEROORMORE,
                               RRel.ONE,
                               rel_npk,
                               RelationExtraction.foreign_key_identifier))


    def check_case_nPK_to_nPK(self, rel1, cols1, rel2, cols2):
        logging.debug(f'join between {rel1} and {rel2} involve no PK')

    def show_erm(self) -> Image:
        self.erm.build_graph()
        return self.erm.get_as_image()
    


                
            

    