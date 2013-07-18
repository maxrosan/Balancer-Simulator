

import io, sys
import numpypy as numpy
import tarfile, re

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


				if log_entry.n_round >= start and log_entry.n_round <= end:
					result.append(log_entry)
				
				if log_entry.n_round > end:
					keep_reading = False

		return result

	def get_stats(self, start, end):

		entries = self.read_rounds(start, end)
		
		macs  = [e.machines_used + e.machines_not_used for e in entries]
		tasks = [e.total_tasks for e in entries]
			
		print "Max. num. de maquinas: %d" % (max(macs))
		print "Min. num. de maquinas: %d" % (min(macs))
		print "Med. num. de maquinas: %f" % (numpy.mean(macs))
		print "Var. num. de maquinas: %f" % (numpy.std(macs))

		print "Max. num. de tarefas: %d" % (max(tasks))
		print "Min. num. de tarefas: %d" % (min(tasks))
		print "Med. num. de tarefas: %f" % (numpy.mean(tasks))
		print "Var. num. de tarefas: %f" % (numpy.std(tasks))

class LogMappingReader:

	def __init__(self):
		pass

	def read_from_stdin(self, start):
	
		line_start = "Round " + str(start) + "--------------\n"
		contents = ""
		line_end   = "--------------\n"

		macs = []

		print "Looking for round"
		while sys.stdin.readline() != line_start:
			pass

		print "Round found"

		ln = sys.stdin.readline()
		i = 0
		while ln != line_end:
			contents = contents + ln
			ln = sys.stdin.readline()
			#print "\r n of lns = %d " % (i),
			i = i + 1

		print "\nRound read"

		for entry in contents.split("##"):
			srv = entry.split(":")[0].replace(",", "").replace("(","").replace(")","").split(" ")[1:]
			if len(srv) == 8:
				macs.append(srv)
			#print srv

		print "Split done => %d " % (len(macs))

		print macs[-1]

		macs = sorted(macs, key=lambda mac:3.*float(mac[1])*float(mac[2]) + float(mac[5])*float(mac[6]), reverse=True)

		for mac in macs:
			print "%f %f" % (float(mac[1]) * float(mac[2]), float(mac[5]) * float(mac[6]))
		

if __name__ == "__main__":

	if sys.argv[1] == "logreader":

		fn     = sys.argv[2]
		start  = int(sys.argv[3])
		end    = int(sys.argv[4])
		reader = LogReader(fn)
		reader.get_stats(start, end)

	elif sys.argv[1] == "mappingreader":

		mappingLog = LogMappingReader()
		mappingLog.read_from_stdin(int(sys.argv[2]))

	else:
		print "command not found"
