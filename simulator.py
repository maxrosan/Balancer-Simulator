#!/usr/bin/pypy

import Queue

class Event:
	
	def __init__(self, _time, _callback, _args):
		self.time = _time                     # tempo em segundos
		self.callback = _callback             # callback do evento
		self.args = _args                     # tupla de argumentos do callback


class Simulator:

	def __init__(self):
		self.pq = Queue.PriorityQueue(0)
		self.curr_time = 0
	
	def add_event(self, event):
		self.pq.put((event.time, event))

	def execute(self, event):
		if event.time >= self.curr_time:
			event.callback(event.args)
			self.curr_time = event.time
		else:
			raise NameError("VoltaDoTempo")

	def main_loop(self):
		while not self.pq.empty():
			e = self.pq.get()
			self.execute(e[1])


if __name__ == "__main__":

	def func_example((attr1, attr2)):
		print attr1, attr2
	
	sim = Simulator()
	sim.add_event(Event(10, func_example, ("Hello", "Word 1")))
	sim.add_event(Event(9, func_example, ("Hello", "Word 2")))
	sim.add_event(Event(12, func_example, ("Hello", "Word 3")))
	sim.main_loop()
