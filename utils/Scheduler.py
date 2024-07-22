import math
import heapq
import numpy as np
import random

class Tiled_image:
    def __init__(self, w, h, complexity, deadline=0):
        self.w = w
        self.h = h
        # self.hard = random.choice([0, 1])  # whether the task is hard or not
        # self.c = 112.4 * w * h / (640 * 640) * random.uniform(0.3, 3)  # complexity of the task, the unit is Gflops
        # self.c = (181.7 if self.hard else 112.4) * w * h / (640 * 640) # TODO 这里假定计算量是根据是否是hard task来决定的
        self.c = complexity
        self.deadline = deadline

    def get_size(self):
        return self.w*self.h

    def get_complexity(self):
        return self.c

    def get_deadline(self):
        return self.deadline


class Batch:
    priority = 0  # priority of the batch
    queue = []  # queue of tasks of the batch
    batch_complexity = 0  # total complexity of the tasks in the batch

    def __init__(self): # 考虑到每个batch的大小可能不统一，因此不需要初始化batchsize
        self.queue = []
        self.batch_complexity = 0

    def add_tile(self, tile):
        self.queue.append(tile)
        self.batch_complexity += tile.get_complexity()

    def get_complexity(self):
        return self.batch_complexity
    
    def get_tile_num(self):
        return len(self.queue)
    
    def get_size(self):
        return len(self.queue) * self.queue[0].get_size()
    
    # def resize_batch(self, batchsize):
    #     self.batchsize = batchsize

class Device:
    v = 0  # velocity of the device
    batchsize = 0  # batch size of the device，限定的是最大的batch size
    # batchsize_peak = 0  # peak size of the batch 
    power_headroom = 0  # power headroom of the device，定义为当前分配给设备的功率

    def __init__(self, config):
        self.memory = eval(config['memory']) # TODO 之后还要考虑模型参数占用的显存
        self.queue = [] # queue of tasks of the device，相当于硬盘，存放待处理的tile
        self.batches = [] # batch queue of the device，要考虑 budget 限制
        self.total_complexity = 0 # total complexity of the tasks in the queue
        self.resource = 0 # resource to be used by the device。resource 和 budget 这里假定为内存大小 # TODO 不过内存已经用memory限制过了，改成两次拍摄之间能够处理的任务量或许更合适一些
        self.budget = self.memory # TODO budget 包括了内存和功率两个方面
        self.temperature = config['temperature']  # temperature of the device, the unit is K。 25 degree Celsius
        self.top_temperature = config['top_temperature']  # 80 degree Celsius
        self.compute_time_s = 0.0  # compute time of the device
        self.power_per_tile = eval(config['power_per_tile'])  # power per tile of the device # TODO 这里用的是总功率除以core数量，可能不太合适
        self.v_power_ratio = eval(config['v_power_ratio'])  # ratio of velocity and power # TODO 速度与功率的比值，这里假定是线性关系
        self.alpha, self.beta = config['alpha'], config['beta'] # TODO temperature control parameters
        # self.p_sun = config['P_sun']  # power of the sun when evaluate the temperature

    def _calc_batch_size(self, tile_size):
        self.batchsize = min(math.floor(self.memory / tile_size), math.floor(self.power_headroom / self.power_per_tile))
        if self.batchsize < 1: # 如果batchsize小于1，就设置为1，防止 group_tiles 函数出现死循环
            self.batchsize = 1

    def group_tiles(self):
        # print("tile num in devices: ", len(self.queue))
        if not self.queue: # 如果没有任务，直接返回
            return
        # print("\tgroup func start")
        self._calc_batch_size(self.queue[0].get_size())
        # print("batchsize: ", self.batchsize)
        while self.queue and self.resource < self.budget:
            batch = Batch()
            # print("create a new batch")
            for _ in range(self.batchsize):
                new_tile = self.queue.pop(0) # 从队首取出一个tile
                # print("get a tile")
                batch.add_tile(new_tile)
                # print("add a tile, tile size: ", new_tile.get_size())
                self.resource += new_tile.get_size() 
                # print("resource: ", self.resource)
                if not self.queue:
                    break
            self.batches.append(batch)
        # print("\tgroup func end")

    def set_power_headroom(self, power_headroom): # power_headroom 应该会随着设备的使用而变化
        # ambient_temperature = 2.73 # 2.73K
        # if self.temperature > self.top_temperature: # 如果温度超过了阈值，就不再分配功率
        #     self.power_headroom = self.beta * (self.temperature - ambient_temperature) # 保持温度不变
        # else:
        self.power_headroom = power_headroom
        self.v = self.v_power_ratio * self.power_headroom # 速度与功率成正比

    # def set_budget(self, budget): # 不同位置会有不同的 budget
    #     self.budget = budget

    def add_tile(self, tile): # 向硬盘中添加tile
        self.queue.append(tile)
        self.total_complexity += tile.get_complexity()

    def get_processing_time(self): # 预计处理时间
        return self.total_complexity / self.v

    def get_memory(self):
        return self.memory
    
    def _power_sensitivity(self, P):
        # return np.power(P, -0.5)
        return 1
    
    def calc_temperature(self, delta_t):
        ambient_temperature = 2.73 # 2.73K
        self.temperature += self.alpha * (self.power_headroom - self.beta * (self.temperature - ambient_temperature)) * delta_t # 拟合的时候delta_t的单位是min
        return self.temperature
    
    def process_image(self, total_step_in_sec): # 返回处理好的tile的个数，要传给后面的tx设备
        if not self.batches: # 首先判断有没有任务
            if not self.queue: # 连等待的任务都没有了
                return 0
            self.group_tiles() # 加入新的任务
        self.compute_time_s += total_step_in_sec
        while self.compute_time_s >= self.batches[0].get_complexity() / self.v:
            self.compute_time_s -= self.batches[0].get_complexity() / self.v
            self.resource -= self.batches[0].get_size()
            tile_num = self.batches[0].get_tile_num()
            self.batches.pop(0)
            return tile_num
        else:
            return 0

    def get_power(self):
        if not self.batches and not self.queue: # 没有任务
            return 0
        else: # 有任务，返回分配给设备的功率
            return self.power_headroom 

        
