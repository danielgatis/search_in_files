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

def find(q, paths, l):
    l.append(filter(partial(contains, q), paths))

def search6(q, path):
    manager = multiprocessing.Manager()
    l = manager.list()

    workers = []
    cpu_count = multiprocessing.cpu_count()
    paths = list(map(lambda x: x.path, list(os.scandir(path))))
    group_size = int(len(paths) / cpu_count)
   

    for i, paths in enumerate(chunks(paths, group_size)):
        p = multiprocessing.Process(target=find, args=(q, paths, l))
        p.daemon = True
        p.start()    
        workers.append(p)

    for p in workers:
        p.join()

    matches = flatten(l)
        
    matches.sort()
    return matches
    
if __name__ == '__main__': 
    r = search6('walt disney', 'data') 
    print(r)
    print(len(r))