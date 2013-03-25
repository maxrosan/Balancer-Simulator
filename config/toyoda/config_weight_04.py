

method              = 'toyoda'
num_of_jobs         = 8
interval_toyoda     = 100
dataset_path        = "/var/tmp/mr/gs_cluster/"
mapping_log         = "/var/tmp/mr/log/mapping_toyoda_04_brucutu.log"
balancing_log       = "/var/tmp/mr/log/balancing_toyoda_04_brucutu.log"
total_time          = (60 * 60 * 24) * 1

def mac_key_sort(mac):
	return mac.free_CPU() * mac.free_mem()

def task_key_sort(task):
	return max(task.CPU_usage, task.mem_usage)

def score_task_knapsack(task):
	#cpu = task.CPU_usage * 0.4
	#mem = task.mem_usage * 0.6

	return max(cpu, mem)
