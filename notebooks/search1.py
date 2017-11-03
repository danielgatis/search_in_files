from functools import partial
import os

def contains(q, path):
    with(open(path)) as f:
        for line in f:
            if q in line:
                return True
        return False

def search1(q, path):
    r = list(filter(partial(contains, q), map(lambda x: x.path, os.scandir(path))))
    r.sort()
    return r

if __name__ == '__main__':
    r = search1('walt disney', 'data') 
    print(r)
    print(len(r))