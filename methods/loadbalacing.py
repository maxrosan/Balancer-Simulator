
class LoadBalacing:
	
	def __init__(self):
		self.mac_usage                = {}
		self.n_round                  = 0
		self.reset_stats()

	def reset_stats(self):
		self.mac_usage.clear()
		self.task_mapped_successfully = 0
		self.task_failed_to_map       = 0
		self.machines_used            = 0
		self.machines_not_used        = 0

	def balance(self, machines_ready, tasks_to_run, tasks_constraints):
		pass

	def print_balacing_results_verbose(self):
		print "--------- Round %d ------------------------" % self.n_round
		print "Task mapped: ", self.task_mapped_successfully
		print "Task unmapped: ", self.task_failed_to_map
		print "Machines used: ", self.machines_used
		print "Machines not used", self.machines_not_used
		print "-------------------------------------------"
