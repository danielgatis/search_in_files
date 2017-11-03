import os
from multiprocessing import Process, Queue, Array, cpu_count


def contains(q, path):
    with(open(path)) as f:
        for line in f:
            if q in line:
                return True
        return False


def work(id, q, jobs, array):
    while True:        
        job = jobs.get()
        
        if job is None:
            break
        
        idx, path = job

        if contains(q, path):
            array[idx] = 1
        

def search9(q, path):
    jobs = Queue()
    NUMBER_OF_PROCESSES = cpu_count()
    
    paths = []
    job_count = 0
    for idx, f in enumerate(os.scandir('data')):
        paths.append(f.path)
        jobs.put((idx, f.path))
        job_count = job_count + 1

    array = Array('i', job_count, lock=False)
    workers = []

    for i in range(NUMBER_OF_PROCESSES):
        w = Process(target=work, args=(i, q, jobs, array))
        w.daemon = True
        w.start()    
        workers.append(w)
      
    for w in range(NUMBER_OF_PROCESSES):
        jobs.put(None)

    for w in workers:
        w.join()

    matches = [paths[i] for i, match in enumerate(array) if match]
    matches.sort()
 
    jobs.close()
    
    return matches

if __name__ == '__main__': 
    r = search9('walt disney', 'data') 
    print(r)
    print(len(r))