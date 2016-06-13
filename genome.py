import random

# Gene examples
# {'name': 'bool',  'dtype': bool, 'volatility': 0.5}
# {'name': 'int',   'dtype': int, 'min_value': 0, 'max_value': 10, 'volatility': 0.1}
# {'name': 'float', 'dtype': float, 'min_value': 0, 'max_value': 2.5, 'volatility': 0.1, 'granularity': 0.5, 'digits': 4}
# {'name': 'list',  'dtype': list, 'values': [0, 2, 4], 'volatility': 0.1}

class Genome (object):
    """ The Genome is a base class for a genome for a genetic algorithm.
    
        The inheriting class is expected to defined the class variable `specifications`.
        This variable should be an iterable (tuple) containing a dictionary for each gene
        the genome has. Genes can have one of four dtypes: bool, int, float, list. The 
        specification dictionaries for these types are:
        - bool: {'dtype': bool, 'name': '{name}', 'volatility': {volatility}}
        - int: {'dtype': int, 'name': '{name}', 'volatility': {volatility}, 'min_value': {min}, 'max_value': {max}}
        - float: {'dtype': float, 'name': '{name}', 'volatility': {volatility}, 
                  'min_value': {min}, 'max_value': {max}, 'granularity': {g}, 'digits': {d}}
        - list: {'dtype': list, 'name': '{name}', 'volatility': {volatility}, 'values': [values]}
        The keys are:
        - dtype: the dtype of the gene,
        - name (str): the name of the gene,
        - volatility (float in [0, 1]): the likelihood of the gene to mutate,
        - min_value (int/float): the minimum allowed value of the gene,
        - max_value (int/float): the maximum allowed value of the gene,
        - granularity (float): the order of magnitude for mutations,
        - digits (int): the number of significant digits,
        - values (list): the allowed values for the gene. 
        
        Genomes can be created using the create method, which will randomly initialize the genes. """
        
    def __init__(self, genes={}):
        assert set(genes.keys()) == set(self.gene_names), '{cls}: gene definitions do not match'
        self.genes = genes
        

    @classmethod
    def create(cls):
        """ Create a Genome. 
        
            Returns:
                Genome: a randomly initialized genome. """
        return cls(genes={
            spec['name']: cls.initialize(**spec) for spec in cls.specifications
        })    
    
    @classmethod
    def from_dict(cls, genes):
        """ Create a genome from a dict.
        
            Returns:
                Genome: a genome initialized from a dict. """
        return cls(genes={
            spec['name']: (genes[spec['name']] if spec['name'] in genes else cls.initialize(**spec))
                for spec in cls.specifications     
        })
    
    def __repr__(self):
        return '{cls}({val})'.format(
            cls=self.__class__.__name__, 
            val=', '.join('{0}={1}'.format(name, g) for name, g in self.genes.items()))
    
    def __eq__(self, other):
        return all((self.genes[name] == other.genes[name] for name in self.gene_names))  

    def __hash__(self):
        return hash(tuple(self.genes[name] for name in self.gene_names))  
    
    def __getitem__(self, key):
        return self.genes[key]



    def combine(self, other):
        """ Combine with another Genome.
        
            Args:
                other (Genome): the genome to combine with.
                
            Returns:
                Genome: a new genome object with a mixture of genes. """
        return self.__class__({
            name: random.choice((self.genes[name], other.genes[name])) for name in self.genes.keys()
        })

    def mutate(self):
        """ Mutate the Genome.
        
            Returns:
                Genome: a new genome with slightly modified genes. """
        return self.__class__({
            spec['name']: self.mutate_gene(**spec) for spec in self.specifications
        })    
    
    @staticmethod
    def initialize(name, dtype, volatility, **kwargs):
        """ Initialize a gene according to a specification. """
        if dtype is bool:
            return random.choice((False, True))
        elif dtype is list:
            return random.choice(kwargs['values'])
        elif dtype is int:
            return random.randint(kwargs['min_value'], kwargs['max_value'])
        elif dtype is float:
            return round(random.uniform(kwargs['min_value'], kwargs['max_value']), kwargs['digits'])
        raise Exception('Genome.initialize: unknown gene type: {t}'.format(t=dtype))    

    @property
    def gene_names(self):
        """ Returns an iterator over all gene names in the specification. """
        return (spec['name'] for spec in self.specifications)        
        
    def mutate_gene(self, name, dtype, volatility, **kwargs):
        """ Mutate a gene according to a specification. """
        value = self.genes[name]
        if random.random() < volatility:
            if dtype is bool:
                return not value
            elif dtype is list:
                return random.choice(kwargs['values'])
            elif dtype is int:
                return self.mutate_int(value, **kwargs)
            elif dtype is float:
                return self.mutate_float(value, **kwargs)
        return value

    @staticmethod
    def mutate_int(value, min_value, max_value):
        """ Mutate a gene of type int within its limits. """
        if value == min_value:
            return value + 1
        elif value == max_value:
            return value - 1
        return value + random.choice((-1, +1))
         
    @staticmethod
    def mutate_float(value, min_value, max_value, granularity, digits):
        """ Mutate a gene of type float according to a specification. """
        return round(min(max((value + random.gauss(0, granularity)), min_value), max_value), digits) 