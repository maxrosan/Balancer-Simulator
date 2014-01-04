
import site, commands
import methods.glpkalgorithm, prediction.NoPrediction
import migration_policy.MachineUsageMigration, migration_policy.SLABreakMigration

migration_policies = [ migration_policy.SLABreakMigration.SLABreakMigration() ]
method             = methods.glpkalgorithm.GLPK(prediction.NoPrediction.NoPrediction(), migration_policies,
	"/home/max/Src/gsutil/generated/10vms/log/")

host = commands.getoutput("hostname")

mapping_fname = "mapping_glpk_test.log"
balancing_fname = "balancing_glpk_test.log"

machine_events_folder = "machine_events"

dataset_path = ""
path_log     = ""

if host == "brucutu":

	dataset_path  = "/var/tmp/mr/gs_cluster/"
	path_log   = "/var/tmp/mr/log/"

elif host == "godzilla":

	dataset_path  = "/home/maxrosan/src/gs_cluster/"
	path_log   = "/home/maxrosan/simulator/Balancer-Simulator/log/"	

else:
	dataset_path  = "/home/max/Src/gsutil/generated/10vms/"
	path_log      = "/home/max/Src/gsutil/generated/10vms/log/"

mapping_log   = path_log + mapping_fname
balancing_log = path_log + balancing_fname

total_time     = 300 * 10
