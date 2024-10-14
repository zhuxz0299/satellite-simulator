import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
file_bent_pipe = 'backup/bent_pipe2/449380000-energy-system.csv'
file_no_runtime = 'backup/no_runtime5/449380000-energy-system.csv'
file_no_scheduling = 'backup/no_scheduling4/449380000-energy-system.csv'
file_space_only = 'backup/space_only4/449380000-energy-system.csv'
file_space_exit = 'backup/space-exit10/449380000-energy-system.csv'
file_target_fuse = 'backup/target_fuse6/449380000-energy-system.csv'

def read_data(file):
    return pd.read_csv(file, sep=', ', engine='python')

data_bent_pipe = read_data(file_bent_pipe)
data_no_runtime = read_data(file_no_runtime)
data_no_scheduling = read_data(file_no_scheduling)
data_space_only = read_data(file_space_only)
data_space_exit = read_data(file_space_exit)
data_target_fuse = read_data(file_target_fuse)

# 将日期时间转换为datetime对象，指定格式
data_bent_pipe['date_time'] = pd.to_datetime(data_bent_pipe['date_time'])
data_no_runtime['date_time'] = pd.to_datetime(data_no_runtime['date_time'])
data_no_scheduling['date_time'] = pd.to_datetime(data_no_scheduling['date_time'])
data_space_only['date_time'] = pd.to_datetime(data_space_only['date_time'])
data_space_exit['date_time'] = pd.to_datetime(data_space_exit['date_time'])
data_target_fuse['date_time'] = pd.to_datetime(data_target_fuse['date_time'])


# 合并数据
data_bent_pipe['source'] = 'Bent Pipe'
data_no_runtime['source'] = 'No Runtime'
data_no_scheduling['source'] = 'No Scheduling'
data_space_only['source'] = 'Space Only'
data_space_exit['source'] = 'Space Exit'
data_target_fuse['source'] = 'Target Fuse'
# combined_data = pd.concat([data_bent_pipe, data_no_runtime, data_no_scheduling, data_space_only, data_space_exit, data_target_fuse])
combined_data = pd.concat([data_space_exit])

# 绘图
plt.figure(figsize=(10, 6))
for label, group in combined_data.groupby('source'):
    plt.plot(group['date_time'], group['capacitor_charge_coulomb'], label=label)

plt.xlabel('Time')
plt.ylabel('Capacitor Charge (Coulomb)')
plt.title('Capacitor Charge Over Time')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
plt.savefig("image/capacitor_charge_coulomb_space_exit.png")