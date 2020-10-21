import time
import multiprocessing


class AsynchTaskQueue:
    def __init__(self, tmp_file=True):
        self._queue = multiprocessing.Queue()
        self.current_task = None
        self.tmp_file = tmp_file

        if tmp_file:
            self.current_task_path = '../tasks.tm'
            with open(self.current_task_path, 'w') as f:
                f.write('')

    def get_current_task(self):
        if self.tmp_file:
            with open(self.current_task_path, 'r') as f:
                self.current_task = f.read()

        return self.current_task

    def add_task(self, func, func_name='', *args, **kwargs):
        if not func_name:
            func_name = func.__name__
        self._queue.put([func, args, kwargs, func_name])

    def run(self):
        multiprocessing.Process(target=self._run).start()

    def _run(self):
        while True:
            if self._queue.empty():
                time.sleep(1)
            func, args, kwargs, func_name = self._queue.get()
            # self.current_task = func_name
            if self.tmp_file:
                with open(self.current_task_path, 'w') as f:
                    f.write(func_name)
            try:
                func(*args, **kwargs)
            except Exception as err:
                print('Error in {}: \n{}'.format(func.__name__, str(err)))
            finally:
                self.current_task = None

                if self.tmp_file:
                    with open(self.current_task_path, 'w') as f:
                        f.write('')


if __name__ == '__main__':
    def func1(a, b):
        time.sleep(5)
        print('I am working!')
        time.sleep(5)
        print('I am still working!')
        time.sleep(5)
        print('I am done!')

    tm = AsynchTaskQueue()
    tm.run()
    tm.add_task(func1)
