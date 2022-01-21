from threading import Lock

HIGH_PRIORITY = 0
NORMAL_PRIORITY = 1
LOW_PRIORITY = 2
NO_PRIORITY = 3

class Topic():
    def __init__(self, name):
        self.name = name
        self.listener_priorities = {}
        self.listeners = {
            HIGH_PRIORITY: {},
            NORMAL_PRIORITY: {},
            LOW_PRIORITY: {},
            NO_PRIORITY: {}
        }
        self._lock = Lock()
        self.last = None
    
    def subscribe(self, identifier, listener, priority):
        self.listener_priorities[identifier] = priority
        self.listeners[priority][identifier] = listener
        if self.last is not None:
            listener(**self.last)

    def change_priority(self, identifier, new_priority):
        with self._lock:
            old_priority = self.listener_priorities[identifier]
            self.listeners[new_priority][identifier] = self.listeners[old_priority][identifier]
            del self.listeners[old_priority][identifier]
            self.listener_priorities[identifier] = new_priority
    
    def publish(self, **data):
        with self._lock:
            self.last = data
        for priority in [HIGH_PRIORITY, NORMAL_PRIORITY, LOW_PRIORITY, NO_PRIORITY]:
            with self._lock:
                listeners = self.listeners[priority].values()
            for listener in listeners:
                    listener(**data)

    def unsubscribe(self, identifier):
        with self._lock:
            del self.listeners[ self.listener_priorities[identifier] ][identifier]
            del self.listener_priorities[identifier]


class Publisher():
    def __init__(self):
        self._topics = {}
    
    def subscribe(self, topic, identifier, listener, priority=NO_PRIORITY):
        self._get_topic(topic).subscribe(identifier, listener, priority)

    def publish(self, topic, **data):
        self._get_topic(topic).publish(**data)
    
    def change_priority(self, topic, identifier, new_priority):
        self._get_topic(topic).change_priority(identifier, new_priority)
    
    def unsubscribe(self, topic, identifier):
        self._get_topic(topic).unsubscribe(identifier)
    
    def _get_topic(self, topic_name) -> Topic:
        if topic_name not in self._topics:
            self._topics[topic_name] = Topic(topic_name)
        return self._topics[topic_name]

