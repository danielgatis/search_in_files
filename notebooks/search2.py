import os
import threading
from queue import Queue

queue = Queue()
results = []

def contains(q, path):
    with(open(path)) as f:
        for line in f:
            if q in line:
                return True
        return False

def process_queue():
    while True:
        path, q = queue.get()

        if contains(q, path):
            results.append(path)

        queue.task_done()

def search2(q, path):
    for i in range(2):
        t = threading.Thread(target=process_queue)
        t.daemon = True
        t.start()

    for file in os.scandir(path):
        queue.put((file.path, q))

    queue.join()
    results.sort()

    return results

if __name__ == '__main__':
    r = search2('walt disney', 'data')
    print(r)
    print(len(r))
