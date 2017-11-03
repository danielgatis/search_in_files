import multiprocessing 
from functools import partial
import os

def flatten(l): 
    return [item for sublist in l for item in sublist]

def groups(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def contains(q, path):
    with(open(path)) as f:
        for line in f:
            if q in line:
                return True
        return False

def find(q, idx_paths, array):
    for i, path in idx_paths:
        array[i] = int(contains(q, path))  

def search7(q, path):
    cpu_count = multiprocessing.cpu_count()
    idx_paths = list(map(lambda x: (x[0], x[1].path), enumerate(os.scandir(path))))
    
    array = multiprocessing.Array('i', len(idx_paths), lock=False)
    group_size = int(len(idx_paths) / cpu_count)
   
    workers = []
    
    for paths in groups(idx_paths, group_size):
        p = multiprocessing.Process(target=find, args=(q, paths, array))
        p.daemon = True
        p.start()    
        workers.append(p)

    for p in workers:
        p.join()

    matches = [idx_paths[i][1] for i, match in enumerate(array) if match]
    matches.sort()

    return matches
    
if __name__ == '__main__': 
    r = search7('walt disney', 'data') 
    print(r)
    print(len(r))