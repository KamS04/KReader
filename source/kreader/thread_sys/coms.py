from abc import ABCMeta, abstractmethod

ACTION_SCHEDULE = 1
ACTION_TERMINATE = 1


class Action:
    def __init__(self, action_type, task: 'Task'):
        self.action_type = action_type
        self.task = task


class Result:
    def __init__(self, task_id, task_finished, result, should_put=True, exception_occurred=False):
        self.task_id = task_id
        self.task_finished = task_finished
        self.result = result
        self.should_put = should_put
        self.exception_occurred = exception_occurred


class Task(metaclass=ABCMeta):
    def __init__(self, task_id):
        self.task_id = task_id
    
    def execute(self, results_queue):
        try:
            self.run(results_queue)
        except Exception as e:
            results_queue.put(Result(self.task_id, True, e, exception_occurred=True))

    @abstractmethod
    def run(self, results_queue):
        pass


class SingleTask(Task):
    def __init__(self, task_id, target, args=(), kwargs={}):
        super(SingleTask, self).__init__(task_id)
        self.target = target
        self.args = args
        self.kwargs = kwargs
    
    def run(self, results_queue):
        result_value = self.target(*self.kwargs, **self.kwargs)
        results_queue.put(Result(self.task_id, True, result_value))
    
    def __str__(self):
        return str(self.target)


class MultipleTasks(Task):
    def __init__(self, task_id, *targets):
        super(MultipleTasks, self).__init__(task_id)
        self.targets = targets
    
    def run(self, results_queue):
        for target in self.targets:
            result_value = target()
            results_queue.put(Result(self.task_id, False, result_value))
        results_queue.put(Result(self.task_id, True, None, False))


    def __str__(self):
        return f'Task {self.task_id}'


class StreamingTask(SingleTask):
    def run(self, results_queue):
        for result_value in self.target(*self.args, **self.kwargs):
            results_queue.put(Result(self.task_id, False, result_value))
        results_queue.put(Result(self.task_id, True, None, False))

