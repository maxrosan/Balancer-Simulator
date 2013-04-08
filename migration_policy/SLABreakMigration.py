import migration_policy.Migration

class SLABreakMigration(migration_policy.Migration.Migration):

	def __init__(self):
		migration_policy.Migration.Migration()

	def must_migrate(self, old_task, new_task, machine):

		if machine is None:
			return False

		return (not machine.can_run(new_task))
