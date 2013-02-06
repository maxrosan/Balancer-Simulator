#!/usr/bin/python

import simulator, usage, machine, sets
import methods.randommethod, methods.multiknapsackmethod, methods.toyodamethod
import sys

class BalancerSimulator:

	def __init__(self, main_path, balacing_method):
		self.taskusage       = usage.TaskUsage(main_path + "task_usage", 0)
		self.macevents       = machine.MachineEvent(main_path + "machine_events", 0)
		self.time            = 0
		self.interval        = 300
		self.tasks_to_run    = sets.Set([]) # evita entradas repetidas
		self.tasks_executed  = {}
		self.machines_ready  = sets.Set([])
		self.machines_state  = {}
		self.max_time        = 84600
		self.balacing_method = balacing_method

		self.balacing_method.open_log_file("balacing.log")

	def balance(self):
		self.balacing_method.balance(self.machines_ready, self.tasks_to_run, None)
		self.balacing_method.print_balacing_results_verbose()
		self.balacing_method.print_log_file()

		self.tasks_executed.clear()
		for task in self.tasks_to_run:
			self.tasks_executed[task.getID()] = task.machine_ID

		self.tasks_to_run.clear()
				

	# If the task that requested to run have the same ID as a task executed in last round, it is considered that two tasks are the same.
	# However, the values of CPU and memory usage are updated according to the last registry
	# The Google's workload has some invalid values, so it is necessary to check if the values are in the range from 0 to 1
	@staticmethod
	def add_task_usage(balsim, task):
		if task.CPU_usage > 0. and task.CPU_usage <= 1. and task.mem_usage <= 1.:
			if task.getID() in balsim.tasks_executed:
				task.machine_ID = balsim.tasks_executed[task.getID()]
			balsim.tasks_to_run.add(task)

	@staticmethod
	def add_machine_event(balsim, mac):
		if mac.event_type == machine.MachineEventRegister.ADD_EVENT:
			balsim.machines_ready.add(mac)
		elif mac.event_type == machine.MachineEventRegister.UPDATE_EVENT:
			balsim.machines_ready.discard(mac)
			balsim.machines_ready.add(mac)
		else:
			balsim.machines_ready.discard(mac)

	@staticmethod
	def add_event((sim, balsim)):

		balsim.macevents.read_until(balsim.time, BalancerSimulator.add_machine_event, balsim)
		balsim.taskusage.read_until(balsim.time, BalancerSimulator.add_task_usage, balsim)
		balsim.balance()

		balsim.time = balsim.time + balsim.interval
		if balsim.time < balsim.max_time:
			sim.add_event(simulator.Event(balsim.time, BalancerSimulator.add_event, (sim, balsim)))

### ./main.py <balancing load method> <Google workload path> <number of threads>

method = None

if sys.argv[1] == "help":
	print "./main.py <balancing load method> <Google workload path> <number of threads>"
	exit()
elif sys.argv[1] == "knapsack":
	method = methods.multiknapsackmethod.MultiKnapsackMethod()
elif sys.argv[1] == "toyoda":
	method = methods.toyodamethod.ToyodaMethod()
else:
	method = methods.randommethod.RandomMethod()

#main_path            = "/home/max/Src/gsutil/"

method.n_jobs = int(sys.argv[3])

sim = simulator.Simulator()
balsim = BalancerSimulator(sys.argv[2], method)

sim.add_event(simulator.Event(0., BalancerSimulator.add_event, (sim, balsim)))

sim.main_loop()
