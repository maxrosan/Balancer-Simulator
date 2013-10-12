
import sys
import file.reader
import numpy
import matplotlib.pyplot as mp

class TaskEvent:

	timestamp    = 0
	task_index   = 0
	machine_ID   = 0
	event_type   = 0
	priority     = 0

	request_CPU  = 0
	request_mem  = 0
	request_disk = 0

	def __init__(self):
		pass

class TaskEventReader (file.reader.Reader):

	def __init__(self, folder, part):
		file.reader.Reader.__init__(self, folder, part)

	def verify_model(self, condition, model):
		
		return (model.timestamp < condition)

#1 timestamp 
#2 missing info 
#3 job ID 
#4 task index - within the job 
#5 machine ID 
#6 event type 
#7 user name 
#8 scheduling class 
#9 priority 
#10 resource request for CPU cores 
#11 resource request for RAM 
#12 resource request for local disk space 
#13 different-machine constraint

	def get_model(self):

		e = TaskEvent()

		e.timestamp = float(self.line[0])/1000000.
		e.task_index = 0
		e.machine_ID = 0
		e.event_type = 0
		e.priority = int(self.line[8])
		return e


if __name__ == "__main__":

	class histogramState:
		max_bin = 0
		hits    = []
		num_of_events = 0

		def __init__(self):
			pass

	def print_task_event(e, histo):
		histo.max_bin = max(h.max_bin, e.priority)
		histo.hits.append(e.priority)
		histo.num_of_events = histo.num_of_events + 1
		print "\r number of events processed = %d" % (histo.num_of_events),

	h = histogramState()
	taskEventReader = TaskEventReader(sys.argv[1], 0)
	taskEventReader.read_until(15631., print_task_event, h)

	print "max_priority = ", h.max_bin
	fig = mp.figure()
	ax  = fig.add_subplot(111)
	ax.hist(h.hits, h.max_bin, color="green", alpha=0.8)
	mp.show()