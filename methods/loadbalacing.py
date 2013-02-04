
import io
		
class LoadBalacing:
	
	def __init__(self):
		self.mac_usage                = {}
		self.n_round                  = 0
		self.fobj                     = None
		self.n_jobs                   = 2
		self.reset_stats()	

	def reset_stats(self):
		self.mac_usage.clear()
		self.task_mapped_successfully = 0
		self.task_failed_to_map       = 0
		self.task_new                 = 0
		self.machines_used            = 0
		self.machines_not_used        = 0
		self.n_migrations             = 0

	def balance(self, machines_ready, tasks_to_run, state):
		pass

	def open_log_file(self, filename):
		self.fobj = open(filename, "w")
		

	def print_balacing_results_verbose(self):
		print "--------- Round %d ------------------------" % self.n_round
		print "Task mapped: ", self.task_mapped_successfully
		print "Task unmapped: ", self.task_failed_to_map
		print "Machines used: ", self.machines_used
		print "Machines not used: ", self.machines_not_used
		print "Migrations: ", self.n_migrations
		print "New tasks: ", self.task_new
		print "-------------------------------------------"

	def print_log_file(self):
		if self.fobj != None:
			self.fobj.write("%d %d %d %d %d\n" % (self.n_round, self.task_mapped_successfully, self.task_failed_to_map,
			 self.machines_used, self.machines_not_used))
			self.fobj.flush()
