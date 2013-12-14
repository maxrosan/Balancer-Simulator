
import site, commands
import methods.glpkalgorithm, prediction.NoPrediction
import migration_policy.MachineUsageMigration, migration_policy.SLABreakMigration

n_VMS = "100_vms"

migration_policies = [ migration_policy.SLABreakMigration.SLABreakMigration() ]
method             = methods.glpkalgorithm.GLPK(prediction.NoPrediction.NoPrediction(), migration_policies,
	"/run/media/max/media/gsutil/generated/" + n_VMS + "/log")

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
	dataset_path  = "/run/media/max/media/gsutil/generated/" + n_VMS + "/"
	path_log      = "/run/media/max/media/gsutil/generated/" + n_VMS + "/log/"

mapping_log   = path_log + mapping_fname
balancing_log = path_log + balancing_fname

total_time     = 300 * 10
