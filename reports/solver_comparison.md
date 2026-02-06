# Solver Comparison Report

This report summarizes solver performance based on existing logs.

## Summary Table

| Instance | Solver | Status | Max Side | Time (s) | Convergence Points | Log |
|---|---|---|---|---|---|---|
| bp20_first_15.json_highs | highs | ok | 19.299999999999997 | 0.137386 | 1 | `output_bp20_first_15.json_highs_20260205-192159-287686.log` |
| bp20_first_15.json_ortools | ortools | OPTIMAL | 19.3 | 0.012264 | 1 | `output_bp20_first_15.json_ortools_20260205-192159-287591.log` |
| bp20_first_15.json_ortools | ortools | OPTIMAL | 19.3 | 0.011013 | 1 | `output_bp20_first_15.json_ortools_20260205-201848-364815.log` |
| bp20_first_15.json_ortools | ortools | OPTIMAL | 19.3 | 0.011163 | 1 | `output_bp20_first_15.json_ortools_20260205-202200-226323.log` |
| bp20_first_15.json_pulp | pulp | Optimal | 19.3 | 0.007423 | 1 | `output_bp20_first_15.json_pulp_20260205-192159-287700.log` |
| bp20_first_15.json_pyomo | pyomo | ok | 19.299999999999997 | 0.147154 | 1 | `output_bp20_first_15.json_pyomo_20260205-192159-287751.log` |
| figure_2_1.json_highs | highs | ok | 28.59999999999995 | 0.476072 | 1 | `output_figure_2_1.json_highs_20260205-192159-287495.log` |
| figure_2_1.json_highs | highs | ok | 28.59999999999995 | 0.374233 | 1 | `output_figure_2_1.json_highs_20260205-201848-840244.log` |
| figure_2_1.json_highs | highs | ok | 28.59999999999995 | 0.346351 | 1 | `output_figure_2_1.json_highs_20260205-202200-617313.log` |
| figure_2_1.json_ortools | ortools | OPTIMAL | 28.6 | 0.012587 | 1 | `output_figure_2_1.json_ortools_20260205-192159-287310.log` |
| figure_2_1.json_ortools | ortools | OPTIMAL | 28.6 | 0.008881 | 1 | `output_figure_2_1.json_ortools_20260205-201848-364525.log` |
| figure_2_1.json_ortools | ortools | OPTIMAL | 28.6 | 0.012966 | 1 | `output_figure_2_1.json_ortools_20260205-201848-839933.log` |
| figure_2_1.json_ortools | ortools | OPTIMAL | 28.6 | 0.012125 | 1 | `output_figure_2_1.json_ortools_20260205-202200-226134.log` |
| figure_2_1.json_ortools | ortools | OPTIMAL | 28.6 | 0.011483 | 1 | `output_figure_2_1.json_ortools_20260205-202200-617038.log` |
| figure_2_1.json_pulp | pulp | Optimal | 28.6 | 0.230426 | 5 | `output_figure_2_1.json_pulp_20260205-192159-287426.log` |
| figure_2_1.json_pulp | pulp | Optimal | 28.6 | 0.257090 | 5 | `output_figure_2_1.json_pulp_20260205-201848-840182.log` |
| figure_2_1.json_pulp | pulp | Optimal | 28.6 | 0.115241 | 5 | `output_figure_2_1.json_pulp_20260205-202200-617272.log` |
| figure_2_1.json_pyomo | pyomo | ok | 28.59999999999995 | 0.346827 | 1 | `output_figure_2_1.json_pyomo_20260205-192159-287532.log` |
| figure_2_1.json_pyomo | pyomo | ok | 28.59999999999995 | 0.319481 | 1 | `output_figure_2_1.json_pyomo_20260205-201848-840352.log` |
| figure_2_1.json_pyomo | pyomo | ok | 28.59999999999995 | 0.270909 | 1 | `output_figure_2_1.json_pyomo_20260205-202200-617356.log` |
| heavy_bimodal_100.json_highs | highs | ok | 254.05 | 0.241566 | 1 | `output_heavy_bimodal_100.json_highs_20260205-192159-706243.log` |
| heavy_bimodal_100.json_ortools | ortools | OPTIMAL | 254.05 | 0.015793 | 1 | `output_heavy_bimodal_100.json_ortools_20260205-192159-621334.log` |
| heavy_bimodal_100.json_ortools | ortools | OPTIMAL | 254.05 | 0.035243 | 1 | `output_heavy_bimodal_100.json_ortools_20260205-201848-364958.log` |
| heavy_bimodal_100.json_ortools | ortools | OPTIMAL | 254.05 | 0.015797 | 1 | `output_heavy_bimodal_100.json_ortools_20260205-202200-226408.log` |
| heavy_bimodal_100.json_pulp | pulp | Optimal | 254.05 | 3600.292384 | 26049 | `output_heavy_bimodal_100.json_pulp_20260205-192159-688196.log` |
| heavy_bimodal_100.json_pyomo | pyomo | ok | 254.05 | 0.239371 | 1 | `output_heavy_bimodal_100.json_pyomo_20260205-192159-718759.log` |
| heavy_narrow_200.json_highs | highs | ok | 499.08000000000084 | 0.201890 | 1 | `output_heavy_narrow_200.json_highs_20260205-192159-771803.log` |
| heavy_narrow_200.json_ortools | ortools | OPTIMAL | 499.08 | 0.024928 | 1 | `output_heavy_narrow_200.json_ortools_20260205-192159-749302.log` |
| heavy_narrow_200.json_ortools | ortools | OPTIMAL | 499.08 | 0.031796 | 1 | `output_heavy_narrow_200.json_ortools_20260205-201848-364999.log` |
| heavy_narrow_200.json_ortools | ortools | OPTIMAL | 499.08 | 0.117226 | 1 | `output_heavy_narrow_200.json_ortools_20260205-202200-226444.log` |
| heavy_narrow_200.json_pulp | pulp | Optimal | 499.08 | 3600.160134 | 49245 | `output_heavy_narrow_200.json_pulp_20260205-192159-767906.log` |
| heavy_narrow_200.json_pyomo | pyomo | ok | 499.08000000000084 | 0.102417 | 1 | `output_heavy_narrow_200.json_pyomo_20260205-192159-821729.log` |
| heavy_uniform_50.json_highs | highs | ok | 138.59999999187528 | 43.539417 | 1 | `output_heavy_uniform_50.json_highs_20260205-192159-287941.log` |
| heavy_uniform_50.json_ortools | ortools | OPTIMAL | 138.6 | 0.013644 | 1 | `output_heavy_uniform_50.json_ortools_20260205-192159-287833.log` |
| heavy_uniform_50.json_ortools | ortools | OPTIMAL | 138.6 | 0.011466 | 1 | `output_heavy_uniform_50.json_ortools_20260205-201848-364915.log` |
| heavy_uniform_50.json_ortools | ortools | OPTIMAL | 138.6 | 0.012632 | 1 | `output_heavy_uniform_50.json_ortools_20260205-202200-226408.log` |
| heavy_uniform_50.json_pulp | pulp | Optimal | 138.6 | 3600.367226 | 3127 | `output_heavy_uniform_50.json_pulp_20260205-192159-287884.log` |
| heavy_uniform_50.json_pyomo | pyomo | ok | 138.59999999187528 | 43.078269 | 1 | `output_heavy_uniform_50.json_pyomo_20260205-192159-287974.log` |
