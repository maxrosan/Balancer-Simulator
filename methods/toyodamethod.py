

import loadbalacing
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

# RandomMethod selects a task randomly to run
#
class ToyodaMethod(loadbalacing.LoadBalacing):


	@staticmethod
	def run(score_task_knapsack, m_tasks, tasks, mac):	

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
	def balance_partial(mac_key_sort, score_task_knapsack, conn, m_mac_state, m_tasks_state, machines, tasks):
		
		print "processing %d %d" % (len(machines), len(tasks))

		mac_list = [mac for mac in machines if m_mac_state[mac].free_CPU() > 1e-10 and m_mac_state[mac].free_mem() > 1e-10]

		tasks_list = list(tasks)

		macs = {}

		for mac in mac_list:
			tasks_to_sched = ToyodaMethod.run(score_task_knapsack, m_tasks_state, tasks_list, m_mac_state[mac])

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

	def __init__(self, threshold, mac_key_sort, task_key_sort, score_task_knapsack, mac_key_pq, method_sel_macs, must_migrate):
		loadbalacing.LoadBalacing.__init__(self)

		self.machines_state      = {}
		self.tasks_state         = {}
		self.tasks_input         = {}

		self.method_sel_macs     = method_sel_macs

		if method_sel_macs == 'priority_queue':
			self.pq           = Queue.PriorityQueue(0)
		elif method_sel_macs == 'list':
			self.pq           = []
		elif method_sel_macs == 'nothing':
			self.pq           = None
		else:
			print "Unknown method"
			exit()

		self.threshold_migration = int(threshold)
		self.mac_key_sort        = mac_key_sort
		self.task_key_sort       = task_key_sort
		self.score_task_knapsack = score_task_knapsack
		self.mac_key_pq          = mac_key_pq

		self.must_migrate        = must_migrate


	def add_machine_event(self, mac):
		if mac.event_type == mac.ADD_EVENT:
			self.machines_state[mac.machine_ID] = mac
		elif mac.event_type == mac.UPDATE_EVENT:

			if self.machines_state[mac.machine_ID].capacity_CPU > mac.capacity_CPU or self.machines_state[mac.machine_ID].capacity_memory > mac.capacity_memory:
				for task in self.machines_state[mac.machine_ID].tasks:
					self.migrate(self.tasks_state[task])
					self.machines_state[mac.machine_ID].remove_task(self.tasks_state[task])

			self.machines_state[mac.machine_ID].capacity_CPU    = mac.capacity_CPU
			self.machines_state[mac.machine_ID].capacity_memory = mac.capacity_memory

		else:
			for task in self.machines_state[mac.machine_ID].tasks:
				self.migrate(self.tasks_state[task])

			del self.machines_state[mac.machine_ID]

	def add_task_usage(self, task):
		if task.getID() in self.tasks_input:
			self.tasks_input[task.getID()].CPU_usage_real = max(self.tasks_input[task.getID()].CPU_usage_real, task.CPU_usage_real)
			self.tasks_input[task.getID()].mem_usage_real = max(self.tasks_input[task.getID()].mem_usage_real, task.mem_usage_real)
		else:
			self.tasks_input[task.getID()] = task

	def migrate(self, task):
		task.move = True
		task.mig_origin = task.machine_ID
		task.machine_ID = -1

	def calculatePrediction(self):
		## there is no prediction yet

		for task_ID in self.tasks_input:
			self.tasks_input[task_ID].CPU_usage = self.tasks_input[task_ID].CPU_usage_real 
			self.tasks_input[task_ID].mem_usage = self.tasks_input[task_ID].mem_usage_real

		##

	def removePrediction(self, task_ID):
		pass

	def __update_tasks(self):

		print "Updating"

		# Remove old tasks
		for task_ID in list(self.tasks_state):
			task = self.tasks_state[task_ID]
			if not (task_ID in self.tasks_input):
				if task.machine_ID != -1:
					if task.machine_ID in self.machines_state:
						self.machines_state[task.machine_ID].remove_task(self.tasks_state[task_ID])
				
				self.removePrediction(task_ID)
				del self.tasks_state[task_ID]

		print "Old done!"

		self.calculatePrediction()

		for task_ID in self.tasks_input:

			if not (task_ID in self.tasks_state):
				task = self.tasks_state[task_ID] = self.tasks_input[task_ID]
				task.first_round = (self.n_round + 1)
				task.last_round  = (self.n_round + 1)
		
				if self.method_sel_macs == 'priority_queue':
	
					if not self.pq.empty():
						mac = self.pq.get()[1]
						while not (mac.machine_ID in self.machines_state):
							mac = self.pq.get()[1]
						if mac.can_run(task):
							mac.add_task(task)
							task.machine_ID = mac.machine_ID
						self.pq.put((-self.mac_key_pq(mac) , mac))

				elif self.method_sel_macs == 'list':

					mac_value = 0
					mac_max   = None

					for mac in self.pq:
						if mac.can_run(task) and self.score_task_knapsack(task, mac) > mac_value:
							mac_value = self.score_task_knapsack(task, mac)
							mac_max   = mac

					if mac_max != None:
						mac_max.add_task(task)
						task.machine_ID = mac_max.machine_ID

				elif self.method_sel_macs == 'nothing':
					pass
						
			else:
				new_task = self.tasks_input[task_ID]
				old_task = self.tasks_state[task_ID]
			
				old_task.inc_age()
				old_task.last_round = self.n_round + 1
				from_mach = old_task.machine_ID

				if not (from_mach in self.machines_state):
					old_task.machine_ID = -1

				if old_task.machine_ID != -1:

					self.machines_state[from_mach].remove_task(old_task)
					old_task.machine_ID = -1

					old_task.CPU_usage_real = new_task.CPU_usage_real
					old_task.mem_usage_real = new_task.mem_usage_real

					if old_task.age_round <= self.threshold_migration:
						#if (old_task.CPU_usage < new_task.CPU_usage or old_task.mem_usage < new_task.mem_usage):

						if self.must_migrate(old_task, task, self.machines_state[from_mach]) or \
						 (not self.machines_state[from_mach].can_run(new_task)):
							self.migrate(old_task)
						else:
							old_task.move       = False
							old_task.machine_ID = from_mach
							self.machines_state[from_mach].add_task(new_task)
					else:
						old_task.age_round = 1
						self.migrate(old_task)

				old_task.CPU_usage = new_task.CPU_usage
				old_task.mem_usage = new_task.mem_usage

				old_task.CPU_usage_real = new_task.CPU_usage_real
				old_task.mem_usage_real = new_task.mem_usage_real


		print "New tasks ready!"

		self.tasks_input.clear()

	def __count_new_tasks(self):
		new_tasks = 0
		for task_ID in self.tasks_state:
			if self.tasks_state[task_ID].age_round == 0:
				new_tasks = new_tasks + 1
		return new_tasks

	def __count_SLAs(self):
		res = 0
		for mac_ID in self.machines_state:
			if self.machines_state[mac_ID].SLA_break():
				res = res + self.machines_state[mac_ID].n_tasks
		return res

	def __count_mapped(self):
		res_y = 0
		res_n = 0
		for task_ID in self.tasks_state:
			if self.tasks_state[task_ID].machine_ID == -1:
				res_n = res_n + 1
			else:
				res_y = res_y + 1
		return (res_y, res_n)

	def __count_macs(self):
		res_y = 0
		res_n = 0
		
		for mac_ID in self.machines_state:
			if self.machines_state[mac_ID].count_tasks() > 0:
				res_y = res_y + 1
			else:
				res_n = res_n + 1

		return (res_y, res_n)

	def __count_migrations(self):
		res = 0

		for task_ID in self.tasks_state:
			task = self.tasks_state[task_ID]
			if task.machine_ID != -1 and task.move and task.mig_origin != task.machine_ID:
				task.move       = False
				res             = res + 1
				task.mig_origin = -1

		return res

	def __calc_heap(self):

		if self.method_sel_macs == 'priority_queue':

			print "Calculating PQ"
			while not self.pq.empty():
				self.pq.get()
			for mac in self.machines_state:
				if self.machines_state[mac].n_tasks != 0:
					self.pq.put((-self.mac_key_pq(self.machines_state[mac]), self.machines_state[mac])) 
			print "done"

		elif self.method_sel_macs == 'list':
			self.pq = [self.machines_state[mac] for mac in self.machines_state if self.machines_state[mac].n_tasks != 0]
		elif self.method_sel_macs == 'nothing':
			pass

	def __calc_usage(self):
		print "Printing tasks......",

		self.mac_usage.clear()

		usage_vec = []
		usage_cpu = []
		usage_mem = []

		for mac in self.machines_state:
			lst_tasks = []
			if self.machines_state[mac].n_tasks > 0:
				self.mac_usage[mac] = (self.machines_state[mac], lst_tasks)
				for task in self.machines_state[mac].tasks:
					lst_tasks.append(self.tasks_state[task])

				mac_obj = self.mac_usage[mac][0]
				usage_vec.append((mac_obj.CPU_usage_real * mac_obj.mem_usage_real) / (mac_obj.capacity_CPU * mac_obj.capacity_memory))
				usage_cpu.append(mac_obj.CPU_usage_real / mac_obj.capacity_CPU)
				usage_mem.append(mac_obj.mem_usage_real / mac_obj.capacity_memory)

		if len(usage_vec) > 0:
			self.usage_mean_per = numpy.mean(usage_vec)
			self.usage_stan_per = numpy.std(usage_vec)
			self.usage_CPU_mean = numpy.mean(usage_cpu)
			self.usage_mem_mean = numpy.mean(usage_mem)

		print "OK"

	def __update_macs(self):

		for mac_ID in self.machines_state:
			self.machines_state[mac_ID].calculate_consumption(self.tasks_state)

	def beforeBalancing(self):
		pass

	def balance(self): 
		
		migrations = 0

		def work(conn, mmacs, mtasks, macs, tasks):
			ToyodaMethod.balance_partial(self.mac_key_sort, self.score_task_knapsack, conn, mmacs, mtasks, macs, tasks)

		def update_map(macs):
			for mac_ID in macs:
				for task in macs[mac_ID]:
					self.machines_state[mac_ID].add_task(self.tasks_state[task])
					self.tasks_state[task].machine_ID = mac_ID

		def div_list(lst):
			res = [None] * self.n_jobs

			for i in range(0, len(lst)):
				#ind = i % self.n_jobs
				ind = i / self.n_jobs
				if res[ind] == None:
					res[ind] = []
				res[ind].append(lst[i])

			return res

		def bal(mac_list, task_list):
			procs     = []
			conns     = [None] * self.n_threads

			n_tasks   = len(task_list)
			n_macs    = len(mac_list)
			tasks_div = n_tasks / self.n_threads
			mac_div   = n_macs / self.n_threads


			if n_tasks == 0 or n_macs == 0:
				print "No %d %d" % (n_macs, n_tasks)
				return

			print "Go! %d %d %d" % (self.n_jobs, n_macs, n_tasks)
			##
			if len(task_list) > 10000:

				print "MP"

				mac_lsts  = div_list(mac_list)
				task_lsts = div_list(task_list)

				for i in range(0, self.n_jobs):
					t = None
					if i < (self.n_jobs - 1):
						conns[i], child_conn = multiprocessing.Pipe()
						p = multiprocessing.Process(target = work, 
						  args = (child_conn, self.machines_state, self.tasks_state, mac_lsts[i], task_lsts[i]))
						p.start()
						procs.append(p)
					else:
						macs = ToyodaMethod.balance_partial(self.mac_key_sort, self.score_task_knapsack, 
						        None, self.machines_state, self.tasks_state, mac_lsts[i], task_lsts[i])

						update_map(macs)
				
				for i in range(0, self.n_jobs-1):
					macs = conns[i].recv()
					procs[i].join()	
					update_map(macs)

			else:
				print "UP"

				macs = ToyodaMethod.balance_partial(self.mac_key_sort, self.score_task_knapsack,
				          None, self.machines_state, self.tasks_state, mac_list, task_list)

				update_map(macs)

		###

		self.__update_tasks()
		#self.__update_macs()

		s_time = time.time()
	
		self.n_threads  = self.n_jobs
	
		self.n_round = self.n_round + 1
		self.reset_stats()
		self.task_new = self.__count_new_tasks()

		self.beforeBalancing()

		for mac in self.machines_state:
			if self.machines_state[mac].SLA_break():
				for task in self.machines_state[mac].tasks:
					self.migrate(self.tasks_state[task])
					self.machines_state[mac].remove_task(self.tasks_state[task])

		for i in range(0, 2):


			print "Processing %d" % (i)

			macs = sorted([mac_id for mac_id in self.machines_state if self.machines_state[mac_id].n_tasks > 0],
			              key=lambda mac_id:self.mac_key_sort(self.machines_state[mac_id]), reverse=True) + \
			       sorted([mac_id for mac_id in self.machines_state if self.machines_state[mac_id].n_tasks == 0],
		        	      key=lambda mac_id:self.mac_key_sort(self.machines_state[mac_id]), reverse=True)

			tasks = sorted([task for task in list(self.tasks_state) if self.tasks_state[task].machine_ID == -1],
		                    key=lambda task:self.task_key_sort(self.tasks_state[task]), reverse=True)

			bal(macs, tasks)
				
		# Gather the task weren't mapped earlier
		tasks_without_mac = [task for task in self.tasks_state if self.tasks_state[task].machine_ID == -1]
		if len(tasks_without_mac) > 0:

			print "Remaining tasks"

			#mac_n_used  = sorted([mac for mac in self.machines_state if self.machines_state[mac].n_tasks == 0],
			#                     key=lambda mac:self.mac_key_sort(self.machines_state[mac]), reverse=True)

			task_wo_mac = sorted([task for task in self.tasks_state if self.tasks_state[task].machine_ID == -1],
			                     key=lambda task:self.task_key_sort(self.tasks_state[task]), reverse=True)
		
			print "WO MAC: ", 

			for task_id in task_wo_mac:
				mac_min = None
				mac_val = 100
				task    = self.tasks_state[task_id]
			
				for mac_id in self.machines_state:
					mac = self.machines_state[mac_id]
					dcpu = mac.free_CPU() - task.CPU_usage
					dmem = mac.free_mem() - task.mem_usage
					val = dcpu*dcpu + dmem*dmem

					if not mac.can_run(task):
						val = val + 4.

					if val < mac_val:
						mac_val = val
						mac_min = mac

				if mac_min != None:
					mac_min.add_task(task)
					task.machine_ID = mac_min.machine_ID
					print "(%f, %f / %f, %f / %f) " % (task.CPU_usage, task.mem_usage, mac.free_CPU(), mac.free_mem(), val), 

			print " "

		
		self.__calc_heap()

		self.total_time = time.time() - s_time

		self.__calc_usage()

		self.total_tasks              = len(self.tasks_state)
		self.SLA_breaks               = self.__count_SLAs()
		self.n_migrations             = self.__count_migrations()
		(self.task_mapped_successfully, self.task_failed_to_map) = self.__count_mapped()
		(self.machines_used, self.machines_not_used)             = self.__count_macs()
