

import loadbalacing, random, usageclass
import numpy
import math

import threading, multiprocessing, time, sys

# RandomMethod selects a task randomly to run
#
class ToyodaMethod(loadbalacing.LoadBalacing):

	@staticmethod
	def run(tasks, mac):
		
		n = len(tasks)

		Tu = []
		Td = range(0, n)
		Pu = numpy.zeros(2, int)
		Z  = 0
		X  = numpy.zeros(n, int)
		Tc = []
		B  = numpy.ones(2, float)

		P  = numpy.zeros((n, 2), float)
		G  = numpy.zeros(n, float)

		U  = numpy.zeros(n, float)

		for x in range(0, n):
			P[x][0] = tasks[x].CPU_usage / mac.capacity_CPU
			P[x][1] = tasks[x].mem_usage / mac.capacity_memory

		keep_going = True

		cnt = math.sqrt(2)

		#print "MAC = %d, ntasks = %d" % (mac.machine_ID, n)

		while keep_going :
	
			# step 2
			del Tc
			Tc = []
			
			for i in Td:
				if P[i][0] <= (1 - Pu[0]) and P[i][1] <= (1 - Pu[1]):
					Tc.append(i)

			#print "2"

			# step 3
			# terminate if Tc = empty
			if len(Tc) == 0:
				keep_going = False
			else:

				# step 4
				# (a)
				if (numpy.dot(Pu, Pu) == 0.):
					for i in Tc:
						d    = sum(P[i])
						G[i] = (tasks[i].CPU_usage * cnt)/d
				# (b)
				else:
					mod_Pu = math.sqrt(numpy.dot(Pu, Pu))
					E      = numpy.array(Pu * (1./mod_Pu))
				
					for i in Tc:
						d    = numpy.dot(P[i], E)
						G[i] = tasks[i].CPU_usage / d

				#print "4"

				# step 5
				v_max = -1
				i_max = 0
				for i in Tc:
					if G[i] > v_max:
						v_max = G[i]
						i_max = i


				#print "5"
				# step 6
				Tu.append(i_max)
				Td.remove(i_max)
				Pu = Pu + P[i_max]
				Z  = Z + tasks[i_max].CPU_usage


		#print "(%f, %f)" % (mac.capacity_CPU, mac.capacity_memory)
		#print Pu

		return Tu
		
	@staticmethod
	def balance_partial(method, idwork, machines, tasks):
		
		## sorting the machine in non-incresing order using the CPU capacity value
		mac_list   = sorted(list(machines), key=lambda mac: mac.capacity_CPU, reverse=True)
		tasks_list = list(tasks)
		mac_used   = 0

		i = 0
		n_macs = len(machines)

		migrations = 0
		new_tasks  = 0

		task_machine_map = {}

		print "%d ## Thread OK" % idwork

		for mac in mac_list:
			n_tasks = len(tasks_list)
			if n_tasks == 0:
				break

			#print "\r work %d processing machine %d of %d with %d tasks" % (idwork, i, n_macs, n_tasks),
			#sys.stdout.flush()
			
			i = i + 1

			tasks = ToyodaMethod.run(tasks_list, mac)

			if len(tasks) > 0:
				mac_used = mac_used + 1

			tasks_to_remove = []

			cpu_usage = 0
			mem_usage = 0
			for t in tasks:

				task = tasks_list[t]

				if task.machine_ID == -1:
					new_tasks = new_tasks + 1
				elif task.machine_ID != mac.machine_ID:
					migrations = migrations + 1
				
				task_machine_map[task.getID()] = mac.machine_ID

				cpu_usage       = cpu_usage + task.CPU_usage
				mem_usage       = mem_usage + task.mem_usage

				tasks_to_remove.append(task)
				


			#method.hash_queue.put((mac.machine_ID, cpu_usage, mem_usage))

			for t in tasks_to_remove:
				tasks_list.remove(t)

		print  "%d ## OK" % idwork

		method.queue.put((mac_used, tasks_list, migrations, task_machine_map))
		method.end_queue.put(idwork)

		print "%d @@" % idwork

	def __init__(self):
		loadbalacing.LoadBalacing.__init__(self)
		self.queue      = multiprocessing.Queue()
		self.end_queue  = multiprocessing.Queue()

	def balance(self, machines_ready, tasks_to_run, state): 
		
		def work(method, workn, macs, tasks):
			ToyodaMethod.balance_partial(method, workn, macs, tasks)
	
		self.n_threads  = self.n_jobs
	
		self.n_round = self.n_round + 1
		self.reset_stats()

		mac_list   = list(machines_ready)
		tasks_list = list(tasks_to_run)

		n_tasks   = len(tasks_to_run)
		n_macs    = len(mac_list)
		tasks_div = n_tasks / self.n_threads
		mac_div   = n_macs / self.n_threads


		if n_tasks == 0:
			return

		procs = []

		for i in range(0, self.n_threads):
			t = None
			if i < (self.n_threads - 1):
				p = multiprocessing.Process(target = work, 
				  args = (self, i, mac_list[mac_div*i:mac_div*(i+1)], tasks_list[tasks_div*i:tasks_div*(i + 1)]))
				p.start()
				procs.append(p)
			else:
				ToyodaMethod.balance_partial(self, i, mac_list[mac_div*i:n_macs], tasks_list[tasks_div*i:n_tasks])

		print "--OK 1--"

		while not self.end_queue.empty():
			proc_nid = self.end_queue.get(True)
			procs[proc_nid].terminate()

			print "Terminate %d" % proc_nid

		print "--OK 2--"

		tasks_remaining    = []
		mac_total_used     = 0
		migrations_total   = 0
		new_tasks_total    = 0
		map_task_mac_final = {}

		while not self.queue.empty():
			(mac_used, tasks, migrations, new_tasks, map_task_mac) = self.queue.get(False)
			
			tasks_remaining = tasks_remaining + tasks
			mac_total_used = mac_total_used + mac_used
			new_tasks_total = new_tasks_total + new_tasks
			map_task_mac_final.update(map_task_mac)

		for task in task_to_run:
			if task.getID() in map_task_mac_final:
				task.machine_ID = map_task_mac_final[task.getID()]

		self.task_mapped_successfully = n_tasks - len(tasks_remaining)
		self.task_failed_to_map       = len(tasks_remaining)
		self.machines_used            = mac_total_used
		self.machines_not_used        = n_macs - mac_total_used

		self.task_new                 = new_tasks_total
		self.n_migrations             = migrations_total
