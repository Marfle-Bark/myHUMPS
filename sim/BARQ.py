# Ethan Busbee

# BARQ: Busbee's Assorted Reusable Queues

from heapq import heappop, heappush

class PriorityQueue(object):
  queue = []
  size = 0

  def __init__(self):
    self.queue = []
    self.size = 0 

  def __del__(self):
    self.queue = []
    self.size = 0

  # temporarily only supporting one item of data
  def push(self, weight=0, data=None):
    try: weight = int(weight)
    except: weight, data = data, weight
    self.size = self.size + 1
    heappush(self.queue, (weight, data))
    # print "BARQ: pushed " + str((weight, data))

  def pop(self):
    if self.size > 0:
      print "BARQ: normal pop"
      self.size = self.size - 1
      return heappop(self.queue)
    else: return None
    # else: print "BARQ: empty stack pop"; return None

    # if len(data) > 1: return (weight, data)
    # else: return (weight, data[0])

  def count(self):
    return self.size

  def empty(self):
    self.__del__()

def testPQ():
  pq = PriorityQueue()
  
  pq.push(0, "marf")
  pq.push(2, "bark", "bark")
  pq.push(1, "le")

  while pq.count() > 0: print pq.pop()
