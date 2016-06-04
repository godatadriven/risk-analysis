import random
# Gene examples
# (bool, None, volatility)
# (list, (values), volatility)
# (int, (min, max), volatility)
# (float, (min, max, granularity), volatility)

class Genome (object):    
    specifications = ( )
       
    def __init__(self, genes):
        self.genes = tuple(genes)
        
    @classmethod
    def create(cls):
        return cls(cls.initialize(*spec) for name, spec in cls.specifications)
    
    def to_dict(self):
        return {name: val for (name, spec), val in zip(self.specifications, self.genes)}
    
    def combine(self, genome):
        return self.__class__(
            random.choice((ours, theirs)) for ours, theirs in zip(self.genes, genome.genes)
        )
    
    def mutate(self):
        return self.__class__(
            self.mutate_gene(val, *spec) for (name, spec), val in zip(self.specifications, self.genes)
        )
                              
    def mutate_gene(self, val, gene_type, gene_range, volatility):
        if random.random() < volatility:
            if gene_type is bool:
                return not val
            elif gene_type is list:
                return random.choice(gene_range)
            elif gene_type is int:
                return self.mutate_int(val, *gene_range)
            elif gene_type is float:
                return self.mutate_float(val, *gene_range)
        return val
    
    @staticmethod
    def initialize(gene_type, gene_range, volatility):
        if gene_type is bool:
            return random.choice((False, True))
        elif gene_type is list:
            return random.choice(gene_range)
        elif gene_type is int:
            return random.randint(*gene_range)
        elif gene_type is float:
            return random.uniform(*gene_range[:2])
        raise Exception('Genome.initialize: unknown gene type: {t}'.format(t=gene_type))
        
    @staticmethod
    def mutate_int(val, gene_min, gene_max):
        if val == gene_min:
            return val + 1
        elif val == gene_max:
            return val - 1
        return val + random.choice((-1, +1))
         
    @staticmethod
    def mutate_float(val, gene_min, gene_max, gene_granularity):
        return min(max((val + random.gauss(0, gene_granularity)), gene_min), gene_max)