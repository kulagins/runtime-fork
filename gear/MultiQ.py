import heapq


class MultiQItem:
    def __init__(self, time, func, args):
        self.time = time
        self.func = func
        self.args = args

    def __lt__(self, other):
        return self.time < other.time

    def __iter__(self):
        return iter((self.time, self.func, self.args))


class MultiQ:
    def __init__(self):
        self.queues = {}
        self.priorities = {}

    def add_queue(self, queue_name, queue=[], priority=10):
        assert queue_name not in self.queues
        heapq.heapify(queue)
        for item in queue:
            assert type(item) is MultiQItem
        self.queues[queue_name] = queue
        self.priorities[queue_name] = priority

    def reset_queue(self, queue_name, queue=[]):
        assert queue_name in self.queues
        heapq.heapify(queue)
        for item in queue:
            assert type(item) is MultiQItem
        self.queues[queue_name] = queue

    def delete_queue(self, queue_name):
        assert queue_name in self.queues
        self.queues.pop(queue_name)

    def change_priority(self, queue_name, priority):
        assert queue_name in self.queues
        self.priorities[queue_name] = priority

    def push_to_queue(self, queue_name, item):
        assert queue_name in self.queues
        assert type(item) is MultiQItem
        heapq.heappush(self.queues[queue_name], item)

    def pop_from_queue(self, queue_name):
        assert queue_name in self.queues
        return heapq.heappop(self.queues[queue_name])

    def get_next(self):
        '''
        Find the queue with the smallest item and return it. If all queues are
        empty or no queues exist, None is returned
        '''
        class candidate:
            def __init__(self, name, time, prio):
                self.name = name
                self.time = time
                self.prio = prio
        candidates = [candidate(name, queue[0].time, self.priorities[name])
                      for name, queue in self.queues.items() if len(queue) > 0]
        if len(candidates) == 0:
            return None
        candidates.sort(key=lambda candidate: (candidate.time, candidate.prio))
        return heapq.heappop(self.queues[candidates[0].name])

    def __iter__(self):
        return self

    def __next__(self):
        ret = self.get_next()
        if ret is None:
            raise StopIteration
        return ret
