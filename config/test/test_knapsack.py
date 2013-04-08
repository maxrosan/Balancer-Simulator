
import site, commands
import methods.toyodaknapsack, prediction.NoPrediction
import migration_policy.MachineUsageMigration, migration_policy.SLABreakMigration

def mac_key_sort(mac):
	return (mac.free_CPU(), mac.free_mem())

def task_key_sort(task):
	gain = (task.CPU_usage*0.4 + task.mem_usage*0.6)
	pun  = 1./(1. + abs(task.CPU_usage - task.mem_usage))
	return gain*pun

def score_task_knapsack(task, mac):
	return max(task.CPU_usage, task.mem_usage)

migration_policies = [ migration_policy.SLABreakMigration.SLABreakMigration() ]

method         = methods.toyodaknapsack.ToyodaKnapsack(prediction.NoPrediction.NoPrediction(), 
 migration_policies, 8, score_task_knapsack,
 mac_key_sort, task_key_sort)

host = commands.getoutput("hostname")

if host == "brucutu":

	dataset_path  = "/var/tmp/mr/gs_cluster/"
	mapping_log   = "/var/tmp/mr/log/mapping_toyodaknapsack_test_brucutu.log"
	balancing_log = "/var/tmp/mr/log/balancing_toyodaknapsack_test_brucutu.log"

elif host == "godzilla":

	dataset_path  = "/home/maxrosan/src/gs_cluster/"
	mapping_log   = "/home/maxrosan/simulator/Balancer-Simulator/mapping_toyodaknapsack_test_brucutu.log"
	balancing_log = "/home/maxrosan/simulator/Balancer-Simulator/balancing_toyodaknapsack_test_brucutu.log"	

else:
	dataset_path  = "/home/max/Src/simulator/gscluster/"
	mapping_log   = "/home/max/Src/simulator/logop/mapping_toyodaknapsack_test_brucutu.log"
	balancing_log = "/home/max/Src/simulator/logop/balancing_toyodaknapsack_test_brucutu.log"

total_time     = 60 * 60 * 6
