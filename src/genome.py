from random import choice, gauss, random, uniform


class Gene(object):
    """
    The Gene is the building block of the Genome. A Gene is a single float inside
    a Genome. It has a set range in which it can vary (with min_value and max_value),
    and it's mutating properties are controlled with the volatility and granularity
    parameters. The values of the Gene are rounded to a set number of digits in order
    to prevent Genomes to be too similar.


    Args:
        name (str): Name of the Gene. Must be unique within a Genome.
        min_value (float): Minimum value of the Gene.
        max_value (float): Maximum value of the Gene.
        volatility (float): The probability the Gene changes when mutating [0, 1].
        granularity (float): The mean change of the Gene when mutating.
        precision (int): The number of digits to round to. Defaults to 4.
    """

    def __init__(self, name, min_value, max_value, volatility, granularity, precision=4):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.volatility = volatility
        self.granularity = granularity
        self.precision = precision

    def initialize(self):
        return round(uniform(self.min_value, self.max_value), self.precision)

    def mutate(self, value):
        if random() < self.volatility:
            round(min(max((value + gauss(0, self.granularity)), self.min_value), self.max_value), self.precision)
        return value


class ListGene(object):
    """
    The ListGene is a variant of the Gene which is not represented by a float, but by an element from a list.

    Args:
        name (str): Name of the Gene. Must be unique within a Genome.
        values (list): Values the Gene can take.
        volatility (float): The probability the Gene changes when mutating [0, 1].
    """

    def __init__(self, name, values, volatility):
        self.name = name
        self.values = values
        self.volatility = volatility

    def initialize(self):
        return choice(self.values)

    def mutate(self, value):
        if random() < self.volatility:
            return choice(self.values)
        return value


class Genome(object):
    """
    A Genome represents a set of Genes. Genomes can be mutated or combined.
    The specifications of the Genes, in the form of Gene or ListGene objects
    go into the specifications class variable.

    Args:
        genes (dict): Dict of all genes.
    """
    specifications = []

    def __init__(self, genes):
        self.genes = genes
        if len(set(self.gene_names)) < len(self.genes):
            raise ValueError('Genome: genes must have unique names.')

    def __eq__(self, other):
        return all((self.genes[name] == other.genes[name] for name in self.gene_names))

    def __getitem__(self, key):
        return self.genes[key]

    def __hash__(self):
        return hash(tuple(self[name] for name in self.gene_names))

    @classmethod
    def create(cls):
        genes = {s.name: s.initialize() for s in cls.specifications}
        return cls(genes)

    @property
    def gene_names(self):
        return sorted([g.name for g in self.specifications])

    def combine(self, other):
        """
        Create a new Genome which is a combination of this and another Genome.

        Args:
            other (Genome): The genome to combine with.

        Returns:
            Genome: A new genome object with a mixture of genes. """
        return self.__class__({name: choice((self.genes[name], other.genes[name])) for name in self.gene_names})

    def mutate(self):
        """
        Mutate the Genome.

        Returns:
            Genome: A new genome with slightly modified genes.
        """
        return self.__class__({s.name: s.mutate(self[s.name]) for s in self.specifications})
