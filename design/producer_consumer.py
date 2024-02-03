from threading import Thread
import time
import random
from queue import Queue

queue = Queue(10)

class DataServer(Thread):

    def __init__(self,queue):
        self.queue = queue
        super(DataServer,self).__init__()
        
    def run(self):
        nums = list(range(5))
        while True:
            num = random.choice(nums)
            self.queue.put(num)
            print("Produced", num)
            print("Queue: ", self.queue.qsize())
            time.sleep(random.random())


class DataClient(Thread):
    def __init__(self,queue):
        self.queue = queue
        super(DataClient,self).__init__()
        
    def run(self):
        while True:
            num = self.queue.get()
            self.queue.task_done()
            print("Consumed", num)
            time.sleep(random.random())


ds = DataServer(queue)
dc = DataClient(queue)

dc.start()
time.sleep(3)
ds.start()
