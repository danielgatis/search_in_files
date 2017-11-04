import os
from multiprocessing import JoinableQueue, Process, Queue, cpu_count


def contains(q, path):
    with(open(path)) as f:
        for line in f:
            if q in line:
                return True
        return False


def work(id, q, jobs, result):
    while True:
        path = jobs.get()

        if path is None:
            break

        if contains(q, path):
            result.put(path)
        else:
            result.put(None)

def search8(q, path):
    jobs = Queue()
    result = JoinableQueue()
    NUMBER_OF_PROCESSES = cpu_count()

    job_count = 0
    for f in os.scandir('data'):
        jobs.put(f.path)
        job_count = job_count + 1

    [Process(target=work, args=(i, q, jobs, result)).start() for i in range(NUMBER_OF_PROCESSES)]

    matches = []
    for t in range(job_count):
        r = result.get()
        result.task_done()
        if r:
            matches.append(r)

    matches.sort()

    for w in range(NUMBER_OF_PROCESSES):
        jobs.put(None)

    result.join()
    jobs.close()
    result.close()

    return matches

if __name__ == '__main__':
    r = search8('walt disney', 'data')
    print(r)
    print(len(r))
