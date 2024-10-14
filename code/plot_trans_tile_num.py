import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
file_bent_pipe = 'backup/bent_pipe3/449380000-communication.csv'
file_no_runtime = 'backup/no_runtime5/449380000-communication.csv'
file_no_scheduling = 'backup/no_scheduling4/449380000-communication.csv'
file_space_only = 'backup/space_only4/449380000-communication.csv'
file_space_exit = 'backup/space-exit10/449380000-communication.csv'
file_target_fuse = 'backup/target_fuse6/449380000-communication.csv'


def read_data(file):
    times = []
    trans_tile_nums = []
    trans_tile_proportion = []
    
    with open(file, 'r') as f:
        for line in f:
            if len(line.split(',')) == 4:
                time_str = line.split(',')[0]
                trans_tile_num_str = line.split(',')[3].split('=')[-1].strip()
                sensor_tile_num_str = line.split(',')[2].split('=')[-1].strip()
                times.append(pd.to_datetime(time_str))
                trans_tile_proportion.append(int(trans_tile_num_str) / int(sensor_tile_num_str))
                trans_tile_nums.append(int(trans_tile_num_str))
                
    return pd.DataFrame({'date_time': times, 'trans_tile_proportion' : trans_tile_proportion, 'trans_tile_nums' : trans_tile_nums})


data_bent_pipe = read_data(file_bent_pipe)
data_bent_pipe['trans_tile_nums'] = data_bent_pipe['trans_tile_nums'] * 88
data_no_runtime = read_data(file_no_runtime)
data_no_scheduling = read_data(file_no_scheduling)
data_space_only = read_data(file_space_only)
data_space_exit = read_data(file_space_exit)
data_target_fuse = read_data(file_target_fuse)

# 合并数据
data_bent_pipe['source'] = 'Bent Pipe'
data_no_runtime['source'] = 'No Runtime'
data_no_scheduling['source'] = 'No Scheduling'
data_space_only['source'] = 'Space Only'
data_space_exit['source'] = 'Space Exit'
data_target_fuse['source'] = 'Target Fuse'
combined_data = pd.concat([data_bent_pipe, data_no_runtime, data_no_scheduling, data_space_only, data_space_exit, data_target_fuse])
# combined_data = pd.concat([data_no_runtime, data_space_exit])

# 将日期时间转换为小时数
combined_data['hours'] = (combined_data['date_time'] - combined_data['date_time'].min()).dt.total_seconds() / 3600

# 绘图
plt.figure(figsize=(10, 6))
for label, group in combined_data.groupby('source'):
    plt.plot(group['hours'], group['trans_tile_nums'], label=label, marker='o')

plt.xlabel('Time')
plt.ylabel("Trans Tile Num")
plt.title("Trans Tile Num Over Time")
plt.legend()
# plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
plt.savefig("image/trans_tile_num.png")

# import pandas as pd

# time_str = '2020-10-26 23:49:55.257461724'
# datetime_obj = pd.to_datetime(time_str)

# print(datetime_obj)  # 输出：2020-10-26 23:49:55.257461724
