#!/bin/sh -xe

python main.py config/test/test_knapsack_gen_10.py
python main.py config/test/test_ffd_gen_10.py
python main.py config/test/test_pulp_gen_10.py

python main.py config/test/test_knapsack_gen_20.py
python main.py config/test/test_ffd_gen_20.py
python main.py config/test/test_pulp_gen_20.py

python main.py config/test/test_knapsack_gen_30.py
python main.py config/test/test_ffd_gen_30.py
python main.py config/test/test_pulp_gen_30.py

python main.py config/test/test_knapsack_gen_40.py
python main.py config/test/test_ffd_gen_40.py
python main.py config/test/test_pulp_gen_40.py

python main.py config/test/test_knapsack_gen_50.py
python main.py config/test/test_ffd_gen_50.py
python main.py config/test/test_pulp_gen_50.py