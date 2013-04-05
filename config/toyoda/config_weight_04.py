

method              = 'toyoda'
num_of_jobs         = 8
interval_toyoda     = 100
dataset_path        = "/var/tmp/mr/gs_cluster/"
mapping_log         = "/var/tmp/mr/log/mapping_toyoda_04_brucutu.log"
balancing_log       = "/var/tmp/mr/log/balancing_toyoda_04_brucutu.log"
total_time          = (60 * 60 * 24) * 1
method_sel_macs     = 'priority_queue'
#method_sel_macs     = 'nothing'

def mac_key_sort(mac):
	return (mac.free_CPU() * mac.free_mem())

def mac_key_pq(mac):
	return (mac.free_CPU() * mac.free_mem())

def task_key_sort(task):
	return max(task.CPU_usage, task.mem_usage)

def score_task_knapsack(task, mac):
	return max(task.CPU_usage, task.mem_usage)

def must_migrate(old_task, new_task, machine):
	#use = (machine.CPU_usage * machine.mem_usage)/(machine.capacity_CPU * machine.capacity_memory)
	#return  (use < 0.5) # and ((1. + old_task.CPU_usage)*(1. + old_task.mem_usage) < (1. + new_task.CPU_usage)*(1. + new_task.mem_usage))
	return False
		
