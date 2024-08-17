import math
import heapq
import numpy as np
import random
import yaml

class Tiled_image:
    def __init__(self, w, h, complexity, deadline=0):
        self.w = w
        self.h = h
        # self.hard = random.choice([0, 1])  # whether the task is hard or not
        # self.c = 112.4 * w * h / (640 * 640) * random.uniform(0.3, 3)  # complexity of the task, the unit is Gflops
        # self.c = (181.7 if self.hard else 112.4) * w * h / (640 * 640) 
        self.c = complexity
        self.deadline = deadline

    def get_size(self):
        return self.w*self.h

    def get_complexity(self):
        return self.c

    def get_deadline(self):
        return self.deadline


class Batch:
    priority = 0  # priority of the batch 由于遵循先进先出，因此不需要优先级
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
    power_headroom = 0  # power headroom of the device，定义为当前分配给设备的功率

    def __init__(self, config):
        self.memory = eval(config['memory']) - eval(config['model_memory']) # 总显存减去模型占用的显存
        self.queue = [] # queue of tasks of the device，相当于硬盘，存放待处理的tile
        self.batches = [] # batch queue of the device，要考虑 budget 限制
        self.total_complexity = 0 # total complexity of the tasks in the queue
        self.resource = 0 # resource 和 budget 这里假定为内存大小 # TODO 不过内存已经用memory限制过了，改成两次拍摄之间能够处理的任务量或许更合适一些
        self.budget = self.memory # budget 指的是内存方面
        self.temperature = config['temperature']  # temperature of the device, the unit is K。 25 degree Celsius
        self.top_temperature = config['top_temperature']  # 80 degree Celsius
        self.compute_time_s = 0.0  # compute time of the device
        self.max_power = config['max_power']  # maximum power of the device
        self.v_power_ratio = eval(config['v_power_ratio'])  # ratio of velocity and power # 速度与功率的比值，这里假定是线性关系
        self.alpha, self.beta = config['alpha'], config['beta'] # temperature control parameters

    def _calc_batch_size(self, tile_size):
        self.batchsize = math.floor(self.memory / tile_size)
        if self.batchsize < 1: # 如果batchsize小于1，就设置为1，防止 group_tiles 函数出现死循环
            self.batchsize = 1

    def get_processing_time(self): # 预计处理时间
        return self.total_complexity / self.v

    def add_tile(self, tile): # 向硬盘中添加tile
        self.queue.append(tile)
        self.total_complexity += tile.get_complexity()

    def group_tiles(self):
        if not self.queue: # 如果没有任务，直接返回
            return
        self._calc_batch_size(self.queue[0].get_size())
        while self.queue and self.resource < self.budget:
            batch = Batch()
            for _ in range(self.batchsize):
                new_tile = self.queue.pop(0) # 从队首取出一个tile
                batch.add_tile(new_tile)
                self.resource += new_tile.get_size() 
                if not self.queue:
                    break
            self.batches.append(batch)

    def get_batch_num(self):
        return len(self.batches)

    def process_image(self, total_step_in_sec): # 返回处理好的tile的个数，要传给后面的tx设备
        if not self.batches: # 首先判断有没有任务
            if not self.queue: # 连等待的任务都没有了
                return 0
            self.group_tiles() # 加入新的任务
        self.compute_time_s += total_step_in_sec
        tile_num = 0
        while self.batches and self.compute_time_s >= self.batches[0].get_complexity() / self.v:
            self.compute_time_s -= self.batches[0].get_complexity() / self.v
            self.resource -= self.batches[0].get_size()
            tile_num += self.batches[0].get_tile_num()
            self.batches.pop(0)
        return tile_num

    def set_power_headroom(self, power_headroom): # power_headroom 应该会随着设备的使用而变化
        self.power_headroom = min(power_headroom, self.max_power)
        self.v = self.v_power_ratio * self.power_headroom # 速度与功率成正比

    def power_sensitivity(self, P):
        # return np.power(P, -0.5)
        return 1

    def get_power(self):
        if not self.batches and not self.queue: # 没有任务
            return 0
        else: # 有任务，返回分配给设备的功率
            return self.power_headroom
        
    def calc_temperature(self, delta_t):
        ambient_temperature = 2.73 # 2.73K
        # print(f"power headroom: {self.power_headroom}, temperature: {self.temperature}", end=", ")
        self.temperature += self.alpha * (self.power_headroom - self.beta * (self.temperature**4 - ambient_temperature**4)) * delta_t # 拟合的时候delta_t的单位是min
        # print(f"new temperature: {self.temperature}")
        return self.temperature

    def get_temperature(self):
        return self.temperature
    
    def is_superheat(self):
        return self.temperature > self.top_temperature
    
    def in_working_temperature(self):
        return self.temperature < self.top_temperature - 9 # 相比降频温度留一点容错
    
    def downclock(self):
        if self.temperature > self.top_temperature - 10:
            self.set_power_headroom(self.beta * (self.temperature ** 4 - 2.73 ** 4))

    def get_memory(self):
        return self.memory

        
