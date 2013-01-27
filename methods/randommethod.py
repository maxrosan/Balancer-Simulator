

import loadbalacing, random

class RandomMethod(loadbalacing.LoadBalacing):

	def __init__(self):
		random.seed()
	
	def balance(self, machines_ready, tasks_to_run, tasks_constraints):

		print "Random balacing"

		
		#mac_list = sorted(list(machines_ready), key=lambda mac: mac.capacity_CPU, reverse=True)

		mac_list = list(machines_ready)

		for task in tasks_to_run:
			mac_selected = mac_list[random.randint(0, len(mac_list)-1)]
			print "%d/%d(%.5f, %.5f) em mac %d (cpu = %.5f, mem = %.5f)" % (task.job_ID, task.task_ID, task.CPU_usage, task.mem_usage,
				mac_selected.machine_ID, mac_selected.capacity_CPU, mac_selected.capacity_memory)
