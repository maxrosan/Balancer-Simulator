
import site
site.addsitedir("/var/tmp/mr/simulator/Balancer-Simulator/")

import methods.loadbalancingalgorithm, prediction.NoPrediction, migration_policy.MachineUsageMigration

method         = methods.loadbalancingalgorithm.LoadBalancingAlgorithm(prediction.NoPrediction.NoPrediction(), 
 migration_policy.MachineUsageMigration.MachineUsageMigration())

dataset_path   = "/home/max/Src/simulator/gscluster/"
mapping_log    = "/home/max/Src/simulator/logop/mapping_toyoda_04_brucutu.log"
balancing_log  = "/home/max/Src/simulator/logop/balancing_toyoda_04_brucutu.log"
total_time     = (60 * 60 * 24) * 1