class Scheduler:
    N = 0
    
    device_list = []  # list of devices

    def __init__(self, config):
        self.N = config['N']
        self.T_wait = config['T_wait']  # maximum tolerable waiting time # TODO 参考了cote的数据，1.8s 为拍摄间隔
        self.device_list = []
        for i in range(self.N):
            with open(config['cfg_path'][0], 'r') as f:
                device_config = yaml.safe_load(f)
            self.device_list.append(Device(device_config))
            

    def _get_partition_size(self, W, H):
        # min_m = min(device.get_memory() for device in self.device_list)
        # max_v = max(device.v for device in self.device_list)
        # limit = min(min_m, max_v * self.T_wait * 640 * 640 / 112.4) # 640*640 的一张图片，计算量为 112.4Gflops
        # partition = max(math.ceil(math.sqrt(W * H / limit)), 1) # 之前是min，感觉是不小心写错了
        # w = math.ceil(W / partition)
        # h = math.ceil(H / partition)
        w, h = 400, 400 # TODO 参考了Resource-efficient In-orbit Detection of Earth Objects的数据，400*400 为一块tile
        partition = math.ceil(W / w) * math.ceil(H / h)
        return partition, w, h

    def _assign_tiles(self, tile_list): # assign tiles to devices, if the tiles cannot be assigned, return False
        device_heap = [(device.get_processing_time(), idx, device) for idx, device in enumerate(self.device_list)] # 加idx是为了防止两个device的处理时间一样
        heapq.heapify(device_heap)

        for tile in tile_list:
            _, idx, device = heapq.heappop(device_heap)
            device.add_tile(tile)
            heapq.heappush(device_heap, (device.get_processing_time(), idx, device))
        for device in self.device_list:
            # print("DEBUG: deive queue size: ", len(device.queue))
            device.group_tiles()

    def get_image(self, W, H):
        partition, w, h = self._get_partition_size(W, H)
        hard = random.choice([0, 1])
        # complexity = (181.7 if hard else 112.4) * w * h / (640 * 640)
        complexity = 3.46 * w * h / (640 * 640) # TODO 复杂度还需要修改
        tile_list = [Tiled_image(w, h, complexity, 0)] * partition
        self._assign_tiles(tile_list)

    def update_task(self, total_step_in_sec): # update the task of the devices，return the number of tiles processed
        tile_num = 0
        for device in self.device_list:
            device.downclock() # 如果温度过高，就降频
            tile_num += device.process_image(total_step_in_sec)
            device.calc_temperature(total_step_in_sec / 60) # delta_t 的单位是min
        return tile_num
    
    def get_task_num(self):
        return sum(device.get_batch_num() for device in self.device_list)

    def power_allocation(self, available_power):
        power_allocations = np.ones(self.N)
        tolerance = 1e-3
        max_iter = 100
        for _ in range(max_iter):
            sensivities = np.array([self.device_list[i].power_sensitivity(power_allocations[i]) for i in range(self.N)])
            sensitivity_ratios = sensivities / np.sum(sensivities)
            new_power_allocations = available_power * sensitivity_ratios
            if np.all(np.abs(new_power_allocations - power_allocations) < tolerance):
                break
            power_allocations = new_power_allocations
        for i in range(self.N):
            self.device_list[i].set_power_headroom(power_allocations[i])

    def get_power(self): # get the total power of the devices
        return sum(device.get_power() for device in self.device_list)
    
    def get_device_temperature(self):
        return [device.get_temperature() for device in self.device_list]
    
    def is_device_superheat(self):
        return any(device.is_superheat() for device in self.device_list)
    
    def in_working_temperature(self):
        return all(device.in_working_temperature() for device in self.device_list)
        
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
