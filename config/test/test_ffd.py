
import site, commands
import methods.ffdbinpacking, prediction.NoPrediction
import migration_policy.MachineUsageMigration, migration_policy.SLABreakMigration

def mac_key_sort(mac):
	gain = (mac.free_CPU()*mac.free_CPU() + mac.free_mem()*mac.free_mem())
	return gain

def task_key_sort(task):
	cpu = task.CPU_usage + 1.
	return cpu

migration_policies = [ migration_policy.SLABreakMigration.SLABreakMigration() ]
method             = methods.ffdbinpacking.FFDBinPacking(prediction.NoPrediction.NoPrediction(), 
 migration_policies, mac_key_sort, task_key_sort, False)

host = commands.getoutput("hostname")

mapping_fname = "mapping_ffd_test.log"
balancing_fname = "balancing_ffd_test.log"

machine_events_folder = "machine_events"

dataset_path = ""
path_log     = ""

if host == "brucutu":

	dataset_path  = "/var/tmp/mr/gs_cluster/"
	path_log   = "/var/tmp/mr/log/"

elif host == "godzilla":

	dataset_path  = "/home/maxrosan/src/gs_cluster/"
	path_log   = "/home/maxrosan/simulator/PL/ssh/log/"	

else:
	dataset_path  = "/run/media/max/media/gsutil/resource/clusterdata-2011-1/"
	path_log      = "log/"

mapping_log   = path_log + mapping_fname
balancing_log = path_log + balancing_fname

total_time     = 2506199.0
