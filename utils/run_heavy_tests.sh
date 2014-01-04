#!/bin/sh -xe

python main.py config/test/test_knapsack_gen_60.py
python main.py config/test/test_ffd_gen_60.py
python main.py config/test/test_pulp_gen_60.py

python main.py config/test/test_knapsack_gen_70.py
python main.py config/test/test_ffd_gen_70.py
python main.py config/test/test_pulp_gen_70.py

python main.py config/test/test_knapsack_gen_80.py
python main.py config/test/test_ffd_gen_80.py
python main.py config/test/test_pulp_gen_80.py
