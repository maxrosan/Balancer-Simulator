

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

		for mac in mac_list:
			n_tasks = len(tasks_list)
			if n_tasks == 0:
				break

			print "\r work %d processing machine %d of %d with %d tasks" % (idwork, i, n_macs, n_tasks),
			sys.stdout.flush()
			
			i = i + 1

			tasks = ToyodaMethod.run(tasks_list, mac)

			if len(tasks) > 0:
				mac_used = mac_used + 1

			tasks_to_remove = []

			for t in tasks:
				tasks_to_remove.append(tasks_list[t])

			for t in tasks_to_remove:
				tasks_list.remove(t)


		method.queue.put(tasks_list)

	def __init__(self):
		loadbalacing.LoadBalacing.__init__(self)
		self.n_threads = 8
		self.queue     = multiprocessing.Queue()

	def balance(self, machines_ready, tasks_to_run, tasks_constraints): 
		
		def work(method, workn, macs, tasks):
			ToyodaMethod.balance_partial(method, workn, macs, tasks)
	
	
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

		for p in procs:
			p.join()

		tasks_remaining = []
		while not self.queue.empty():
			tasks_remaining.append(self.queue.get(False))

		print "tarefas restantes = ", tasks_remaining

		exit()
