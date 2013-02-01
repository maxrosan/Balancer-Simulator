

import loadbalacing, random, usageclass
import numpy
import math

# RandomMethod selects a task randomly to run
#
class ToyodaMethod(loadbalacing.LoadBalacing):

	def __init__(self):
		loadbalacing.LoadBalacing.__init__(self)
	

	def run(self, tasks, mac):
		
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


		print "(%f, %f)" % (mac.capacity_CPU, mac.capacity_memory)
		print Pu

		return Tu
		

	def balance(self, machines_ready, tasks_to_run, tasks_constraints): 
		
		self.n_round = self.n_round + 1
		self.reset_stats()

		## sorting the machine in non-incresing order using the CPU capacity value
		mac_list = sorted(list(mac_list), key=lambda mac: mac.capacity_CPU, reverse=True)
		tasks_list = list(tasks_to_run)

		if len(tasks_list) > 0:
			for mac in mac_list:
				tasks = self.run(tasks_list, mac)
				tasks_to_remove = []
				for t in tasks:
					tasks_to_remove.append(tasks_list[t])
				for t in tasks_to_remove:
					tasks_list.remove(t)
