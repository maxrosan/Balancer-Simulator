

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
	def balance_partial(method, conn, idwork, machines, tasks):
		
		## sorting the machine in non-incresing order using the CPU capacity value
		mac_list   = sorted(list(machines), key=lambda mac: mac.capacity_CPU, reverse=True)
		tasks_list = list(tasks)

		i = 0
		n_macs = len(machines)

		migrations = 0
		new_tasks  = 0

		task_machine_map = {}

		mac_used_list     = []
		mac_not_used_list = []

		for mac in mac_list:
			n_tasks = len(tasks_list)
			if n_tasks == 0:
				mac_not_used_list = mac_not_used_list + mac_list[i:]
				break

			#print "\r work %d processing machine %d of %d with %d tasks" % (idwork, i, n_macs, n_tasks),
			#sys.stdout.flush()
			
			i = i + 1

			tasks = ToyodaMethod.run(tasks_list, mac)

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

			mac.CPU_usage = cpu_usage
			mac.mem_usage = mem_usage

			if len(tasks) > 0:
				mac_used_list.append(mac)
			else:
				mac_not_used_list.append(mac)
				
			for t in tasks_to_remove:
				tasks_list.remove(t)

		return_value = (tasks_list, migrations, new_tasks, task_machine_map, mac_used_list, mac_not_used_list)


		if conn != None:
			conn.send(return_value)
			return None

		return return_value

	def __init__(self):
		loadbalacing.LoadBalacing.__init__(self)

	def __first_fit(self, macs, tasks):
		macs   = sorted(list(macs), key=lambda mac: (mac.capacity_CPU - mac.CPU_usage), reverse=True)
		tasks  = sorted(list(tasks), key=lambda task: task.CPU_usage, reverse=False)
		i = 0

		macs_used   = []
		tasks_sched = []

		for mac in macs:
			at_least_one_task_scheduled = False
			for task in tasks:
				if (mac.capacity_CPU - mac.CPU_usage) >= task.CPU_usage:
					i = i + 1
					at_least_one_task_scheduled = True
					mac.CPU_usage = mac.CPU_usage + task.CPU_usage
				else:
					break
			
			tasks = tasks[i:]

			if not at_least_one_task_scheduled:
				break
			else:
				macs_used.append(mac)

		return (mac_useds, tasks)

	def balance(self, machines_ready, tasks_to_run, state): 
		
		def work(method, conn, workn, macs, tasks):
			ToyodaMethod.balance_partial(method, conn, workn, macs, tasks)
	
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

		for mac in machines_ready:
			mac.CPU_usage = 0
			mac.mem_usage = 0

		procs = []
		conns = [None] * self.n_threads

		tasks_remaining          = []
		migrations_total         = 0
		new_tasks_total          = 0
		map_task_mac_final       = {}
		mac_used_list_final      = []
		mac_not_used_list_final  = []

		for i in range(0, self.n_threads):
			t = None
			if i < (self.n_threads - 1):
				conns[i], child_conn = multiprocessing.Pipe()
				p = multiprocessing.Process(target = work, 
				  args = (self, child_conn, i, mac_list[mac_div*i:mac_div*(i+1)], tasks_list[tasks_div*i:tasks_div*(i + 1)]))
				p.start()
				procs.append(p)
			else:
				(tasks_remaining, migrations_total, new_tasks_total, map_task_mac_final, mac_used_list_final, mac_not_used_list_final) = ToyodaMethod.balance_partial(self, None, i, mac_list[mac_div*i:n_macs], tasks_list[tasks_div*i:n_tasks])

		for i in range(0, self.n_threads - 1):
			(tasks, migrations, new_tasks, map_task_mac, mac_used_list, mac_not_used_list) = conns[i].recv()
			procs[i].join()

			tasks_remaining = tasks_remaining + tasks
			new_tasks_total = new_tasks_total + new_tasks

			map_task_mac_final.update(map_task_mac)

			migrations_total        = migrations_total + migrations
			mac_used_list_final     = mac_used_list_final + mac_used_list
			mac_not_used_list_final = mac_not_used_list_final + mac_not_used_list

		print "Checking"

		# check if there is task that wasn't scheduled, schedule those tasks.
		if len(tasks_remaining) > 0:
			(_, tasks_remaining) = self.__first_fit(mac_used_list_final, tasks_remaining)

		for task in tasks_to_run:
			if task.getID() in map_task_mac_final:
				task.machine_ID = map_task_mac_final[task.getID()]

		self.task_mapped_successfully = n_tasks - len(tasks_remaining)
		self.task_failed_to_map       = len(tasks_remaining)
		self.machines_used            = len(mac_used_list_final)
		self.machines_not_used        = len(mac_not_used_list_final)

		self.task_new                 = new_tasks_total
		self.n_migrations             = migrations_total

		print "#### %d %d %d" % (self.task_failed_to_map, self.machines_used, self.machines_not_used)

		exit()
