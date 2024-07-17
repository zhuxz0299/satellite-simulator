import numpy as np
import matplotlib.pyplot as plt


# class manager:

# 假设有N个设备
N = 4

# 总的动态收集的太阳能功率
I_t = 100

# 基本功率保留给卫星总线和控制
base_power = 10
available_power = I_t - base_power

# 功率分配初始化
power_allocations = np.zeros(N)

# 设备的性能敏感度与功率的关系（假设为二次函数关系）
def sensitivity(P):
    return np.sqrt(P)

# 迭代分配功率，直到功率预算用完
remaining_power = available_power
while remaining_power > 0:
    incremental_power = remaining_power / N
    for i in range(N):
        power_allocations[i] += incremental_power
    remaining_power -= incremental_power * N

# 计算每个设备的性能
throughput = sensitivity(power_allocations)

# 绘制X-P关系曲线
fig, ax = plt.subplots()
for i in range(N):
    power_range = np.linspace(0, power_allocations[i], 100)
    performance = sensitivity(power_range)
    ax.plot(power_range, performance, label=f'Device {i+1}')

ax.set_xlabel('Power (P)')
ax.set_ylabel('Throughput (X)')
ax.legend()
ax.set_title('X-P Relationship Curves for Jetson Orin Devices')
plt.show()

# 输出分配结果
for i in range(N):
    print(f'Device {i+1}: Power Allocation = {power_allocations[i]:.2f} W, Throughput = {throughput[i]:.2f}')
