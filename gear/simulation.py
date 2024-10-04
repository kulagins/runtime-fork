import heapq


class Event:
    def __init__(self, time, callback, data, tags=[], priority=10):
        '''
        An event in the simulation. At the given time, the callback will be
        called with the user provided data as its argument.

        The tags can be used to retrieve related arguments from the queue.

        The priority is used as a tie breaker between events that have the
        same time. Events with lower numbers are preferred over events with
        higher numbers.
        '''
        self.time = time
        self.callback = callback
        self.data = data
        self.tags = tags
        # TODO low number means high priority is counterintuitive. Find a
        # better solution.
        self.priority = priority

    def __lt__(self, other):
        return (self.time, self.priority) < (other.time, other.priority)


class Simulation:
    def __init__(self):
        self.queue = []
        self.time = 0

    def next_event(self):
        event = heapq.heappop(self.queue)
        if self.time> event.time:
            print("event "+event.data.name+ "time "+event.time+"vs current time "+self.time)
        assert event.time >= self.time
        self.time = event.time
        # print(f'{event.time}: {event.callback.__name__} {event.data}')
        event.callback(event.data, event.tags)

    def add_event(self, event):
        assert type(event) is Event
        heapq.heappush(self.queue, event)

    def reset_queue(self, tag=None):
        '''
        Either remove all events from the queue or if a tag is given remove all
        events with the given tag.
        '''
        if tag is None:
            self.queue = []
            return
        self.queue = [e for e in self.queue if tag not in e.tags]
        heapq.heapify(self.queue)

    def find_event_by_name(self, blockingtask_name):
        found_obj = next((obj for obj in self.queue if obj.data.name == blockingtask_name), None)
        return found_obj
