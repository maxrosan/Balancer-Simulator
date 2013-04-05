
import site

site.addsitedir("/var/tmp/mr/simulator/Balancer-Simulator/")

from methods.loadbalancingalgorithm import LoadBalancingAlgorithm
from prediction.NoPrediction import NoPrediction
from migration_policy.MachineUsageMigration import MachineUsageMigration

method              = LoadBalancingAlgorithm(NoPrediction(), MachineUsageMigration())

dataset_path        = "/var/tmp/mr/gs_cluster/"
mapping_log         = "/var/tmp/mr/log/mapping_toyoda_04_brucutu.log"
balancing_log       = "/var/tmp/mr/log/balancing_toyoda_04_brucutu.log"

total_time          = (60 * 60 * 24) * 1
