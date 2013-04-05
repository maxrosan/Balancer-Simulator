
import migration_policy.Migration

class MachineUsageMigration(methods.Migration.Migration):

	def __init__(self):
		methods.Migration.Migration(self)

	def must_migrate(old_task, new_task, machine):

		if machien == None:
			return False

		cpu = max(1., machine.CPU_usage_real)
		mem = max(1., machine.mem_usage_real)

		usage = (cpu * mem) / (machine.capacity_CPU * machine.capacity_memory)

		return (usage < 0.3)
