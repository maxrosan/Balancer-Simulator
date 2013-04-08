
import methods.loadbalancingalgorithm
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

class ToyodaKnapsack(methods.loadbalancingalgorithm.LoadBalancingAlgorithm):
	
	def __init__(self, prediction, migration, n_threads, score_task_knapsack, mac_key_sort, task_key_sort):

		methods.loadbalancingalgorithm.LoadBalancingAlgorithm.__init__(self, prediction, migration)

		self.n_threads = n_threads
		self.score_task_knapsack = score_task_knapsack
		self.mac_key_sort = mac_key_sort
		self.task_key_sort = task_key_sort

	## privs

	def __div_list(self, lst):

		res = [None] * self.n_threads

		#for i in range(0, len(lst)):
		#	ind = i % self.n_threads
		#	if res[ind] == None:
		#		res[ind] = []
		#	res[ind].append(lst[i])

		n = len(lst)
		l = n / self.n_threads

		for i in range(0, self.n_threads):
			start  = i * l
			end    = (i + 1)*l
			res[i] = list(lst[start:end])

		res[self.n_threads - 1] = res[self.n_threads - 1] + list(lst[(self.n_threads * l):n])

		return res

	@staticmethod
	def __run(score_task_knapsack, m_tasks, tasks, mac):	

		n = len(tasks)

		Tu = []
		Td = range(0, n)
		Pu = numpy.zeros(2, float)
		Z  = 0
		X  = numpy.zeros(n, int)
		Tc = []
		B  = numpy.ones(2, float)

		P  = numpy.zeros((n, 2), float)
		G  = numpy.zeros(n, float)

		U  = numpy.zeros(n, float)

		for x in range(0, n):
			P[x][0] = m_tasks[tasks[x]].CPU_usage / mac.free_CPU()
			P[x][1] = m_tasks[tasks[x]].mem_usage / mac.free_mem()

		keep_going = True

		cnt = math.sqrt(2)
		#w_cpu = 0.6
		#w_mem = 1 - w_cpu

		#print "MAC = %d, ntasks = %d" % (mac.machine_ID, n)

		while keep_going :
	
			# step 2
			del Tc
			Tc = []
			
			for i in Td:
				if P[i][0] <= (1. - Pu[0]) and P[i][1] <= (1. - Pu[1]):
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
						G[i] = (score_task_knapsack(m_tasks[tasks[i]], mac) * cnt)/d
				# (b)
				else:
					mod_Pu = math.sqrt(numpy.dot(Pu, Pu))
					E      = numpy.array(Pu * (1./mod_Pu))
				
					for i in Tc:
						d    = numpy.dot(P[i], E)
						G[i] = score_task_knapsack(m_tasks[tasks[i]], mac) / d

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
				Z  = Z + m_tasks[tasks[i_max]].CPU_usage


		#print "(%f, %f)" % (mac.capacity_CPU, mac.capacity_memory)
		#print Pu

		return Tu

	@staticmethod
	def __balance_partial(score_task_knapsack, conn, map_mac, map_task, machines, tasks):
		
		print "processing %d %d" % (len(machines), len(tasks))

		mac_list = [mac for mac in machines if map_mac[mac].free_CPU() > 1e-10 and map_mac[mac].free_mem() > 1e-10]

		tasks_list = list(tasks)

		macs = {}

		for mac in mac_list:
			tasks_to_sched = ToyodaKnapsack.__run(score_task_knapsack, map_task, tasks_list, map_mac[mac])

			macs[mac] = []
			for t in tasks_to_sched:
				macs[mac].append(tasks_list[t])

			tasks_list_copy = list(tasks_list)
			for t in tasks_to_sched:
				tasks_list.remove(tasks_list_copy[t])

			if len(tasks_list) == 0:
				break


		if conn != None:
			conn.send(macs)
			return None

		return (macs)

	@staticmethod
	def __work(score_task_knapsack, conn, mmacs, mtasks, macs, tasks):
		ToyodaKnapsack.__balance_partial(score_task_knapsack, conn, mmacs, mtasks, macs, tasks)

	def __update_map(self, macs):
		for mac_ID in macs:
			for task in macs[mac_ID]:
				self.machines[mac_ID].add_task(self.tasks[task])
				self.tasks[task].machine_ID = mac_ID

	def __run_algorithm(self, mac_list, task_list):
		procs     = []
		conns     = [None] * self.n_threads

		n_tasks   = len(task_list)
		n_macs    = len(mac_list)
		tasks_div = n_tasks / self.n_threads
		mac_div   = n_macs / self.n_threads


		if n_tasks == 0 or n_macs == 0:
			print "No %d %d" % (n_macs, n_tasks)
			return

		print "Go! %d %d %d" % (self.n_threads, n_macs, n_tasks)
		##
		if len(task_list) > 30000:

			print "MP"

			mac_lsts  = self.__div_list(mac_list)
			task_lsts = self.__div_list(task_list)									

			for i in range(0, self.n_threads):
				t = None
				if i < (self.n_threads - 1):
					conns[i], child_conn = multiprocessing.Pipe()
					p = multiprocessing.Process(target = ToyodaKnapsack.__work, 
					  args = (self.score_task_knapsack, child_conn, self.machines, self.tasks, mac_lsts[i], task_lsts[i]))
					p.start()
					procs.append(p)
				else:
					macs = ToyodaKnapsack.__balance_partial(self.score_task_knapsack, None, self.machines, self.tasks, mac_lsts[i], task_lsts[i])

					self.__update_map(macs)
				
			for i in range(0, self.n_threads-1):
				macs = conns[i].recv()
				procs[i].join()	
				self.__update_map(macs)
		else:
			print "UP"
			macs = ToyodaKnapsack.__balance_partial(self.score_task_knapsack,
			          None, self.machines, self.tasks, mac_list, task_list)
			self.__update_map(macs)

	def __ffd_algorithm(self, macs, tasks):

		tasks_sorted = sorted(tasks, key=lambda task_ID: self.task_key_sort(self.tasks[task_ID]), reverse=True)

		macs_sorted  = sorted([mac for mac in macs if self.machines[mac].count_tasks() > 0], 
			 key=lambda mac_ID: self.task_key_sort(self.machines[mac_ID]), reverse=True) + \
			 sorted([mac for mac in macs if self.machines[mac].count_tasks() == 0],
			  key=lambda mac_ID: self.task_key_sort(self.machines[mac_ID]), reverse=True)

		for task in tasks_sorted:
			for mac in macs_sorted:
				if self.machines[mac].can_run(self.tasks[task]):

					obj            = self.tasks[task]
					obj.machine_ID = mac

					self.machines[mac].add_task(obj)

					break


	## end privs

	def add_new_task(self, task):
		pass

	def algorithm(self):

		for mac in self.machines:
			if self.machines[mac].SLA_break():
				for task in list(self.machines[mac].tasks):
					self.migrate(self.tasks[task])
					self.machines[mac].remove_task(self.tasks[task])

		macs = sorted([mac_id for mac_id in self.machines if self.machines[mac_id].n_tasks > 0],
		    key=lambda mac_id:self.mac_key_sort(self.machines[mac_id]), reverse=True) + \
		  sorted([mac_id for mac_id in self.machines if self.machines[mac_id].n_tasks == 0],
		    key=lambda mac_id:self.mac_key_sort(self.machines[mac_id]), reverse=True)

		tasks = sorted([task for task in list(self.tasks) if self.tasks[task].machine_ID == -1],
                    key=lambda task:self.task_key_sort(self.tasks[task]), reverse=True)

		if self.n_round == -1:
			self.__ffd_algorithm(macs, tasks)
		else:
			self.__run_algorithm(macs, tasks)

			macs = sorted([mac_id for mac_id in self.machines if self.machines[mac_id].n_tasks > 0],
			    key=lambda mac_id:self.mac_key_sort(self.machines[mac_id]), reverse=True) + \
			  sorted([mac_id for mac_id in self.machines if self.machines[mac_id].n_tasks == 0],
			    key=lambda mac_id:self.mac_key_sort(self.machines[mac_id]), reverse=True)

			tasks = sorted([task for task in list(self.tasks) if self.tasks[task].machine_ID == -1],
        	            key=lambda task:self.task_key_sort(self.tasks[task]), reverse=True)

			for task_id in tasks:
				mac_min = None
				mac_val = 100
				task    = self.tasks[task_id]
			
				for mac_id in self.machines:
					mac = self.machines[mac_id]
					dcpu = mac.free_CPU() - task.CPU_usage
					dmem = mac.free_mem() - task.mem_usage
					val = dcpu*dcpu + dmem*dmem

					if not mac.can_run(task):
						val = val + 4. + mac.n_tasks

					if val < mac_val:
						mac_val = val
						mac_min = mac

				if mac_min != None:
					mac_min.add_task(task)
					task.machine_ID = mac_min.machine_ID
			
