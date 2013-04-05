
import site
site.addsitedir("/var/tmp/mr/simulator/Balancer-Simulator/")

import methods.loadbalancingalgorithm, prediction.NoPrediction, migration_policy

method         = methods.loadbalancingalgorithm.LoadBalancingAlgorithm(prediction.NoPredictionNo.Prediction(), 
 migration_policy.MachineUsageMigration.MachineUsageMigration())

dataset_path   = "/var/tmp/mr/gs_cluster/"
mapping_log    = "/var/tmp/mr/log/mapping_toyoda_04_brucutu.log"
balancing_log  = "/var/tmp/mr/log/balancing_toyoda_04_brucutu.log"
total_time     = (60 * 60 * 24) * 1
