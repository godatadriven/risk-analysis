import os, random, math, copy
import matplotlib.pyplot as plt

graph = {
    # North America
    'alaska': ['northwest-territory', 'alberta', 'kamchatka'],
    'alberta': ['alaska', 'northwest-territory', 'ontario', 'western-united-states'],
    'central-america': ['western-united-states', 'eastern-united-states', 'venezuela'],
    'eastern-united-states': ['central-america', 'western-united-states', 'ontario', 'quebec'],
    'greenland': ['northwest-territory', 'ontario', 'quebec', 'iceland'],
    'northwest-territory': ['alaska', 'alberta', 'greenland', 'ontario'],
    'ontario': ['alberta', 'eastern-united-states', 'greenland', 'northwest-territory', 'quebec', 'western-united-states'],
    'quebec': ['eastern-united-states', 'greenland', 'ontario'],
    'western-united-states': ['alberta', 'central-america', 'eastern-united-states', 'ontario'],
    # South America
    'argentina': ['brazil', 'peru'],
    'brazil': ['north-africa', 'argentina', 'peru', 'venezuela'],
    'peru': ['brazil', 'venezuela', 'argentina'],
    'venezuela': ['peru', 'brazil', 'central-america'],
    # Europe
    'great-britain': ['iceland', 'northern-europe', 'scandinavia', 'western-europe'],
    'iceland': ['greenland', 'great-britain', 'scandinavia'],
    'northern-europe': ['scandinavia', 'ukraine', 'southern-europe', 'western-europe', 'great-britain'],
    'scandinavia': ['ukraine', 'northern-europe', 'great-britain', 'iceland'],
    'southern-europe': ['egypt', 'western-europe', 'northern-europe', 'ukraine', 'middle-east'],
    'ukraine': ['ural', 'afghanistan', 'middle-east', 'southern-europe', 'northern-europe', 'scandinavia'],
    'western-europe': ['great-britain', 'north-africa', 'southern-europe', 'northern-europe'],
    # Africa
    'congo': ['east-africa', 'south-africa', 'north-africa'],
    'east-africa': ['egypt', 'middle-east', 'madagascar', 'south-africa', 'congo', 'north-africa'],
    'egypt': ['southern-europe', 'middle-east', 'east-africa', 'north-africa'],
    'madagascar': ['east-africa', 'south-africa'],
    'north-africa': ['western-europe', 'egypt', 'east-africa', 'congo', 'brazil'],
    'south-africa': ['congo', 'east-africa', 'madagascar'],
    # Asia
    'afghanistan': ['ukraine', 'ural', 'china', 'india', 'middle-east'],
    'china': ['siam', 'india', 'afghanistan', 'siberia', 'ural', 'mongolia'],
    'india': ['china', 'siam', 'middle-east', 'afghanistan'],
    'irkutsk': ['yakutsk', 'mongolia', 'siberia', 'kamchatka'],
    'japan': ['kamchatka', 'mongolia'],
    'kamchatka': ['japan', 'alaska', 'irkutsk', 'mongolia', 'yakutsk'],
    'middle-east': ['east-africa', 'egypt', 'ukraine', 'afghanistan', 'india', 'southern-europe'],
    'mongolia': ['japan', 'china', 'siberia', 'irkutsk', 'kamchatka'],
    'siam': ['indonesia', 'india', 'china'],
    'siberia': ['irkutsk', 'yakutsk', 'mongolia', 'china', 'ural'],
    'ural': ['siberia', 'china', 'afghanistan', 'ukraine'],
    'yakutsk': ['kamchatka', 'irkutsk', 'siberia'],
    # Oceania,
    'eastern-australia': ['new-guinea', 'western-australia'],
    'indonesia': ['siam', 'new-guinea', 'western-australia'],
    'new-guinea': ['eastern-australia', 'indonesia', 'western-australia'],
    'western-australia': ['eastern-australia', 'indonesia', 'new-guinea']
}
continents = {
    'north-america': ['alaska', 'alberta', 'central-america', 'eastern-united-states', 
                      'greenland', 'northwest-territory', 'ontario', 'quebec', 'western-united-states'],
    'south-america': ['argentina', 'brazil', 'peru', 'venezuela'],
    'europe': ['great-britain', 'iceland', 'northern-europe', 'scandinavia', 'southern-europe', 
               'ukraine', 'western-europe'],
    'africa': ['congo', 'east-africa', 'egypt', 'madagascar', 'north-africa', 'south-africa'],
    'asia': ['afghanistan', 'china', 'india', 'irkutsk', 'japan', 'kamchatka', 'middle-east', 
             'mongolia', 'siam', 'siberia', 'ural', 'yakutsk'],
    'oceania': ['eastern-australia', 'indonesia', 'new-guinea', 'western-australia']
}
continent_bonus = {
    'north-america': 5,
    'south-america': 2,
    'europe': 5,
    'africa': 3,
    'asia': 7,
    'oceania': 2
}

