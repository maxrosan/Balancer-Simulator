

import io, sys
import numpypy as numpy

class LogEntry:

	def __init__(self):
		self.n_round = 0
		self.task_mapped_successfully = 0
		self.task_failed_to_map = 0
		self.machines_used = 0
		self.machines_not_used = 0
		self.n_migrations = 0
		self.task_new = 0
		self.total_time = 0
		self.usage_mean_per = 0
		self.usage_stan_per = 0
		self.usage_CPU_mean = 0
		self.usage_mem_mean = 0
		self.total_tasks = 0
		self.SLA_breaks = 0

class LogReader:

	def __init__(self, filename):

		self.fn = open(filename, "r")

	def read_rounds(self, start, end):
		
		keep_reading = True
		result = []

		while keep_reading:
			ln = self.fn.readline()
			if len(ln) < 1:
				keep_reading = False
			else:
				entries = ln.split(' ', 13)

				log_entry = LogEntry()

				log_entry.n_round                  = int(entries[0])
				log_entry.task_mapped_successfully = int(entries[1])
				log_entry.task_failed_to_map       = int(entries[2])
				log_entry.machines_used            = int(entries[3])
				log_entry.machines_not_used        = int(entries[4])
				log_entry.n_migrations             = int(entries[5])
				log_entry.task_new                 = int(entries[6])
				log_entry.total_time               = float(entries[7])
				log_entry.usage_mean_per           = float(entries[8])
				log_entry.usage_stan_per           = float(entries[9])
				log_entry.usage_CPU_mean           = float(entries[10])
				log_entry.usage_mem_mean           = float(entries[11])
				log_entry.total_tasks              = int(entries[12])
				log_entry.SLA_breaks               = int(entries[13])


				if self.n_round >= start and self.n_round <= end:
					result.append(log_entry)
				
				if self.n_round > end:
					keep_reading = False

		return result

	def get_stats(self, start, end):

		entries = self.read_rounds(start, end)
		
		macs = [e.machines_used + e.machines_not_used for e in entries]
			
		print "Max. num. de maquinas: %d \n" % (max(macs))
		print "Min. num. de maquinas: %d \n" % (min(macs))
		print "Med. num. de maquinas: %f \n" % (self.mean(macs))



if __name__ == "__main__":

	fn    = sys.argv[1]
	start = int(sys.argv[2])
	end   = int(sys.argv[3])

	reader = LogReader(fn)
	reader.get_stats(start, end)
