
from pulp import *
import random

prob = LpProblem("test1", LpMinimize)

VMs = []

n_servers = 100
n_VMs     = 60

for i in range(0, n_VMs):

	cpu = random.random()
	mem = random.random()

	VMs.append((cpu, mem))

servers = []

for i in range(0, n_servers):
	servers.append((1., 1.))

print "Defining variables"

x = []
for i in range(0, n_VMs):
	_var = []
	for j in range(0, n_servers):
		_var.append(LpVariable("x[" + str(i) + "][" + str(j) + "]", 0, 1, "Integer"))
	x.append(_var)

#x = LpVariable("x", 0., 1.)

#print VMs
#print servers

#prob += x + 4*y + 9*z

print "Defining function"

prob += sum([sum( [x[i][j] * (VMs[i][0] / servers[j][0]) for i in range(0, n_VMs)]) for j in range(0, n_servers)])

print "Defining constraints"

for j in range(0, n_servers):
	prob += sum([x[i][j]*VMs[i][0] for i in range(0, n_VMs)]) <= servers[j][0]
	prob += sum([x[i][j]*VMs[i][1] for i in range(0, n_VMs)]) <= servers[j][1]

print "Defining constraints"

for i in range(0, n_VMs):
	prob += sum([x[i][j] for j in range(0, n_servers)]) == 1.


print "Problem defined"

#prob += x+y <= 5
#prob += x+z >= 10
#prob += -y+z == 7

#print prob

prob.writeLP("problem.lp")

GLPK().solve(prob)

for v in prob.variables():
	print v.name, " = ", v.varValue

print "obj = ", value(prob.objective)