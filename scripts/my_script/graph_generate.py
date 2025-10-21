import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.stats import gmean


INPUT_CSV = "../../results/data/Project Analysis - gaze_ipcp_l1_analysis.csv"


df = pd.read_csv(INPUT_CSV)


prefetchers = ['ipcp_l1', 'gaze', 'gaze_ipcp_l1']


workloads = df['Workload'].unique().tolist()
n_prefetchers = len(prefetchers)


speedup_data = {pf: [] for pf in prefetchers}

def simplify_workload_name(wl):
    return wl.split('.', 1)[1] if '.' in wl else wl


for wl in workloads:
    df_wl = df[df['Workload'] == wl]
    cycles_no = df_wl[df_wl['Prefetcher'] == 'no']['Cycles'].values[0]
    for pf in prefetchers:
        if pf in df_wl['Prefetcher'].values:
            cycles_pf = df_wl[df_wl['Prefetcher'] == pf]['Cycles'].values[0]
            speedup = cycles_no / cycles_pf
            speedup_data[pf].append(speedup)
        else:
            speedup_data[pf].append(np.nan)


geo_means = {pf: gmean([v for v in speedup_data[pf] if not np.isnan(v)]) for pf in prefetchers}
for pf in prefetchers:
    speedup_data[pf].append(geo_means[pf])


workloads.append("SPEC17_Average")



n_workloads = len(workloads)
x = np.arange(n_workloads)
width = 0.25

fig, ax = plt.subplots(figsize=(12,6))

for i, pf in enumerate(prefetchers):
    ax.bar(x + i*width, speedup_data[pf], width, label=pf)


ax.set_xlabel('Workload')
ax.set_ylabel('Speedup over no prefetcher')
ax.set_title('Prefetcher Speedup Across Workloads of SPEC17')
ax.set_xticks(x + width)
ax.set_xticklabels(
    [simplify_workload_name(wl) if wl != "SPEC17_Average" else "SPEC17_Average" 
     for wl in workloads],
    rotation=45, ha='right'
)

ax.legend()


for i, wl in enumerate(workloads):
    for j, pf in enumerate(prefetchers):
        height = speedup_data[pf][i]
        if not np.isnan(height):
            ax.text(i + j*width, height + 0.02, f"{height:.3f}", ha='center', va='bottom', fontsize=8,rotation=45)

plt.tight_layout()
plt.show()
