# import socket
# import traceback
import sys

# oldsocket = socket.socket

# class newsocket(oldsocket):
#     def __init__(self, *args, **kwargs):
#         print("### OPENING SOCKET ### <<<")
#         # traceback.print_stack(file=sys.stdout)
#         print()
#         super().__init__(*args, **kwargs)
        
#     def close(self, *args, **kwargs):
#         print("### CLOSING SOCKET ### >>>")
#         super().close(*args, **kwargs)
        
# socket.socket = newsocket
    
    
from rdflib import Graph, URIRef
from rdflib.plugins.stores import sparqlstore

endpoint = "http://localhost:5820/dbpedia/query"
store = sparqlstore.SPARQLUpdateStore()
store.open(endpoint)

ng = Graph(store, URIRef("http://pt.dbpedia.org"))

def valid_neighbour(obj):
    if not isinstance(obj, URIRef):
        return False
    
    # uri = str(obj)
    # if (not uri.startswith("http://pt.dbpedia.org/resource/") and
    #         not uri.startswith("http://dbpedia.org/ontology/")):
    #     return False
    
    # if uri.startswith("http://pt.dbpedia.org/resource/"):
    #     title = uri[31:]
    #     if ":" in title and not title.startswith("Categoria:"):
    #         return False
    
    return True

def get_neighbours(uriref):
    try:
        n3 = uriref.n3()
    except Exception:
        return set()
    
    query = "SELECT ?o WHERE {{ {} ?p ?o }}".format(n3)
    return {o for o, in ng.query(query) if valid_neighbour(o)}

def get_neighbourhood(uriref, max_distance):
    emitted = False
    
    prev_layer = {uriref}
    all_obj = {uriref}
    for i in range(max_distance):
        next_layer = set()
        
        for obj in prev_layer:
            n = get_neighbours(obj).difference(all_obj)
            next_layer.update(n)
            all_obj.update(n)
            
            for obj in n:
                if not emitted:
                    yield (0, uriref)
                    emitted = True
                yield (i + 1, obj)
        
        prev_layer = next_layer

def normalize_word(word):
    return word[0].upper() + word[1:]

if __name__ == "__main__":
    MAX_DISTANCE = 3
    cache = {}
    
    line_template = "{} -- {}\n"
    
    def get_index(key, cache_handler):
        index = cache.get(key, None)
        if index is None:
            cache[key] = index = len(cache)
            cache_handler.write(line_template.format(index, key))
        return index
    
    with open("test_words.txt") as f:
        words = {normalize_word(line.rstrip("\n")) for line in f if line.rstrip("\n")}
    
    with open("train_words.txt") as f:
        words.update(normalize_word(line.rstrip("\n")) for line in f if line.rstrip("\n"))
    
    with open("words.vec", "w") as result, open("words.cache", "w") as cache_handler:
        for word in sorted(words):
            uriref = URIRef("http://pt.dbpedia.org/resource/" + word)
            
            vec = {}
            for dist, neighbour in get_neighbourhood(uriref, MAX_DISTANCE):
                index = get_index(str(neighbour), cache_handler)
                vec[index] = 0.5 ** dist
            vec = ["{}:{}".format(index, val) for index, val in sorted(vec.items())]
            if vec:
                line = line_template.format(word, " ".join(vec))
                result.write(line)
