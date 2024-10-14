import pandas as pd
import matplotlib.pyplot as plt
import ast

# 读取数据
file_no_runtime = 'backup/no_runtime3/449380000-device-temperature.csv'
# file_no_runtime = 'backup/no_runtime2/449380000-device-temperature.csv'
file_no_scheduling = 'backup/no_scheduling2/449380000-device-temperature.csv'
file_space_only = 'backup/space_only2/449380000-device-temperature.csv'
file_space_exit = 'backup/space-exit8/449380000-device-temperature.csv'
# file_space_exit = 'backup/space-exit7/449380000-device-temperature.csv'
file_target_fuse = 'backup/target_fuse4/449380000-device-temperature.csv'

def read_data(file):
    # 读取整个文件
    with open(file, 'r') as f:
        lines = f.readlines()
    
    # 处理数据，提取时间和温度
    data = []
    for line in lines[1:]:  # 跳过标题行
        date_time, temperature = line.strip().split(', ', 1)
        temperature = ast.literal_eval(temperature)  # 将字符串转换为列表
        data.append([date_time, temperature[0], temperature[1]])
    
    # 创建DataFrame
    df = pd.DataFrame(data, columns=['date_time', 'device1_temp', 'device2_temp'])
    df['date_time'] = pd.to_datetime(df['date_time'])
    return df

data_no_runtime = read_data(file_no_runtime)
data_no_scheduling = read_data(file_no_scheduling)
data_space_only = read_data(file_space_only)
data_space_exit = read_data(file_space_exit)
data_target_fuse = read_data(file_target_fuse)

# 合并数据
data_no_runtime['source'] = 'No Runtime'
data_no_scheduling['source'] = 'No Scheduling'
data_space_only['source'] = 'Space Only'
data_space_exit['source'] = 'Space Exit'
data_target_fuse['source'] = 'Target Fuse'
# combined_data = pd.concat([data_no_runtime, data_no_scheduling, data_space_only, data_space_exit, data_target_fuse])
combined_data = pd.concat([data_space_exit, data_no_runtime])

# 将日期时间转换为小时数
combined_data['hours'] = (combined_data['date_time'] - combined_data['date_time'].min()).dt.total_seconds() / 3600

# 绘图
plt.figure(figsize=(10, 6))
for label, group in combined_data.groupby('source'):
    # plt.plot(group['date_time'], group['device1_temp'], label=f'{label} Device 1')
    plt.plot(group['hours'], group['device2_temp'], label=f'{label}')

plt.xlabel('Time')
plt.ylabel('Computer Temperature (K)')
plt.title('Computer Temperature Over Time')
plt.legend()
# plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
plt.savefig("image/computer_temperature_debug.png")