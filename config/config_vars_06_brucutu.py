method              = 'toyoda'
num_of_jobs         = 8
interval_toyoda     = 10
dataset_path        = "/var/tmp/mr/gs_cluster/"
mapping_log         = "/var/tmp/mr/log/mapping_toyoda_06_brucutu.log"
balancing_log       = "/var/tmp/mr/log/balancing_toyoda_06_brucutu.log"
w_cpu               = 0.6
w_mem               = 1 - w_cpu
total_time          = (60 * 60 * 24) * 1
