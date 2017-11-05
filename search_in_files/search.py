# -*- coding: utf-8 -*-

import argparse
from multiprocessing import Array, Process, Queue, cpu_count
from os.path import abspath, exists, isdir, join
from sys import exit, getdefaultencoding
from threading import Thread
from time import time

import six
from search_in_files.csearch import find_in_file, sort

if six.PY3:
    from os import scandir
else:
    from os import listdir as scandir


if six.PY3:
    from queue import Queue as ThreadQueue
else:
    from Queue  import Queue  as ThreadQueue


if six.PY3:
    get_path = lambda folder, f: f.path
else:
    get_path = lambda folder, f: join(folder, str(f))


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


def work(pattern, encoding, task_queue, results, get_result=find_in_file):
    """
        Consumes all the tasks
    """
    while True:
        args = task_queue.get()

        if args is None:
            break

        idx, path = args
        results[idx] = int(get_result(pattern, path, encoding))


def create_tasks(folder, task_queue, scandir=scandir, get_path=get_path):
    """
        Creates one task for each file on a folder
    """
    tasks = []

    for idx, f in enumerate(scandir(folder)):
        path = get_path(folder, f)
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
    encoding,
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
        (pattern, encoding, task_queue, results),
        get_worker_klass(cpu_count)
    )

    # waits for the workers to finish
    wait_for_workers(workers, task_queue)

    # gets the paths and sorts alphabetically
    return sort(tasks, results)


def main():
    parser = argparse.ArgumentParser(
        prog='search_in_files',
        description='Search text in files'
    )

    parser.add_argument(
        'pattern',
        type=str,
        help='an pattern to search'
    )

    parser.add_argument(
        'folder',
        type=str,
        default='.',
        nargs='?',
        help='an folder path (default: .)'
    )

    parser.add_argument(
        'encoding',
        default=None,
        type=str,
        nargs='?',
        help='the char encoding (default: {})'.format(getdefaultencoding())
    )

    args = parser.parse_args()

    pattern = args.pattern
    folder = abspath(args.folder)
    encoding  = args.encoding

    if not exists(folder):
        print('This path does not exists: {}'.format(folder))
        exit(0)

    if not isdir(folder):
        print('This path is not a directory: {}'.format(folder))
        exit(0)

    matches, took = timing(search)(pattern, folder, encoding)

    for match in matches:
        print('{}'.format(match))

    if matches:
        print('There were {} occurrence(s) of the term "{}" ({:0.3f} ms)'
              .format(len(matches), pattern, took))
    else:
        print('No occurrences were found by term "{}" ({:0.3f} ms)'
              .format(pattern, took))


if __name__ == '__main__':
    main()
