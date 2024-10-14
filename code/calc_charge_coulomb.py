import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
file_bent_pipe = 'backup/bent_pipe3/449380000-energy-system.csv'
file_no_runtime = 'backup/no_runtime5/449380000-energy-system.csv'
file_no_scheduling = 'backup/no_scheduling4/449380000-energy-system.csv'
file_space_only = 'backup/space_only4/449380000-energy-system.csv'
file_space_exit = 'backup/space-exit10/449380000-energy-system.csv'
file_target_fuse = 'backup/target_fuse6/449380000-energy-system.csv'

def read_data(file):
    return pd.read_csv(file, sep=', ', engine='python')

def calc_charge(data):
    solar_array_ampere = data['solar_array_ampere']
    total_charge = 0
    for ampere in solar_array_ampere:
        total_charge += ampere
    return total_charge
    # capaciptor_charge_coulomb = data['capacitor_charge_coulomb']
    # total_charge = 0
    # pre_charge = None
    # for charge in capaciptor_charge_coulomb:
    #     if pre_charge is not None and charge > pre_charge:
    #         total_charge += (charge - pre_charge)
    #     pre_charge = charge
    # return total_charge

data_bent_pipe = read_data(file_bent_pipe)
data_no_runtime = read_data(file_no_runtime)
data_no_scheduling = read_data(file_no_scheduling)
data_space_only = read_data(file_space_only)
data_space_exit = read_data(file_space_exit)
data_target_fuse = read_data(file_target_fuse)

total_charge_bent_pipe = calc_charge(data_bent_pipe)
total_charge_no_runtime = calc_charge(data_no_runtime)
total_charge_no_scheduling = calc_charge(data_no_scheduling)
total_charge_space_only = calc_charge(data_space_only)
total_charge_space_exit = calc_charge(data_space_exit)
total_charge_target_fuse = calc_charge(data_target_fuse)

print(f"Total charge for Bent Pipe: {total_charge_bent_pipe}, No Runtime: {total_charge_no_runtime}, No Scheduling: {total_charge_no_scheduling}, Space Only: {total_charge_space_only}, Space Exit: {total_charge_space_exit}, Target Fuse: {total_charge_target_fuse}")

# 画一个柱状图
# sources = ['Bent Pipe', 'No Runtime', 'No Scheduling', 'Space Only', 'Space Exit', 'Target Fuse']
sources = ['Bent Pipe', 'Space Only', 'Space Exit', 'Target Fuse']
# charges = [total_charge_bent_pipe, total_charge_no_runtime, total_charge_no_scheduling, total_charge_space_only, total_charge_space_exit, total_charge_target_fuse]
charges = [total_charge_bent_pipe, total_charge_space_only, total_charge_space_exit, total_charge_target_fuse]

plt.bar(sources, charges)
plt.xlabel('Source')
plt.ylabel('Total Charge')
plt.title('Total Charge by Source')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
plt.savefig("image/total_charge_by_source.png")