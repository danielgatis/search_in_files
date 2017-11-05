# -*- coding: utf-8 -*-

import unittest
from multiprocessing import Process
from multiprocessing.queues import Queue
from os.path import join
from threading import Thread

import six
from search_in_files.search import (create_tasks, create_workers, find_in_file,
                                    get_task_queue, get_worker_klass, search,
                                    timing, wait_for_workers, work)

if six.PY3:
    from queue import Queue as ThreadQueue
else:
    from Queue  import Queue  as ThreadQueue


class SearchTest(unittest.TestCase):
    def test_timing(self):
        times = [2, 1]
        f = lambda: 'ok'
        time = lambda: times.pop()

        r = timing(f, time)()

        self.assertTrue(r[0] == 'ok')
        self.assertTrue(r[1] == 1000)

    def test_find_in_file_when_true(self):
        r = find_in_file('match', 'fake-path', 'utf-8', open_file=mocked_open)
        self.assertTrue(r)

    def test_find_in_file_when_false(self):
        r = find_in_file('no-match', 'fake-path', 'utf-8', open_file=mocked_open)
        self.assertFalse(r)

    def test_work_get_result(self):
        tasks = [None, (0, True)]
        f  = lambda x, y, z: True
        results = [0]
        queue = MockedQueue(tasks=tasks)

        work('pattern', 'utf-8', queue, results, get_result=f)

        self.assertTrue(results[0])

    def test_work_killed(self):
        tasks = [(0, True), None]
        f  = lambda x, y, z: True
        results = [0]
        queue = MockedQueue(tasks=tasks)

        work('pattern', 'utf-8', queue, results, get_result=f)

        self.assertFalse(results[0])

    def test_create_tasks_python3(self):
        folder =  'folder'

        paths = [
            'path1',
            'path2',
            'path3',
        ]

        queue = MockedQueue()
        get_path = lambda folder, f: f.path

        tasks = create_tasks(
            folder,
            queue,
            scandir=mocked_scandir(paths),
            get_path=get_path
        )

        self.assertTrue(len(tasks) == len(paths))
        self.assertTrue(tasks == list(enumerate(paths)))

    def test_create_tasks_python2(self):
        folder =  'folder'

        paths = [
            'path1',
            'path2',
            'path3',
        ]

        queue = MockedQueue()
        get_path = lambda folder, f: join(folder, str(f))

        tasks = create_tasks(
            'folder',
            queue,
            scandir=mocked_scandir(paths),
            get_path=get_path
        )

        full_paths = [(p[0], join(folder, p[1])) for p in enumerate(paths)]

        self.assertTrue(len(tasks) == len(paths))
        self.assertTrue(tasks == full_paths)

    def test_create_workers(self):
        f = lambda: True
        args = (True,)
        process_klass = MockedProcess
        worker_number = 1

        workers = create_workers(worker_number, args, process_klass, work_f=f)

        self.assertTrue(len(workers) == 1)
        self.assertTrue(workers[0].daemon)
        self.assertTrue(workers[0].is_started)
        self.assertTrue(workers[0].args == args)
        self.assertTrue(workers[0].target == f)

    def test_wait_for_workers(self):
        queue = MockedQueue()
        workers = [MockedWorker(), MockedWorker()]
        wait_for_workers(workers, queue)

        for w in workers:
            self.assertTrue(w.is_joined)

        self.assertTrue(queue.is_closed)

    def test_get_worker_klass_multicore(self):
        self.assertTrue(get_worker_klass(2) == Process)

    def test_get_worker_klass_singlecore(self):
        self.assertTrue(get_worker_klass(1) == Thread)

    def test_get_task_queue_multicore(self):
        self.assertTrue(isinstance(get_task_queue(2), Queue))

    def test_get_task_queue_singlecore(self):
        self.assertTrue(isinstance(get_task_queue(1), ThreadQueue))

    def test_search(self):
        results = [1, 1, 1, 1]
        paths = ['z', 'w', 'f', 'a']
        tasks = list(enumerate(paths))

        cpu_count = lambda: None
        get_task_queue = lambda x: None
        get_worker_klass = lambda x: None
        array_klass = lambda x, y, lock: results
        create_tasks = lambda x, y: tasks
        create_workers = lambda x, y, z: None
        wait_for_workers = lambda x, y: None

        matches = search(
            'pattern',
            'folder',
            'utf-8',
            get_task_queue=get_task_queue,
            get_worker_klass=get_worker_klass,
            array_klass=array_klass,
            get_cpu_count=cpu_count,
            create_tasks=create_tasks,
            create_workers=create_workers,
            wait_for_workers=wait_for_workers,
        )

        self.assertTrue(len(matches) == len(results))
        self.assertTrue(matches == sorted(paths))


class mocked_open:
    def __init__(self, *args, **kwargs):
        pass

    def __exit__(self, *args):
        pass

    def __enter__(self):
        def f():
            yield 'match'

        return f()


class MockedQueue:
    def __init__(self, tasks=[]):
        self.tasks = tasks
        self.is_closed = False

    def get(self):
        return self.tasks.pop()

    def close(self):
        self.is_closed = True

    def put(self, t):
        self.tasks.append(t)


class MockedWorker:
    def __init__(self):
        self.is_joined = False

    def join(self):
        self.is_joined = True


class MockedProcess:
    def __init__(self, target, args):
        self.daemon = False
        self.is_started = False
        self.target = target
        self.args = args

    def start(self):
        self.is_started = True


def mocked_scandir(paths):
    _paths = paths[:]

    class F:
        def __init__(self, path):
            self.path = path

        def __str__(self):
            return self.path

    def G(path):
        while len(_paths) > 0:
            yield F(_paths.pop(0))

    return G


if __name__ == '__main__':
    unittest.main()
