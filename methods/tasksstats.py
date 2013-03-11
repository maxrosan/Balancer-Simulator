import loadbalacing
import numpypy as numpy
import math, random, Queue, io

# RandomMethod selects a task randomly to run
#
class TasksStats(loadbalacing.LoadBalacing):

	def __init__(self, fileoutput):

		loadbalacing.LoadBalacing.__init__(self)

		self.tasks         = {}
		self.machines      = {}
		self.logf          = open(fileoutput, 'w+')
		self.hist          = {}

		self.n_writes      = 0

	def __generate_output(self):

		if len(self.tasks) == 0:
			return

		map_t = {}
		
		name = "%d-%d.csv" % (int(self.bal_sim.time - self.bal_sim.interval), int(self.bal_sim.time))
		op = open(name, "w+")

		for task_ID in self.tasks:
			key = "%d-%d-%d-%d" % (int(self.bal_sim.time - self.bal_sim.interval), int(self.bal_sim.time), self.tasks[task_ID].job_ID, self.tasks[task_ID].task_ID)
			map_t[key] = (self.tasks[task_ID].CPU_usage, self.tasks[task_ID].mem_usage)

		keys = sorted(map_t.keys())

		for key in keys:
			op.write(("\t".join(key.split("-"))) + ("\t%f\t%f\n" % map_t[key]))

		op.close()
			

	def balance(self):
		
		cpu = 0.
		mem = 0.

		self.n_round = self.n_round + 1

		n_rem = 0
		for task_ID in list(self.tasks):
			if self.tasks[task_ID].last_round < self.n_round:
				del self.tasks[task_ID]
				del self.hist[task_ID]
				n_rem = n_rem + 1
			else:
				self.tasks[task_ID].inc_age()
				self.hist[task_ID].append((self.tasks[task_ID].CPU_usage, self.tasks[task_ID].mem_usage))

		self.reset_stats()

#		for mac in self.machines:
#
#			obj = self.machines[mac]

#			cpu = cpu + obj.capacity_CPU
#			mem = mem + obj.capacity_memory


		#cpu_task = 0.
		#mem_task = 0.

		n_hists = 0
		max_hist = 0

		alpha = 2./(5. + 1.)
		l = [1., -5., 10., -10., 5.]
		#l = [-1., 10., -45., 120., -210., 252., -210., 120., -45., 10.]
		kl = len(l)

		for task in self.tasks:

			obj = self.tasks[task]
			len_hist = len(self.hist[task])
			max_hist = max(len_hist, max_hist)	

			if len_hist >= 150:

				n_hists = n_hists + 1
	
				if self.n_writes <= 100:
					self.n_writes = self.n_writes + 1

					f = open("log/tasks/task." + task + ".log", "w+")
	
					pred_5_cpu = 0.
					pred_5_mem = 0.

					pred_5_cpu_mov = 0.
					pred_5_mem_mov = 0.

					pred_5_cpu_mov_exp = 0.
					pred_5_mem_mov_exp = 0.

					pred_cpu_lagrange = 0.
					pred_mem_lagrange = 0.

					i = 0
					for tup in self.hist[task]:

						lst = self.hist[task]

						if i >= 5:
							pred_5_cpu = sum([t[0] for t in lst[(i - 5):i]])/5.
							pred_5_mem = sum([t[1] for t in lst[(i - 5):i]])/5.
							
							pred_5_cpu_mov = sum([(6 - j) * lst[i - j][0] for j in range(1,6)])/15.
							pred_5_mem_mov = sum([(6 - j) * lst[i - j][1] for j in range(1,6)])/15.

							pred_5_cpu_mov_exp = lst[i - 1][0]
							pred_5_mem_mov_exp = lst[i - 1][1]
							for k in range(2,6):
								pred_5_cpu_mov_exp = pred_5_cpu_mov_exp * (1. - alpha) + alpha * lst[i - k][0]
								pred_5_mem_mov_exp = pred_5_mem_mov_exp * (1. - alpha) + alpha * lst[i - k][1]


						if i >= kl:

							pred_cpu_lagrange = 0.
							pred_mem_lagrange = 0.

							for k in range(1, kl + 1):
								pred_cpu_lagrange = pred_cpu_lagrange + l[kl - k]*lst[i - k][0]
								pred_mem_lagrange = pred_mem_lagrange + l[kl - k]*lst[i - k][1]

						i = i + 1
						f.write("%f %f %f %f %f %f %f %f %f %f\n" % (tup[0], tup[1], pred_5_cpu, pred_5_mem, pred_5_cpu_mov, pred_5_mem_mov,
						 pred_5_cpu_mov_exp, pred_5_mem_mov_exp, pred_cpu_lagrange, pred_mem_lagrange))

					f.close()

				self.hist[task] = []

		print "# n_hists = %d; max = %d; n_rem = %d" % (n_hists, max_hist, n_rem)
				

		#	cpu_task = cpu_task + obj.CPU_usage
		#	mem_task = mem_task + obj.mem_usage

		#strng = '%f %f\n' % (cpu_task / cpu, mem_task / mem)
		
		#self.logf.write(strng)
		#print strng 

		#self.__generate_output()

		self.total_tasks       = len(self.tasks)
		self.machines_not_used = len(self.machines)

		#self.tasks.clear()

	def add_machine_event(self, mac):
		if mac.event_type == mac.ADD_EVENT:
			self.machines[mac.machine_ID] = mac
		elif mac.event_type == mac.UPDATE_EVENT:
			if mac.machine_ID in self.machines:
				self.machines[mac.machine_ID].capacity_CPU    = mac.capacity_CPU
				self.machines[mac.machine_ID].capacity_memory = mac.capacity_memory
		else:
			del self.machines[mac.machine_ID]

	def add_task_usage(self, task):
		if task.getID() in self.tasks:

			if self.tasks[task.getID()].last_round == (self.n_round + 1):
				cpu = max(self.tasks[task.getID()].CPU_usage, task.CPU_usage)
				mem = max(self.tasks[task.getID()].mem_usage, task.mem_usage)
			else:
				cpu = task.CPU_usage
				mem = task.mem_usage
				
			self.tasks[task.getID()].CPU_usage = cpu
			self.tasks[task.getID()].mem_usage = mem
		else:
			self.tasks[task.getID()] = task
			self.hist[task.getID()]  = []

		task_obj            = self.tasks[task.getID()]
		task_obj.last_round = self.n_round + 1
