import migration_policy.Migration

import numpypy as numpy

class AverageMigration(migration_policy.Migration.Migration):

	def __init__(self, num):
		migration_policy.Migration.Migration()
		self.has_print_info = True

		self.num = num

	def must_migrate(self, old_task, new_task, machine):

		if machine is None:
			return False

		cpu_mean = mem_mean = 1.

		if not hasattr(old_task, "average"):
			old_task.average = []
		else:

			if len(old_task.average) == self.num:
				old_task.average.pop(0)

			cpu = max(2., new_task.CPU_usage / (old_task.CPU_usage if old_task.CPU_usage > 0. else 1.))
			mem = max(2., new_task.mem_usage / (old_task.mem_usage if old_task.mem_usage > 0. else 1.))

			old_task.average.append((cpu, mem))

			cpu_mean = numpy.mean([cpu_v for (cpu_v, _) in old_task.average])
			mem_mean = numpy.mean([mem_v for (_, mem_v) in old_task.average])

		if len(old_task.average) < self.num:
			return False

		old_cpu = new_task.CPU_usage
		old_mem = new_task.mem_usage

		new_task.CPU_usage = new_task.CPU_usage * cpu_mean
		new_task.mem_usage = new_task.mem_usage * mem_mean

		can_r = machine.can_run(new_task)

		new_task.CPU_usage = old_cpu
		new_task.mem_usage = old_mem

		return not can_r

	def print_info(self, tasks):
		for tid in list(tasks)[:5]:
			t = tasks[tid]
			if hasattr(t, "average"):
				print t.average
				
