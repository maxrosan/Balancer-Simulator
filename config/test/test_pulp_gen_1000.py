
import site, commands
import methods.glpkalgorithm, prediction.NoPrediction
import migration_policy.MachineUsageMigration, migration_policy.SLABreakMigration

def mac_key_sort(mac):
	gain = (mac.free_CPU()*mac.free_CPU() + mac.free_mem()*mac.free_mem())
	return gain

def task_key_sort(task):
	#gain = (task.CPU_usage*task.CPU_usage + task.mem_usage*task.mem_usage)
	#pun  = 1./(1. + abs(task.CPU_usage - task.mem_usage))
	return max(task.CPU_usage, task.mem_usage)


n_VMS = "1000_vms"

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