class Scheduler:
    N = 0
    
    device_list = []  # list of devices

    def __init__(self, config):
        self.N = config['N']
        self.device_list = [Device(config)] * self.N  
        self.T_wait = config['T_wait']  # maximum tolerable waiting time # TODO 参考了cote的数据，1.8s 为拍摄间隔

    def _get_partition_size(self, W, H):
        min_m = min(device.get_memory() for device in self.device_list)
        max_v = max(device.v for device in self.device_list)
        limit = min(min_m, max_v * self.T_wait * 640 * 640 / 112.4) # TODO 640*640 的一张图片，计算量为 112.4Gflops
        partition = max(math.ceil(math.sqrt(W * H / limit)), 1) # TODO 之前是min，感觉是不小心写错了
        w = math.ceil(W / partition)
        h = math.ceil(H / partition)
        return partition, w, h

    def _assign_tiles(self, tile_list): # assign tiles to devices, if the tiles cannot be assigned, return False
        device_heap = [(device.get_processing_time(), device) for device in self.device_list]
        heapq.heapify(device_heap)

        for tile in tile_list:
            _, device = heapq.heappop(device_heap)
            device.add_tile(tile)
            heapq.heappush(device_heap, (device.get_processing_time(), device))
        for device in self.device_list:
            device.group_tiles()

    def get_image(self, W, H):
        partition, w, h = self._get_partition_size(W, H)
        hard = random.choice([0, 1])
        complexity = (181.7 if hard else 112.4) * w * h / (640 * 640)
        tile_list = [Tiled_image(w, h, complexity, 0)] * partition * partition
        # print("tile_list size: ", len(tile_list))
        self._assign_tiles(tile_list)

    def power_allocation(self, available_power):
        power_allocations = np.ones(self.N)
        tolerance = 1e-3
        max_iter = 100
        for _ in range(max_iter):
            sensivities = np.array([self.device_list[i]._power_sensitivity(power_allocations[i]) for i in range(self.N)])
            sensitivity_ratios = sensivities / np.sum(sensivities)
            new_power_allocations = available_power * sensitivity_ratios
            if np.all(np.abs(new_power_allocations - power_allocations) < tolerance):
                break
            power_allocations = new_power_allocations
        for i in range(self.N):
            self.device_list[i].set_power_headroom(power_allocations[i])

    def get_power(self): # get the total power of the devices
        return sum(device.get_power() for device in self.device_list)
        
    def update_task(self, total_step_in_sec): # update the task of the devices，return the number of tiles processed
        tile_num = 0
        for device in self.device_list:
            tile_num += device.process_image(total_step_in_sec)
            # device.calc_temperature(total_step_in_sec / 60) # delta_t 的单位是min
        return tile_num
    
    def clear_buffer(self):
        for device in self.device_list:
            device.queue = []
            device.batches = []
            device.total_complexity = 0
            device.resource = 0
            device.compute_time_s = 0.0


if __name__ == "__main__":
    test_list = [[]] * 4
    print(test_list)
