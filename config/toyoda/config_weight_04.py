

method              = 'toyoda'
num_of_jobs         = 8
interval_toyoda     = 100
dataset_path        = "/var/tmp/mr/gs_cluster/"
mapping_log         = "/var/tmp/mr/log/mapping_toyoda_04_brucutu.log"
balancing_log       = "/var/tmp/mr/log/balancing_toyoda_04_brucutu.log"
total_time          = (60 * 60 * 24) * 1
method_sel_macs     = 'list'

def mac_key_sort(mac):
	return mac.capacity_CPU * mac.capacity_memory

def mac_key_pq(mac):
	return mac.free_CPU() * mac.free_mem()

def task_key_sort(task):
	return max(task.CPU_usage, task.mem_usage)

def score_task_knapsack(task, mac):
	return (task.CPU_usage * mac.free_CPU() + task.mem_usage * mac.free_mem())
