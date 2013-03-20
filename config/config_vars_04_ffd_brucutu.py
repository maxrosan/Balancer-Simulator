
method              = "ffd"
num_of_jobs         = 8
dataset_path        = "/var/tmp/mr/gs_cluster/"
mapping_log         = "/var/tmp/mr/log/mapping_ffd_04_brucutu.log"
balancing_log       = "/var/tmp/mr/log/balancing_ffd_04_brucutu.log"
total_time          = (60 * 60 * 24) * 1

w_cpu               = 0.4
w_mem               = 1 - w_cpu
interval_mig        = 80
mac_sorted          = True
