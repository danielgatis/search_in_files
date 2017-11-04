import multiprocessing
import os
from functools import partial


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

def find(q, paths, queue):
    queue.put(filter(partial(contains, q), paths))

def search4(q, path):
    workers = []
    matches = []
    queue = multiprocessing.Queue()    
    cpu_count = multiprocessing.cpu_count()
    paths = list(map(lambda x: x.path, list(os.scandir(path))))
    group_size = int(len(paths) / cpu_count)
    
    for paths in chunks(paths, group_size):
        p = multiprocessing.Process(target=find, args=(q, paths, queue))
        p.daemon = True
        p.start()
        workers.append(p)
       
    while True:
        matches.append(queue.get())
        if len(matches) == len(workers):
            break
    
    matches = flatten(matches)

    matches.sort()
    return matches
    
if __name__ == '__main__': 
    r = search4('walt disney', 'data') 
    print(r)
    print(len(r))
