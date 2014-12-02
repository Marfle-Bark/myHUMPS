# Ethan Busbee

import sys, random, traceback
from datetime import datetime
from BARQ import PriorityQueue
from Duper import Duper

def test(slots = 200, data = 100, shortsize = 1, longsize = 15):
  print "\n\n\n"
  now = "log/log_" + str(datetime.now())
  out = open(now, "w")
  sys.stdout = Duper(sys.stdout, out)
  print "Logging set up through Duper. Testing begins now!"
  print "(Start time = " + str(datetime.now()) + ")"

  sim = myHUMPS(slots, data, shortsize, longsize)
  # sim.popEverything()
  sim.simulate()
  
class myHUMPS(object):
  """"myHUMPS has a funny name and it's awesome."""

  # class variables
  slots = 100 # Number of slots to bound initial scheduling to
  data = 50 # Amount of data to send (in slots)
  shortsize = 1 # Size of short data streams
  longsize = 10 # Size of long data streams
  ready = False # Whether the sim is prepared or not
  timeline = PriorityQueue() # BARQ priority queue to represent send schedule
  now = 0 # current time (used for scheduling, starts at 0)
  starts = {} # Stream scheduling times, key:value where key = time, value = (start, size)
  ends = {} # Stream completion times, key:value where key = time, value = (start, end, size)

  def __init__(self, slots = 100, data = 20, shortsize = 1, longsize = 5):
    
    # get some breathing room for output
    print "\n\n\n***Starting initialization..."

    # input checking and setting
    self._initializeInputs(slots, data, shortsize, longsize)
    print "Inputs have been validated and set."

    shortData, shortCount = self._getShortSenderInfo()
    longData, longCount = self._getLongSenderInfo()

    print "For " + str(data) + " slots of data to send:"
    print "  80% of the data (" + str(longData) + " slots) will be sent in " + str(longCount) + " streams of size " + str(longsize) + "."
    print "  20% of the data (" + str(shortData) + " slots) will be sent in " + str(shortCount) + " streams of size " + str(shortsize) + "."

    self._massSchedule(shortCount, longCount)
    print "\nScheduling operations have been completed.\n"

    self.ready = True

  def simulate(self):
    try:
      if not self.ready: raise Exception("***ERROR: Simulator not prepared for run. Aborting simulation...")
      print "\n***Starting simulation..."
      waitingToSend = PriorityQueue() # Queue of packets to be sent

      while self.ready and self.timeline.count() > 0:  # while there's still something scheduled to send in the timeline
        while waitingToSend.count() == 0: # while there aren't any streams backed-up and waiting

          nextStream = self.timeline.pop()  # check the next scheduled stream from the timeline
          if nextStream == None: self.ready = False; break # game over!
          # DEBUG
          print "nextStream info: " + str(nextStream)
          # DEBUG

          if self.now < nextStream[0]: # if next stream is from THE FUTURE dundundun
            self.now = nextStream[0]
            print "**Timewarped to time = " + str(self.now) + "..."

          wantToSend = []               # list of streams wanting to send right now
          wantToSend.append(nextStream) # add the stream we know is scheduled for right now to the list

          if self.timeline.count() == 0: self.ready = False
          else:
            temple = self.timeline.pop()  # pop the next scheduled stream off the timeline
            while temple[0] == self.now:  # if the temp tuple (temple) is for right now
              wantToSend.append(temple)   # add it to the list of things wanting to send
              temple = self.timeline.pop()# and also get a new temple and loop back
            self.timeline.push(weight = temple[0], data = temple[1])    # push the FUTURE stream back onto the

          print "\n**Running simulation step: time = " + str(self.now) + "..."
          if len(wantToSend) > 1: # collision! Bummer :c
            self.now = self.now + 1
            print "*There was a collision, time will advance to time = " + str(self.now) + "..."
            for item in wantToSend:
              waitingToSend.push(weight = item[0], data = item[1])

          elif len(wantToSend) == 1: # no collision! hooray!
            print "*A stream of size = " + str(wantToSend[0][1]) + " has the floor..."
            stream = wantToSend[0]
            self.now = self.now + stream[1] # advance time by stream size
            self.ends[self.now] = (self.starts[stream[0]], self.now, stream[1]) # (start time, end time, stream size)
            print "*Stream has been sent, it is now time = " + str(self.now) + "...\n"

          else: # this should mean things are over
            print "*I HAVE NO IDEA WHAT'S GOING ON HERE, WHY IS THIS RUNNING"

        else: # waitingToSend has something that's... waiting to send
          print str(waitingToSend.count()) + " streams dropped from WTS queue."
          waitingToSend.empty()
          continue


        if self.timeline.count() == 0 and waitingToSend.count() == 0: self.ready = False; break # game over, maaaaan
      # end of timeline, finalize things here
    except: print "\n\n\n" + str(traceback.format_exc())
    finally: print "***Ending simulation..."

  def popEverything(self):
    while self.timeline.count() > 0: print self.timeline.pop()
    self.ready = False

  def _massSchedule(self, shortSenderCount, longSenderCount):
    print "\n***Starting mass scheduling operation..."
    
    # schedule short streams
    print "\n**Starting scheduling of short streams...\n"
    for i in range(shortSenderCount):
      time = random.randint(0, self.slots)
      self._schedule(self.shortsize, time)
      self.starts[time] = (time, self.shortsize)
    print "\n**Scheduling of short streams completed...\n"

    # schedule large streams
    print "\n**Starting scheduling of long streams...\n"
    for i in range(longSenderCount):
      time = random.randint(0, self.slots)
      self._schedule(self.longsize, time)
      self.starts[time] = (time, self.longsize)
    print "\n**Scheduling of long streams completed...\n"

  def _schedule(self, size, time):
    print "*Running scheduling step: time = " + str(time) + ", size = " + str(size) + "..."
    self.timeline.push(weight = time, data = size)

  def _initializeInputs(self, slots, data, shortsize, longsize):
    if not slots > 0: raise Exception("\nSlots need to be > 0!")
    if not data > 0: raise Exception("\nData needs to be > 0!")
    if not shortsize > 0: raise Exception("\nShort streams must be > 0!")
    if not longsize > 0: raise Exception("\nLong streams must be > 0!")

    self.slots = int(slots)
    self.data = int(data)
    self.shortsize = int(shortsize)
    self.longsize = int(longsize)

    self.now = 0

  def _getShortSenderInfo(self):
    data_20p = int(0.2 * self.data)
    packetcount = int(data_20p / self.shortsize)
    return (data_20p, packetcount)

  def _getLongSenderInfo(self):
    data_80p = int(0.8 * self.data)
    packetcount = int(data_80p / self.longsize)
    return (data_80p, packetcount)

test()