
import io, time, gzip
		
class LoadBalacing:
	
	def __init__(self):
		self.mac_usage                = {}
		self.n_round                  = 0
		self.fobj                     = None
		self.n_jobs                   = 2
		self.bal_sim                  = None

		self.reset_stats()	

		self.intervalOfSampling = 300/3600.
		self.timeForMigration   = 60/3600.

		self.W_cpu_l_25 = 48   * self.intervalOfSampling
		self.W_cpu_g_25 = 21.3 * self.intervalOfSampling

		self.W_on_l_25 = 18      * self.intervalOfSampling
		self.W_on_g_25 = 24.675  * self.intervalOfSampling

		self.W_mig     = (30. + 30.) * self.timeForMigration

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
		self.total_tasks              = 0.
		self.finished_tasks           = 0

		self._start_time              = 0.

	def start_timing(self):
		self._start_time = time.time()

	def stop_timing(self):
		self.total_time  = time.time() - self._start_time

	def balance(self):
		pass

	def open_log_file(self, filename_balancing, filename_mapping):
		self.balancing_fobj = open(filename_balancing, "w+")
		#self.mapping_fobj   = open(filename_mapping, "w+")
		self.mapping_fobj   = open(filename_mapping, "w+")
		self.usage_obj      = open(filename_mapping + "usage.log", "w+")

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
		print "Usage CPU mean: ", self.usage_CPU_mean
		print "Usage mem mean: ", self.usage_mem_mean
		print "Total: ", self.total_tasks
		print "Finished tasks: ", self.finished_tasks
		print "Energy: ", self._calculate_energy()
		print "-------------------------------------------"

	def _calculate_energy(self):

		W_total = 0.

		for mac_ID in self.mac_usage:
			if self.mac_usage[mac_ID][0].count_tasks() > 0:
				W_total = W_total + (self.W_on_l_25 if self.mac_usage[mac_ID][0].CPU_usage_real < 0.25 else self.W_on_g_25)
				W_total = W_total + (self.W_cpu_l_25 if self.mac_usage[mac_ID][0].CPU_usage_real < 0.25 else self.W_cpu_g_25) * self.mac_usage[mac_ID][0].CPU_usage_real

		W_total = W_total + self.W_mig * self.n_migrations

		return W_total

	def print_log_file(self):
		if self.balancing_fobj != None:


			W_total = self._calculate_energy()

			self.balancing_fobj.write("%d %d %d %d %d %d %d %f %f %f %f %f %d %d %f\n" % (
				self.n_round,
				self.task_mapped_successfully, self.task_failed_to_map,
			 	self.machines_used, self.machines_not_used,
				self.n_migrations,
				self.task_new,
				self.total_time,
				self.usage_mean_per, self.usage_stan_per,
				self.usage_CPU_mean, self.usage_mem_mean,
				self.total_tasks,
				self.SLA_breaks,
				W_total))

			self.balancing_fobj.flush()

			self.mapping_fobj.write("Round %d--------------\n" % self.n_round)
			self.usage_obj.write("%d %d\n" % (self.n_round, len(self.mac_usage)))

			for mac_ID in self.mac_usage:
				
				self.mapping_fobj.write("## %d (%f, %f, %f, %f, %f, %f) : " % (
					mac_ID, 
					self.mac_usage[mac_ID][0].capacity_CPU, self.mac_usage[mac_ID][0].capacity_memory, 
					self.mac_usage[mac_ID][0].CPU_usage, self.mac_usage[mac_ID][0].mem_usage,
					self.mac_usage[mac_ID][0].CPU_usage_real, self.mac_usage[mac_ID][0].mem_usage_real
					))

				self.usage_obj.write("%d %f %f\n" % (mac_ID, self.mac_usage[mac_ID][0].CPU_usage_real, self.mac_usage[mac_ID][0].mem_usage_real))

				cpu_total = 0.
				mem_total = 0.

				cpu_total_real = 0.
				mem_total_real = 0.

				SLA_status = ("SLA = %d" % (self.mac_usage[mac_ID][0].count_tasks())) if self.mac_usage[mac_ID][0].SLA_break() else "No SLA" 

				for task in self.mac_usage[mac_ID][1]:
					self.mapping_fobj.write("(%s, %f, %f, %f, %f) ; " % (
					 task.getID(), 
					task.CPU_usage, task.mem_usage,
					task.CPU_usage_real, task.mem_usage_real
					))
					
					cpu_total = cpu_total + task.CPU_usage
					mem_total = mem_total + task.mem_usage

					cpu_total_real = cpu_total_real + task.CPU_usage_real
					mem_total_real = mem_total_real + task.mem_usage_real

				self.mapping_fobj.write(" === (%f, %f, %f, %f)[%s]\n\n" % (cpu_total, mem_total, cpu_total_real, mem_total_real, SLA_status))

			self.mapping_fobj.write("--------------\n")
			self.mapping_fobj.flush()
			self.usage_obj.flush()

