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

class region (object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'Region({r})'.format(r=self.name)
    def continent(self):
        global continents
        for c, regions in continents.items():
            if self.name in regions: return c
        raise Exception('no continent defined for region {r}'.format(r=self.name))
    def neighbors(self):
        global graph
        return graph[self.name]
    
def regions():
    global graph
    return [region(r) for r in graph.keys()]