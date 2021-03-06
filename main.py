#!/usr/bin/python
#

import simulator, usage, machine, sets
import sys

class BalancerSimulator:

	def __init__(self, main_path, balacing_method, balancing_log, mapping_log, total_time, machine_events_folder):
		self.taskusage          = usage.TaskUsage(main_path + "task_usage", 0)
		self.macevents          = machine.MachineEvent(main_path + machine_events_folder, 0)
		self.time               = 300
		self.interval           = 300
		self.start_time         = 0
		self.max_time           = total_time
		self.balacing_method    = balacing_method

		balacing_method.bal_sim = self
		
		self.balacing_method.open_log_file(balancing_log, mapping_log)

	def balance(self):
		self.balacing_method.balance()
		self.balacing_method.print_balacing_results_verbose()
		self.balacing_method.print_log_file()
				
	@staticmethod
	def add_task_usage(balsim, task):
		if (task.CPU_usage > 0. or task.mem_usage > 0.) and task.CPU_usage <= 1. and task.mem_usage <= 1.:
			balsim.balacing_method.add_task_usage(task)

	@staticmethod
	def add_machine_event(balsim, mac):
		balsim.balacing_method.add_machine_event(mac)

	@staticmethod
	def add_event((sim, balsim)):

		balsim.macevents.read_until(balsim.time - balsim.interval, balsim.time, BalancerSimulator.add_machine_event, balsim)
		balsim.taskusage.read_until(balsim.time - balsim.interval, balsim.time, BalancerSimulator.add_task_usage, balsim)
		balsim.balance()

		balsim.time = balsim.time + balsim.interval
		if balsim.time <= balsim.max_time:
			sim.add_event(simulator.Event(balsim.time, BalancerSimulator.add_event, (sim, balsim)))

### ./main.py <balancing load method> <Google workload path> <number of threads>

method = None
var_globals = {}
var_locals  = {}

if sys.argv[1] == "help":
	print "./main.py <config_file>"
	exit()
else:
	execfile(sys.argv[1], var_globals, var_locals)

method = var_locals["method"]

sim = simulator.Simulator()
balsim = BalancerSimulator(var_locals["dataset_path"], method, var_locals["balancing_log"], var_locals["mapping_log"], var_locals["total_time"], var_locals["machine_events_folder"])

sim.add_event(simulator.Event(0., BalancerSimulator.add_event, (sim, balsim)))

sim.main_loop()
