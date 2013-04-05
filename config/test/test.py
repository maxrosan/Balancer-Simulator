
import site

site.addsitedir("/var/tmp/mr/simulator/Balancer-Simulator/")

import methods.loadbalancingalgorithm.LoadBalancingAlgorithm
import prediction.NoPrediction.NoPrediction
import migration_policy.MachineUsageMigration.MachineUsageMigration

method              = LoadBalancingAlgorithm(NoPrediction(), MachineUsageMigration())

dataset_path        = "/var/tmp/mr/gs_cluster/"
mapping_log         = "/var/tmp/mr/log/mapping_toyoda_04_brucutu.log"
balancing_log       = "/var/tmp/mr/log/balancing_toyoda_04_brucutu.log"

total_time          = (60 * 60 * 24) * 1
