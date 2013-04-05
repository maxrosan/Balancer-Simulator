
import migration_policy.Migration

class MachineUsageMigration(migration_policy.Migration.Migration):

	def __init__(self):
		migration_policy.Migration.Migration()

	def must_migrate(self, old_task, new_task, machine):

		if machine is None:
			return False

		cpu = max(1., machine.CPU_usage_real)
		mem = max(1., machine.mem_usage_real)

		usage = (cpu * mem) / (machine.capacity_CPU * machine.capacity_memory)

		return (usage < 0.3)
