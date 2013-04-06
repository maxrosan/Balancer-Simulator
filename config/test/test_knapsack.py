
import site, commands
import methods.toyodaknapsack, prediction.NoPrediction, migration_policy.MachineUsageMigration

def mac_key_sort(mac):
	return (1. + mac.free_CPU())*(1. + mac.free_mem())

def task_key_sort(task):
	return max(task.CPU_usage, task.mem_usage)

def score_task_knapsack(task, mac):
	return max(task.CPU_usage, task.mem_usage)

method         = methods.toyodaknapsack.ToyodaKnapsack(prediction.NoPrediction.NoPrediction(), 
 migration_policy.MachineUsageMigration.MachineUsageMigration(), 8, score_task_knapsack,
 mac_key_sort, task_key_sort)

host = commands.getoutput("hostname")

if host == "brucutu":

	dataset_path  = "/var/tmp/mr/gs_cluster/"
	mapping_log   = "/var/tmp/mr/log/mapping_toyodaknapsack_test_brucutu.log"
	balancing_log = "/var/tmp/mr/log/balancing_toyodaknapsack_test_brucutu.log"

else:
	dataset_path  = "/home/max/Src/simulator/gscluster/"
	mapping_log   = "/home/max/Src/simulator/logop/mapping_toyodaknapsack_test_brucutu.log"
	balancing_log = "/home/max/Src/simulator/logop/balancing_toyodaknapsack_test_brucutu.log"

total_time     = (60 * 60 * 24) * 1