locations = { 
    'kamchatka': [1510, 150],
    'yakutsk': [1390, 135],
    'siberia': [1260, 200],
    'ural': [1170, 270],
    'irkutsk': [1360, 280],
    'mongolia': [1360, 395],
    'japan': [1530, 395],
    'china': [1330, 510],
    'afghanistan': [1140, 430],
    'india': [1225, 580],
    'siam': [1355, 630],
    'middle-east': [1050, 560],
    
    'eastern-australia': [1540, 920],
    'indonesia': [1355, 800],
    'new-guinea':  [1500, 760],
    'western-australia': [1445, 970],
    
    'madagascar': [1060, 970],
    'south-africa': [930, 960],
    'congo': [910, 830],
    'east-africa': [985, 750],
    'north-africa': [805, 683],
    'egypt': [910, 640],
    
    'ukraine': [1010, 290],
    'scandinavia': [880, 200],
    'southern-europe': [860, 470],
    'northern-europe': [855, 385],
    
    'venezuela': [430, 630],
    'alaska': [135, 180],
    'northwest-territory': [300, 180],
    'alberta': [270, 260],
    'central-america' : [270, 500],
    'ontario' : [390, 280],
    'greenland' : [600, 120],
    'quebec' : [500, 290],
    'eastern-united-states' : [400, 420],
    'western-united-states' : [280, 400],
    'brazil' : [550, 730],
    'peru' : [450, 770],
    'argentina' : [470, 890],
    'iceland' : [740, 230],
    'great-britain' : [700, 350],
    'western-europe' : [720, 540]
}

class Region (object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'Region({r})'.format(r=self.name)
    def continent(self):
        global continents
        for c, regions in continents.items():
            if self.name in regions: return c
        raise Exception('no continent defined for region {r}'.format(r=self.name))
    def location(self):
        global locations
        return locations[self.name]
    def neighbors(self):
        global graph
        return graph[self.name]
    
class Allocation (object):
    all_regions = set([Region(r) for r in graph.keys()])
    def __init__(self, regions=[]):
        if isinstance(regions, int):
            self.sample(n=regions)
        elif isinstance(regions, Allocation):
            self.regions = copy.copy(regions.regions)
        else:
            self.regions = set(regions)
    
    def __repr__(self):
        return 'Allocation({s})'.format(s=self.regions)
    
    def __size__(self):
        return len(self.regions)
    
    def contains(self, region):
        return region in self.regions
    
    def opposite(self):
        return Allocation(self.all_regions.difference(self.regions))
    
    def sample(self, n=21):
        self.regions = set(random.sample(self.all_regions, n))
        
    def choose(self, opposite=False):
        sample = self.opposite() if opposite else self
        return random.choice(list(sample.regions))
    
    def swap(self):
        added = self.choose(opposite=True)
        removed = self.choose()
        self.regions.remove(removed)
        self.regions.add(added)
    
    def new_armies(self):
        global continent_bonus
        retval = max(3, int(math.floor(len(self.regions)/3)))
        for continent in self.full_continents():
            retval += continent_bonus[continent]
        return retval
    
    def full_continents(self):
        global continents
        retval = [ ]
        for continent, regions in continents.items():
            n_regions = len(regions)
            n_my_regions = len([r for r in self.regions if r.continent() == continent])
            if n_regions == (n_my_regions):
                retval.append(continent)
        return retval
    
    def safe_nodes(self):
        retval = 0
        for r in self.regions:
            safe = True
            for n in r.neighbors():
                if not n in [x.name for x in self.regions]:
                    safe = False
                    break
            retval += safe
        return retval
    
    def safe_ratio(self):
        return float(self.safe_nodes()) / (self.opposite().safe_nodes() + 1)
    def safe_difference(self):
        return self.safe_nodes() - self.opposite().safe_nodes()
    def new_difference(self):
        return self.new_armies() - self.opposite().new_armies()


    
    def plot(self, color='black'):
        im = plt.imread(os.getcwd() + '/risk.png')
        plt.figure(figsize = (10,15))
        implot = plt.imshow(im)
        for r in self.regions:
            coor = r.location()
            plt.scatter([coor[0]], [coor[1]], s = 150, c=color)
        plt.show()  
        