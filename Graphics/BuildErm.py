import base64
import mermaid as md
from mermaid.graph import Graph
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
        self.entitys = []
        self.attributes = []
        self.relations = []
    
    def entity_exists(self, entity: str):
        return True if entity in self.entitys else False
    
    def add_relation(self, rel : tuple[str, LRel, RRel, str, str]):
        if not self.entity_exists(rel[0]):
                raise Exception(f"{rel[0]} not in Entitys")
        if not self.entity_exists(rel[3]):
            raise Exception(f"{rel[3]} not in Entitys")
        dup = [t for t in self.relations if t[0] == rel[0] and t[3] == rel[3]]
        if len(dup) > 0:
            raise Exception(f"relation between {rel[0]} and {rel[3]} already exists")
        self.relations.append(rel)
    
    def add_entity(self, entity : str, attributes : list[tuple[str, str, str]] = []):
        if self.entity_exists(entity):
            raise Exception(f"entity {entity} already exists")
        self.entitys.append(entity)
        self.attributes.append(attributes)
    
    def build_graph(self): 
        self.graph = 'erDiagram\n'
        for i, entity in enumerate(self.entitys):
            self.graph += f'\t{entity}' 
            self.graph += ' {\n'
            for attribute in self.attributes[i]:
                self.graph += f'\t\t{attribute[0]} {attribute[1]} {attribute[2]}'
            self.graph += '\t\n}'
        for relation in self.relations:
            self.graph += f'{relation[0]} {relation[1]}--{relation[2]} {relation[3]} : {relation[4]}'


    def get_as_image(self) -> Image :
        graphbytes = self.graph.encode('utf8')
        base64_bytes = base64.urlsafe_b64encode(graphbytes)
        base64_string = base64_bytes.decode('ascii')
        img = Image(url='https://mermaid.ink/img/' + base64_string)
        return img