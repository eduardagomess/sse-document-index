import shutil
import os
import matplotlib.pyplot as plt
import numpy as np
from base_chart import run_experiment

results = {}

# Run each configuration 5 times
for num_diseases in [1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
    times = []
    for run in range(5):
        experiment_name = f"diseases_{num_diseases}_run{run+1}"
        *_, avg_search_time = run_experiment(
            num_documents=100,
            diseases_per_doc=num_diseases,
            prop_hepatite=0.4,
            experiment_name=experiment_name
        )
        times.append(avg_search_time)

        # Delete generated data folder
        shutil.rmtree(f"data/exp_{experiment_name}", ignore_errors=True)

    results[num_diseases] = (np.mean(times), np.std(times))

x_vals = sorted(results.keys())
y_vals = [results[x][0] for x in x_vals]  # average search times

plt.figure(figsize=(8, 5))
plt.plot(x_vals, y_vals, marker='o')
plt.title("Search Time vs Number of Keywords per Document")
plt.xlabel("Keywords per Document")
plt.ylabel("Average Search Time (s)")
plt.xticks(x_vals)  # Ensure x-axis shows integer values only
plt.grid(True)
plt.tight_layout()
plt.show()
