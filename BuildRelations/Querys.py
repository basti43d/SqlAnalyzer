import logging

class Querys:
        query_a = """
            select count(*) 
            from (
                select cols1
                from rel1
                except
                select cols2
                from rel2
            ) t
        """

        query_b = """
            select count(*)
            from rel1
        """

        query3 = """
        """

        def build_query_a(rel1, cols1, rel2, cols2):
            logging.debug(f'creating query_a for relations {rel1} and {rel2}')
            return Querys.query_a.replace('rel1', rel1) \
                                .replace('rel2', rel2) \
                                .replace('cols1', ', '.join(cols1)) \
                                .replace('cols2', ', '.join(cols2))

        def build_query_b(rel):
            logging.debug(f'creating query_b for relation {rel}')
            return Querys.query_b.replace('rel1', rel)

        def build_query_c(rel):
            logging.debug(f'created query_c for relation {rel}')
            pass