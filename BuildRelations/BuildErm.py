import logging
import base64
from IPython.display import Image
from enum import StrEnum

class LRel(StrEnum):
    ZEROORONE = '|o',
    ONE = '||',
    ZEROORMORE = '}o',
    ONEORMORE = '}|'

class RRel(StrEnum):
    ZEROORONE = 'o|',
    ONE = '||',
    ZEROORMORE = 'o{',
    ONEORMORE = '|{',


class BuildErm :

    graph : str
    entitys : list
    relations : list[(str, LRel, RRel, str, str)]
    attributes : list[list[tuple[str, str, str]]]


    def __init__(self):
        self.graph = ''
        self.entities = []
        self.attributes = []
        self.relations = []
        self.entities_set = set()
        self.relations_set = set()
    
    def add_entity_if_not_exists(self, entity : str, attributes : list[tuple[str, str, str]] = []):
        if entity not in self.entities_set:
            self.entities.append(entity)
            self.attributes.append(attributes)
            self.entities_set.add(entity)
    
    def add_relation(self, rel : tuple[str, LRel, RRel, str, str]):
        if rel[0] not in self.entities_set:
            self.add_entity_if_not_exists(rel[0])
        if rel[3] not in self.entities_set:
            self.add_entity_if_not_exists(rel[3])
        rel_ident = rel[0] + '.' + rel[3] if rel[0] < rel[3] else rel[3] + '.' + rel[0]
        if rel_ident in self.relations_set:
            logging.info(f'ignoring relation between {rel[0]} and {rel[3]} because it already exists')
        else:
            self.relations_set.add(rel_ident)
            self.relations.append(rel)
    
    def build_graph(self): 
        self.graph = 'erDiagram\n'
        for i, entity in enumerate(self.entities):
            self.graph += f'\t{entity}' 
            self.graph += ' {\n'
            for attribute in self.attributes[i]:
                self.graph += f'\t\t{attribute[0]} {attribute[1]} {attribute[2]}'
            self.graph += '\n\t}'
            self.graph += '\n'
        for relation in self.relations:
            self.graph += f'\t{relation[0]} {relation[1]}--{relation[2]} {relation[3]} : {relation[4]}'
    
    def get_base64_string(self):
        graphbytes = self.graph.encode('utf8')
        base64_bytes = base64.urlsafe_b64encode(graphbytes)
        base64_string = base64_bytes.decode('ascii')
        return base64_string


    def get_as_image(self) -> Image :
        base64 = self.get_base64_string()
        img = Image(url='https://mermaid.ink/img/' + base64, format='png')
        return img
