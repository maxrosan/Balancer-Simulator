
import methods.loadbalancingalgorithm
from pulp import *
import commands
from xml.etree.ElementTree import ElementTree
import time

class GLPK(methods.loadbalancingalgorithm.LoadBalancingAlgorithm):

	log_path = "."

	problemFileName = ""
	scriptFileName = ""
	resultFileName = ""
	idInstance = ""

	def __init__(self, prediction, migration, log_path, relax = False):
		
		methods.loadbalancingalgorithm.LoadBalancingAlgorithm.__init__(self, prediction, migration)

		self.log_path = log_path
		self.relax = relax

	def __copy_cplex_script(self):

		print "Copying CPLEX script"

		self.__write_cplex_script()

		cplex_script_copied = False

		while not cplex_script_copied:
			try:
				self.exec_cmd("scp -C tmp/" + self.scriptFileName + " maxrosan@ime:")
				cplex_script_copied = True
			except Exception, e:
				print "Copying failed, trying again..."
				print e
				time.sleep(2)

	def __define_id_instance(self, n_VMs, n_servers):
		self.idInstance = str(n_VMs) + "_" + str(n_servers)

	def __write_cplex_script(self):

		self.problemFileName = "problem_" + self.idInstance + ".lp"
		self.scriptFileName = "script_" + self.idInstance + ".cplex"
		self.resultFileName = "results_" + self.idInstance + ".sol"
		
		cplexFile = open("tmp/" + self.scriptFileName, "w+")

		cplexFile.write("read " + self.problemFileName + "\n")
		cplexFile.write("set logfile /var/tmp/mr/log/cplex_log.log" + "\n")
		cplexFile.write("set threads 15" + "\n")
		cplexFile.write("set workdir /var/tmp/mr/" + "\n")
		cplexFile.write("set workmem 80000" + "\n")
		cplexFile.write("optimize" + "\n")
		cplexFile.write("write " + self.resultFileName + "\n")
		cplexFile.write("quit\n")

		cplexFile.close()

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


		#print [ self.tasks[t].age_round for t in tasks ]

		for i in range(0, n_VMs):
			_var = []
			_y   = []
			t    = self.tasks[tasks[i]]

			for j in range(0, n_servers):

				if not self.relax:
					_var.append(LpVariable("x[" + str(i) + "][" + str(j) + "]", 0, 1, "Integer"))
				else:
					_var.append(LpVariable("x[" + str(i) + "][" + str(j) + "]", 0., 1.))

				_y.append(0 if self.get_task(tasks[i]).mig_origin == macs[j] or t.age_round == 0 else 1)

			y.append(_y)
			x.append(_var)

		#print y

		for j in range(0, n_servers):

			#if not self.relax:
			z.append(LpVariable("z[" + str(j) + "]", 0, 1, "Integer"))
			#else:
			#	z.append(LpVariable("z[" + str(j) + "]", 0., 1.))

			m = self.machines[macs[j]]
			if m.CPU_usage > 0.25:
				W_cpu.append(self.W_cpu_g_25)
				W_on.append(self.W_on_g_25)
			else:
				W_cpu.append(self.W_cpu_l_25)
				W_on.append(self.W_on_l_25)


		print "Defining function [ %d ] [ %d ]" % (n_VMs, n_servers)

		prob += sum([z[j] * W_on[j] + sum( [x[i][j]  *  ( (self.tasks[tasks[i]].CPU_usage / self.machines[macs[j]].capacity_CPU) * W_cpu[j] + y[i][j] * self.W_mig ) for i in range(0, len(tasks))]) for j in range(0, len(macs))])

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

		self.__define_id_instance(n_VMs, n_servers)
		self.__copy_cplex_script()

		solfn = self.log_path + "/" + self.problemFileName

		resultFileName = self.resultFileName

		print "Problem saved in " + solfn

		prob.writeLP(solfn)

		try:
			self.exec_cmd("scp -C " + solfn + " maxrosan@ime:")
			self.exec_cmd("ssh -p 31001 maxrosan@localhost \"if [ -e " + resultFileName + " ]; then rm " + resultFileName + "; fi;\"")
			self.exec_cmd("ssh -p 31001 maxrosan@localhost \"nohup sh -c cplex < ~/" + self.scriptFileName + " 2&>1 > /dev/null &\"")
			
			while int(self.exec_cmd_return("ssh -p 31001 maxrosan@localhost \"if [ -e " + resultFileName + " ]; then echo 1; else echo 0; fi;\"")) == 0:
				print "Waiting results [%d]" % (self.n_round)
				time.sleep(1)

			self.exec_cmd("scp maxrosan@ime:~/" + resultFileName + " .")

		except Exception, e:
			print e
			exit()

		tree = ElementTree()
		e = tree.parse(resultFileName)

		x_sol = []

		for i in range(0, n_VMs):
			x_sol.append([0] * n_servers)

		for var in e.iter("variable"):
			inds = var.get("name").split("_")
			if inds[0] == "x":
				if not self.relax:
					x_sol[int(inds[1])][int(inds[3])] = (int) (round(float(var.get("value"))))
				else:
					x_sol[int(inds[1])][int(inds[3])] = float(var.get("value"))

		for i in range(0, n_VMs):

			j_max = 0
			for j in range(1, n_servers):
				if x_sol[i][j] > x_sol[i][j_max]:
					j_max = j


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

	def exec_cmd_return(self, cmd):
		ex = commands.getstatusoutput(cmd)
		return ex[1]