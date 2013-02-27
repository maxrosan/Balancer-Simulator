
import io, time
		
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
		self.total_time               = 0.
		self.SLA_breaks               = 0
		self.usage_mean_per           = 0.
		self.usage_stan_per           = 0.
		self.usage_CPU_mean           = 0.
		self.usage_mem_mean           = 0.

		self._start_time              = 0.

	def start_timing(self):
		self._start_time = time.time()

	def stop_timing(self):
		self.total_time  = time.time() - self._start_time

	def balance(self, machines_ready, tasks_to_run, state):
		pass

	def open_log_file(self, filename_balancing, filename_mapping):
		self.balancing_fobj = open(filename_balancing, "w+")
		self.mapping_fobj   = open(filename_mapping, "w+")

	def add_machine_event(self, machine):
		pass		

	def add_task_usage(self, task):
		pass

	def print_balacing_results_verbose(self):
		print "--------- Round %d ------------------------" % self.n_round
		print "Task mapped: ", self.task_mapped_successfully
		print "Task unmapped: ", self.task_failed_to_map
		print "Machines used: ", self.machines_used
		print "Machines not used: ", self.machines_not_used
		print "Migrations: ", self.n_migrations
		print "New tasks: ", self.task_new
		print "Time for balancing: ", self.total_time
		print "SLA: ", self.SLA_breaks
		print "Usage standard deviation: ", self.usage_stan_per
		print "Usage mean: ", self.usage_mean_per
		print "-------------------------------------------"

	def print_log_file(self):
		if self.balancing_fobj != None:
			self.balancing_fobj.write("%d %d %d %d %d %d %d %f %f %f\n" % (self.n_round, self.task_mapped_successfully, self.task_failed_to_map,
			 self.machines_used, self.machines_not_used, self.n_migrations, self.task_new, self.total_time, self.usage_mean_per, self.usage_stan_per))
			self.balancing_fobj.flush()

			self.mapping_fobj.write("Round %d--------------\n" % self.n_round)
			for mac_ID in self.mac_usage:
				self.mapping_fobj.write("## %d (%f, %f, %f, %f) : " % (mac_ID, self.mac_usage[mac_ID][0].capacity_CPU, self.mac_usage[mac_ID][0].capacity_memory, self.mac_usage[mac_ID][0].CPU_usage, self.mac_usage[mac_ID][0].mem_usage))
				for task in self.mac_usage[mac_ID][1]:
					self.mapping_fobj.write("(%d, %f, %f) ; " % (task.getID(), task.CPU_usage, task.mem_usage))
				self.mapping_fobj.write("\n")

			self.mapping_fobj.write("--------------\n")
			self.mapping_fobj.flush()
