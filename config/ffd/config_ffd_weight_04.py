
method              = 'ffd'
num_of_jobs         = 8
interval_mig        = 100
dataset_path        = "/var/tmp/mr/gs_cluster/"
mapping_log         = "/var/tmp/mr/log/mapping_ffd_04_brucutu.log"
balancing_log       = "/var/tmp/mr/log/balancing_ffd_04_brucutu.log"
w_cpu               = 0.4
w_mem               = 1 - w_cpu
total_time          = (60 * 60 * 24) * 1

mac_sorted          = False

def mac_key_sort(mac):
	return mac.free_CPU()

def task_key_sort(task):
	dcpu = w_cpu * task.CPU_usage
	dmem = w_mem * task.mem_usage
	return (dcpu + dmem)

