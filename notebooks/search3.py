import multiprocessing 
from functools import partial
import os

def flatten(l): 
    return [item for sublist in l for item in sublist]

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def contains(q, path):
    with(open(path)) as f:
        for line in f:
            if q in line:
                return True
        return False

def find(q, paths):
    return filter(partial(contains, q), paths)

def search3(q, path):    
    cpu_count = multiprocessing.cpu_count()
    paths = list(map(lambda x: x.path, list(os.scandir(path))))
    group_size = int(len(paths) / cpu_count)

    p = multiprocessing.Pool(cpu_count)
    r = p.map(partial(find, q), chunks(paths, group_size))
    matches = flatten(r)

    matches.sort()
    return matches
    
if __name__ == '__main__': 
    r = search3('walt disney', 'data') 
    print(r)
    print(len(r))