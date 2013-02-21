

import loadbalacing
import numpy
import math

import threading, multiprocessing, time, sys

# RandomMethod selects a task randomly to run
#
class ToyodaMethod(loadbalacing.LoadBalacing):

	@staticmethod
	def run(m_tasks, tasks, mac):	

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
			P[x][0] = m_tasks[tasks[x]].CPU_usage / mac.free_CPU()
			P[x][1] = m_tasks[tasks[x]].mem_usage / mac.free_mem()

		keep_going = True

		cnt = math.sqrt(2)
		w_cpu = 0.6
		w_mem = 1 - w_cpu

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
						G[i] = ((m_tasks[tasks[i]].CPU_usage * w_cpu + m_tasks[tasks[i]].mem_usage * w_mem) * cnt)/d
				# (b)
				else:
					mod_Pu = math.sqrt(numpy.dot(Pu, Pu))
					E      = numpy.array(Pu * (1./mod_Pu))
				
					for i in Tc:
						d    = numpy.dot(P[i], E)
						G[i] = (m_tasks[tasks[i]].CPU_usage * w_cpu + m_tasks[tasks[i]].mem_usage * w_mem) / d

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
	def balance_partial(conn, m_mac_state, m_tasks_state, machines, tasks):
		
		mac_list = sorted(machines, key=lambda mac:m_mac_state[mac].free_CPU(), reverse=True)
		mac_list = [mac for mac in mac_list if m_mac_state[mac].free_CPU() > 1e-10 and m_mac_state[mac].free_mem() > 1e-10]

		tasks_list = list(tasks)

		macs = {}

		for mac in mac_list:
			tasks_to_sched = ToyodaMethod.run(m_tasks_state, tasks_list, m_mac_state[mac])

			if len(tasks_to_sched) == 0:
				break

			macs[mac] = []
			for t in tasks_to_sched:
				macs[mac].append(tasks_list[t])

			tasks_list_copy = list(tasks_list)
			for t in tasks_to_sched:
				tasks_list.remove(tasks_list_copy[t])


		if conn != None:
			conn.send(macs)
			return None

		return (macs)

	def __init__(self):
		loadbalacing.LoadBalacing.__init__(self)

		self.threshold_migration = 2
		self.machines_state      = {}
		self.tasks_state         = {}

	def add_machine_event(self, mac):
		if mac.event_type == mac.ADD_EVENT:
			self.machines_state[mac.machine_ID] = mac
		elif mac.event_type == mac.UPDATE_EVENT:
			self.machines_state[mac.machine_ID] = mac
		else:
			del self.machines_state[mac.machine_ID]

	def add_task_usage(self, task):
		if task.getID() in self.tasks_state and self.tasks_state[task.getID()].first_round == (self.n_round + 1):
			if task.CPU_usage >= self.tasks_state[task.getID()].CPU_usage:
				self.tasks_state[task.getID()] = task
		elif not (task.getID() in self.tasks_state):
			task.last_round = self.n_round + 1
			self.tasks_state[task.getID()] = task
			self.tasks_state[task.getID()].first_round = self.n_round + 1
		else:
			self.tasks_state[task.getID()].inc_age()
			self.tasks_state[task.getID()].last_round = self.n_round + 1

			old_task = self.tasks_state[task.getID()]

			if task.CPU_usage > old_task.CPU_usage or task.mem_usage > old_task.mem_usage:

				if old_task.machine_ID != -1:
					self.machines_state[old_task.machine_ID].remove_task(self.tasks_state, old_task.getID())

				old_task.CPU_usage = task.CPU_usage
				old_task.mem_usage = task.mem_usage
				old_task.altered = True

				self.tasks_state[task.getID()] = old_task

				if old_task.machine_ID != -1:
					self.machines_state[old_task.machine_ID].add_task(self.tasks_state, old_task.getID())

			else:
				old_task.altered = False
				self.tasks_state[task.getID()] = old_task

	def __clear_old_tasks(self):
		tasks = list(self.tasks_state)
		for task_ID in tasks:
			tak = self.tasks_state[task_ID]
			if tak.last_round < self.n_round:
				if tak.machine_ID != -1:
					self.machines_state[tak.machine_ID].remove_task(self.tasks_state, task_ID)
				del self.tasks_state[task_ID]

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
				res = res + 1
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

	def balance(self): 
		
		def work(conn, mmacs, mtasks, macs, tasks):
			ToyodaMethod.balance_partial(conn, mmacs, mtasks, macs, tasks)
	
		self.n_threads  = self.n_jobs
	
		self.n_round = self.n_round + 1
		self.reset_stats()
		self.task_new = self.__count_new_tasks()
		self.__clear_old_tasks()

		mac_list  = sorted(list(self.machines_state), key=lambda mac:self.machines_state[mac].free_CPU(), reverse=True)
		task_list = sorted([task for task in list(self.tasks_state) if self.tasks_state[task].machine_ID == -1],
		             key=lambda task:self.tasks_state[task].CPU_usage, reverse=True)

		procs     = []
		conns     = [None] * self.n_threads

		n_tasks   = len(task_list)
		n_macs    = len(mac_list)
		tasks_div = n_tasks / self.n_threads
		mac_div   = n_macs / self.n_threads


		print "Go! %d" % (self.n_jobs)
		##
		if len(task_list) > 10000:

			for i in range(0, self.n_jobs):
				t = None
				if i < (self.n_jobs - 1):
					conns[i], child_conn = multiprocessing.Pipe()
					p = multiprocessing.Process(target = work, 
					  args = (child_conn, self.machines_state, self.tasks_state, mac_list[mac_div*i:mac_div*(i+1)], task_list[tasks_div*i:tasks_div*(i + 1)]))
					p.start()
					procs.append(p)
				else:
					macs = ToyodaMethod.balance_partial(None, self.machines_state, self.tasks_state, mac_list[mac_div*i:n_macs], task_list[tasks_div*i:n_tasks])

					for mac_ID in macs:
						for task in macs[mac_ID]:
							self.machines_state[mac_ID].add_task(self.tasks_state, task)
							self.tasks_state[task].machine_ID = mac_ID
				
			for i in range(0, self.n_jobs-1):
				macs = conns[i].recv()
				procs[i].join()	

				for mac_ID in macs:
					for task in macs[mac_ID]:
						self.machines_state[mac_ID].add_task(self.tasks_state, task)
						self.tasks_state[task].machine_ID = mac_ID

		else:
			macs = ToyodaMethod.balance_partial(None, self.machines_state, self.tasks_state, mac_list, task_list)
			for mac_ID in macs:
				for task in macs[mac_ID]:
					self.machines_state[mac_ID].add_task(self.tasks_state, task)
					self.tasks_state[task].machine_ID = mac_ID
			
		##

		tasks_without_mac = [task for task in self.tasks_state if self.tasks_state[task].machine_ID == -1]
		if len(tasks_without_mac) > 0:
			macs_not_used = [mac for mac in self.machines_state if self.machines_state[mac].count_tasks() == 0]
			macs = ToyodaMethod.balance_partial(None, self.machines_state, self.tasks_state, mac_used, tasks_without_mac)
			for mac_ID in macs:
				for task in macs[mac_ID]:
					self.machines_state[mac_ID].add_task(self.tasks_state, task)
					self.tasks_state[task].machine_ID = mac_ID
					tasks_without_mac.remove(mac_ID)
		


		self.SLA_breaks               = self.__count_SLAs()
		(self.task_mapped_successfully, self.task_failed_to_map) = self.__count_mapped()
		(self.machines_used, self.machines_not_used)             = self.__count_macs()

		time.sleep(1)
