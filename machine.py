
import sys, io, os

class MachineEventRegister:

	ADD_EVENT = 0
	REMOVE_EVENT = 1
	UPDATE_EVENT = 2

	def __init__(self):
		self.time = 0.
		self.machine_ID = 0
		self.event_type = 0
		self.platform_ID = 0
		self.capacity_CPU = 0.
		self.capacity_memory = 0.
		self.CPU_usage = 0
		self.mem_usage = 0
		self.used = 0
		self.n_tasks = 0

		self.tasks = []

	def __hash__(self):
		return self.machine_ID

	def __eq__(self, other):
		return (self.machine_ID == other.machine_ID) # evita registros repetidos	

	def print_info(self):
		e = ""
		if self.event_type == 0:
			e = "+"
		elif self.event_type == 1:
			e = "-"
		else:
			e = "U"

		print "(machine event) %d %d [%s] %s %.5f %.5f" % (self.time, self.machine_ID, e, 
			self.platform_ID, self.capacity_CPU, self.capacity_memory)

	def add_task(self, task):
		self.tasks.append(task.getID())
		self.CPU_usage = task.CPU_usage + self.CPU_usage
		self.mem_usage = task.mem_usage + self.mem_usage
		self.n_tasks = self.n_tasks + 1

	def reset_stats(self):
		self.CPU_usage = 0
		self.mem_usage = 0

	def calculate_consumption(self, map_tasks):
		self.CPU_usage = 0
		self.mem_usage = 0

		for task_ID in self.tasks:
			self.CPU_usage = self.CPU_usage + map_tasks[task_ID].CPU_usage
			self.mem_usage = self.mem_usage + map_tasks[task_ID].mem_usage

	def remove_task(self, task):
		self.tasks.remove(task.getID())
		self.CPU_usage = self.CPU_usage - task.CPU_usage
		self.mem_usage = self.mem_usage - task.mem_usage
		self.n_tasks = self.n_tasks - 1


	def SLA_break(self):
		return ((self.CPU_usage - self.capacity_CPU) > 1e-10 or (self.mem_usage - self.capacity_memory) > 1e-10)

	def free_CPU(self):
		return (self.capacity_CPU - self.CPU_usage)

	def free_mem(self):
		return (self.capacity_memory - self.mem_usage)

	def count_tasks(self):
		return self.n_tasks

	def can_run(self, task):
		return ((self.capacity_CPU - self.CPU_usage) > task.CPU_usage and (self.capacity_memory - self.mem_usage) > task.mem_usage)

			
class MachineEvent:

	def __init__(self, folder, part):
		self.line = None
		self.folder = folder
		self.part = part - 1
		self.fd = None
	
	def name_format(self, part):
		num_str = str(part)
		fn = self.folder + "/part-" + ("0" * (5 - len(num_str))) + num_str + "-of-00001.csv"
		return fn
	
	def has_next(self):
		fn = self.name_format(self.part + 1)
		e = os.path.exists(fn)
		if not e:
			print "Nao existe " + fn
		return e
	def open_next(self):
		self.part = self.part + 1
		self.fd = io.open(self.name_format(self.part), 'r+')

		print "Arquivo " + str(self.part) + " do machine event"

	def dect_eof(self):
		return (self.line == None)

	def read_next_line(self):
		if self.fd == None:
			self.line = None
			return

		ln = self.fd.readline()
		if len(ln) < 1 or (not ln.endswith("\n")):
			self.line = None
		else:
			self.line = ln.split(',',6)
		
	def read_until(self, start, end, callback, arg): # callback(arg, MachineEventRegister)

		keep_going = True

		while keep_going:

			if self.line == None:
				self.read_next_line()

			if self.dect_eof():
				if self.has_next():
					self.open_next() # considera-se que o proximo arquivo tenha pelo menos uma linha
				else:
					keep_going = False
			else:
				machine = MachineEventRegister()
				machine.time = float(self.line[0])/1000000.
				machine.machine_ID = int(self.line[1])
				machine.event_type = int(self.line[2])
				machine.platform_ID = self.line[3]
				machine.capacity_CPU = float(self.line[4])
				machine.capacity_memory = float(self.line[5])

				#machine.print_info()

				if start <= machine.time and machine.time <= end:
					callback(arg, machine)
					self.line = None				
				else:
					keep_going = False
		
		return True


if __name__ == "__main__":

	def machine_info(arg, machine):
		machine.print_info()
	
	macev = MachineEvent(sys.argv[1], 0)
	macev.read_until(100., machine_info, None)
