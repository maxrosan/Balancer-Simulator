#!/usr/bin/python

import simulator, usage, machine, sets
import methods.toyodamethod
import sys

class BalancerSimulator:

	def __init__(self, main_path, balacing_method):
		self.taskusage       = usage.TaskUsage(main_path + "task_usage", 0)
		self.macevents       = machine.MachineEvent(main_path + "machine_events", 0)
		self.time            = 0
		self.interval        = 300
		self.start_time      = 0
		self.max_time        = 84600
		self.balacing_method = balacing_method
		
		self.balacing_method.open_log_file("balancing.log", "mapping.log")

	def balance(self):
		self.balacing_method.balance()
		self.balacing_method.print_balacing_results_verbose()
		self.balacing_method.print_log_file()
				
	@staticmethod
	def add_task_usage(balsim, task):
		if task.CPU_usage > 0. and task.mem_usage > 0 and task.CPU_usage <= 1. and task.mem_usage <= 1.:
			balsim.balacing_method.add_task_usage(task)

	@staticmethod
	def add_machine_event(balsim, mac):
		balsim.balacing_method.add_machine_event(mac)

	@staticmethod
	def add_event((sim, balsim)):

		balsim.macevents.read_until(balsim.time, BalancerSimulator.add_machine_event, balsim)
		balsim.taskusage.read_until(balsim.time, BalancerSimulator.add_task_usage, balsim)
		balsim.balance()

		balsim.time = balsim.time + balsim.interval
		if balsim.time <= balsim.max_time:
			sim.add_event(simulator.Event(balsim.time, BalancerSimulator.add_event, (sim, balsim)))

### ./main.py <balancing load method> <Google workload path> <number of threads>

method = None

if sys.argv[1] == "help":
	print "./main.py <balancing load method> <Google workload path> <number of threads>"
	exit()
#elif sys.argv[1] == "knapsack":
#	method = methods.multiknapsackmethod.MultiKnapsackMethod()
elif sys.argv[1] == "toyoda":
	method = methods.toyodamethod.ToyodaMethod(sys.argv[4:])
else:
	method = None

#main_path            = "/home/max/Src/gsutil/"

method.n_jobs = int(sys.argv[3])

sim = simulator.Simulator()
balsim = BalancerSimulator(sys.argv[2], method)

sim.add_event(simulator.Event(0., BalancerSimulator.add_event, (sim, balsim)))

sim.main_loop()
