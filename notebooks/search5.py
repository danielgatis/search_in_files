import multiprocessing
import os
import tempfile
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

def find(q, paths, tem_path):
    with(open(tem_path, 'a')) as f:
        for path in filter(partial(contains, q), paths):
            f.write('{}\n'.format(path))

def search5(q, path):
    workers = []
    cpu_count = multiprocessing.cpu_count()
    paths = list(map(lambda x: x.path, list(os.scandir(path))))
    group_size = int(len(paths) / cpu_count)
    results = []

    for i, paths in enumerate(chunks(paths, group_size)):
        temp_name = next(tempfile._get_candidate_names())
        temp_dir = tempfile._get_default_tempdir()
        tem_path = os.path.join(temp_dir, temp_name)

        results.append(tem_path)

        p = multiprocessing.Process(target=find, args=(q, paths, tem_path))
        p.daemon = True
        p.start()    
        workers.append(p)

    for p in workers:
        p.join()

    matches = []

    while len(results) > 0:
        r = results[0]
        if not os.path.isfile(r):
            continue

        with(open(r)) as f:
            matches = matches + f.readlines()
        
        results.pop(0)
        
    matches.sort()
    return matches
    
if __name__ == '__main__': 
    r = search5('walt disney', 'data') 
    print(r)
    print(len(r))
