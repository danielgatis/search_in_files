# -*- coding: utf-8 -*-

cimport cython
from multiprocessing import Array, Process, Queue, cpu_count
from os.path import abspath, exists, isdir, join
from sys import argv, exit
from threading import Thread
from time import time

import six

if six.PY3:
    from os import scandir
else:
    from os import listdir as scandir


if six.PY3:
    from queue import Queue as ThreadQueue
else:
    from Queue  import Queue  as ThreadQueue


if six.PY3:
    get_path = lambda f: f.path
else:
    get_path = lambda f: join(folder, str(f))


def timing(f, time=time):
    """
        Measures the time of execution of a function
    """
    def wrap(*args):
        time1 = time()
        ret = f(*args)
        time2 = time()
        took = (time2 - time1) * 1000
        return ret, took
    return wrap


def find_in_file(pattern, path, open_file=open):
    """
        Returns True when the file contains the pattern otherwise returns False
    """
    try:
        with open_file(path, 'r') as f:
            for line in f:
                if line.find(pattern) > -1:
                    return True
    except:
        pass

    return False


def work(pattern, task_queue, results, get_result=find_in_file):
    """
        Consumes all the tasks
    """
    while True:
        args = task_queue.get()

        if args is None:
            break

        idx, path = args
        results[idx] = int(get_result(pattern, path))


def create_tasks(folder, task_queue, scandir=scandir):
    """
        Creates one task for each file on a folder
    """
    tasks = []

    for idx, f in enumerate(scandir(folder)):
        path = get_path(f)
        task = (idx, path)
        tasks.append(task)
        task_queue.put(task)

    return tasks


def create_workers(worker_number, args, process_klass, work_f=work):
    """
        Creates the workers based on cpu count
    """
    workers = []

    for _ in range(worker_number):
        w = process_klass(target=work_f, args=args)
        w.daemon = True
        w.start()
        workers.append(w)

    return workers


def wait_for_workers(workers, task_queue):
    """
        Waits for all workers to finish
    """
    for w in workers:
        task_queue.put(None)

    for w in workers:
        w.join()

    task_queue.close()


def get_worker_klass(cpu_count):
    """
        Gets the worker class based on cpu count
    """
    if cpu_count == 1:
        return Thread

    return Process


def get_task_queue(cpu_count):
    """
        Gets the queue based on cpu count
    """
    if cpu_count == 1:
        t = ThreadQueue()
        t.close = lambda: None
        return t

    return Queue()


def search(
    pattern,
    folder,
    get_task_queue=get_task_queue,
    get_worker_klass=get_worker_klass,
    array_klass=Array,
    get_cpu_count=cpu_count,
    create_tasks=create_tasks,
    create_workers=create_workers,
    wait_for_workers=wait_for_workers,
):
    """
        Searches for a pattern on each file of an folder
    """
    # cpu count
    cpu_count = get_cpu_count()

    # creates the task queue
    task_queue = get_task_queue(cpu_count)

    # creates a task for each file in folder and puts it in queue
    tasks = create_tasks(folder, task_queue)

    # creates a shared memory to store the results
    results = array_klass('i', len(tasks), lock=False)

    # creates a bunch of workers
    workers = create_workers(
        get_cpu_count(),
        (pattern, task_queue, results),
        get_worker_klass(cpu_count)
    )

    # waits for the workers to finish
    wait_for_workers(workers, task_queue)

    # gets the paths and sorts alphabetically
    matches = [tasks[i][1] for i, match in enumerate(results) if match]
    matches.sort()

    return matches


if __name__ == '__main__':
    if (len(argv) < 3):
        print('Usage: python search.py <pattern> <directory>')
        print('')
        print('Example:')
        print('\tpython search.py "walt disney" ./data')
        exit(0)

    pattern = argv[1]
    folder = abspath(argv[2])

    if not exists(folder):
        print('O caminho {} não existe'.format(folder))
        exit(0)

    if not isdir(folder):
        print('O caminho {} não é um diretório'.format(folder))
        exit(0)

    matches, took = timing(search)(pattern, folder)

    for match in matches:
        print('{}'.format(match))

    if matches:
        print('Foram encontrada {} ocorrência(s) pelo termo "{}" ({:0.3f} ms)'
              .format(len(matches), pattern, took))
    else:
        print('Não foram encontrada ocorrências pelo termo "{}" ({:0.3f} ms)'
              .format(pattern, took))
