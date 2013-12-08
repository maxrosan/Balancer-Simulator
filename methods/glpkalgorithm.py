
import methods.loadbalancingalgorithm
from pulp import *
import commands
from xml.etree.ElementTree import ElementTree

class GLPK(methods.loadbalancingalgorithm.LoadBalancingAlgorithm):

	log_path = "."

	def __init__(self, prediction, migration, log_path):
		
		methods.loadbalancingalgorithm.LoadBalancingAlgorithm.__init__(self, prediction, migration)

		self.log_path = log_path

	def add_new_task(self, task):
		pass

	def algorithm(self):

		macs  = list(self.machines)
		tasks = list(self.tasks)

		n_VMs = len(tasks)
		n_servers = len(macs)		

		prob = LpProblem("GLPK_problem", LpMinimize)

		print "Defining variables"

		x = []
		y = []
		z = []

		W_cpu = []
		W_on  = []

		W_cpu_l_25 = 0.133 * 300/3600.
		W_cpu_g_25 = 0.05 * 300/3600.

		W_on_l_25 = 18 * 300/3600.
		W_on_g_25 = 30 * 300/3600.

		W_mig     = 10 * 300/3600.

		print [ self.tasks[t].age_round for t in tasks ]

		for i in range(0, n_VMs):
			_var = []
			_y   = []
			t    = self.tasks[tasks[i]]

			for j in range(0, n_servers):
				_var.append(LpVariable("x[" + str(i) + "][" + str(j) + "]", 0, 1, "Integer"))
				_y.append(0 if self.get_task(tasks[i]).mig_origin == macs[j] or t.age_round == 0 else 1)

			y.append(_y)
			x.append(_var)

		print y

		for j in range(0, n_servers):
			z.append(LpVariable("z[" + str(j) + "]", 0, 1, "Integer"))

			m = self.machines[macs[j]]
			if m.CPU_usage > 0.25:
				W_cpu.append(W_cpu_g_25)
				W_on.append(W_on_g_25)
			else:
				W_cpu.append(W_cpu_l_25)
				W_on.append(W_on_l_25)


		print "Defining function [ %d ] [ %d ]" % (n_VMs, n_servers)

		prob += sum([z[j] * W_on[j] + sum( [x[i][j]  *  ( (self.tasks[tasks[i]].CPU_usage / self.machines[macs[j]].capacity_CPU) * W_cpu[j] + y[i][j] * W_mig ) for i in range(0, len(tasks))]) for j in range(0, len(macs))])

		print "Defining constraints"

		for i in range(0, n_VMs):
			t = self.tasks[tasks[i]]
			prob += sum([x[i][j] for j in range(0, n_servers)]) == 1.

		for j in range(0, n_servers):
			prob += sum([x[i][j]*self.tasks[tasks[i]].CPU_usage for i in range(0, n_VMs)]) - z[j] * self.machines[macs[j]].capacity_CPU    <= 0.
			prob += sum([x[i][j]*self.tasks[tasks[i]].mem_usage for i in range(0, n_VMs)]) - z[j] * self.machines[macs[j]].capacity_memory <= 0.

		#pulp.GLPK().solve(prob)

		#for v in prob.variables():
		#	print v.name, " = ", v.varValue

		solfn = self.log_path + "/problem.lp"

		prob.writeLP(solfn)

		try:
			self.exec_cmd("scp " + solfn + " maxrosan@ime:")
			self.exec_cmd("ssh -p 31001 maxrosan@localhost \"rm results.sol; cplex < ~/script.cplex\"")
			self.exec_cmd("scp maxrosan@ime:~/results.sol .")
		except Exception, e:
			print e
			exit()

		tree = ElementTree()
		e = tree.parse("results.sol")

		x_sol = []

		for i in range(0, n_VMs):
			x_sol.append([0] * n_servers)

		for var in e.iter("variable"):
			inds = var.get("name").split("_")
			if inds[0] == "x":
				x_sol[int(inds[1])][int(inds[3])] = (int) (round(float(var.get("value"))))

		for i in range(0, n_VMs):

			j_max = -1
			for j in range(0, n_servers):
				if x_sol[i][j] == 1:
					j_max = j
					break


			mac  = self.machines[macs[j_max]]
			task = self.tasks[tasks[i]]

			print "TASK " + tasks[i] + "(" + str(i) + ") => " + str(macs[j_max]) + "(" + str(j_max) + ")"
			
			if task.machine_ID != -1:
				self.machines[task.machine_ID].remove_task(task)
			
			mac.add_task(task)
			task.machine_ID = macs[j_max]


	def exec_cmd(self, cmd):
		ex = commands.getstatusoutput(cmd)
		if (ex[0] != 0):
			raise Exception("Failed to execute command '" + cmd + "': " + ex[1])
		else:
			print "CMD: " + cmd + " => " + ex[1]