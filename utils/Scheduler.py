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
        self.idle_power = config['idle_power']  # idle power of the device
        self.v_power_ratio = eval(config['v_power_ratio'])  # ratio of velocity and power # 速度与功率的比值，这里假定是线性关系
        self.alpha, self.beta = config['alpha'], config['beta'] # temperature control parameters
        self.is_cooling = "False"
        self.state = "OFF" # 为了方便计算温度而设定的

    def _calc_batch_size(self, tile_size):
        self.batchsize = math.floor(self.memory / tile_size)
        if self.batchsize < 1: # 如果batchsize小于1，就设置为1，防止 group_tiles 函数出现死循环
            self.batchsize = 1

    def set_state(self, state):
        self.state = state

    def get_processing_time(self): # 预计处理时间
        if self.v == 0:
            return 1e9
        return self.total_complexity / self.v

    def get_complexity(self):
        return self.total_complexity

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
        if self.v == 0: # 如果设备没有速度，说明设备过热，没有工作
            return 0
        if not self.batches: # 首先判断有没有任务
            if not self.queue: # 连等待的任务都没有了
                self.power_headroom = self.idle_power
                return 0
            self.group_tiles() # 加入新的任务
        self.compute_time_s += total_step_in_sec
        tile_num = 0
        while self.batches and self.compute_time_s >= self.batches[0].get_complexity() / self.v:
            self.compute_time_s -= self.batches[0].get_complexity() / self.v
            self.total_complexity -= self.batches[0].get_complexity()
            self.resource -= self.batches[0].get_size()
            tile_num += self.batches[0].get_tile_num()
            self.batches.pop(0)
        return tile_num

    def set_power_headroom(self, power_headroom): # power_headroom 应该会随着设备的使用而变化
        self.power_headroom = min(power_headroom, self.max_power)
        if self.power_headroom <= self.idle_power:
            self.state = "OFF"
            self.power_headroom = 0
            self.v = 0
        else:
            self.v = self.v_power_ratio * (self.power_headroom - self.idle_power) # 速度与功率成正比

    def power_sensitivity(self, P):
        # return np.power(P, -0.5)
        return self.v_power_ratio

    def get_power(self):
        if self.power_headroom == 0:
            return 0
        if not self.batches and not self.queue: # 没有任务
            return self.idle_power
        else: # 有任务，返回分配给设备的功率
            return self.power_headroom

    def calc_temperature(self, delta_t):
        ambient_temperature = 2.73 # 2.73K
        if self.state == "OFF":
            self.temperature += self.alpha * (self.idle_power - self.beta * (self.temperature**4 - ambient_temperature**4)) * delta_t
        else:
            self.temperature += self.alpha * (self.power_headroom - self.beta * (self.temperature**4 - ambient_temperature**4)) * delta_t # 拟合的时候delta_t的单位是min
        return self.temperature

    def get_temperature(self):
        return self.temperature
    
    def is_superheat(self):
        return self.temperature > self.top_temperature
    
    def in_working_temperature(self):
        return self.temperature < self.top_temperature - 9 # 相比降频温度留一点容错
    
    def get_cooling(self):
        return self.is_cooling
    
    def set_cooling(self, cooling):
        self.is_cooling = cooling
    
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
            with open(config['cfg_path'][i], 'r') as f:
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

    def _assign_tiles_no_scheduling(self, tile_list):
        tile_num, cnt = len(tile_list), 0
        while cnt < tile_num:
            for device in self.device_list:
                if cnt >= tile_num:
                    break
                device.add_tile(tile_list[cnt])
                cnt += 1
        for device in self.device_list:
            device.group_tiles()

    def set_device_state(self, state):
        for device in self.device_list:
            device.set_state(state)

    def get_image(self, W, H):
        partition, w, h = self._get_partition_size(W, H)
        hard = random.choice([0, 1])
        complexity = (3.5 if hard else 2.0) * random.uniform(0.9, 1.1) * w * h / (640 * 640)
        # complexity = 3.46 * w * h / (640 * 640) # TODO 复杂度还需要修改
        tile_list = [Tiled_image(w, h, complexity, 0)] * partition
        self._assign_tiles(tile_list)

    def get_image_no_scheduling(self, W, H):
        partition, w, h = self._get_partition_size(W, H)
        hard = random.choice([0, 1])
        complexity = (3.5 if hard else 2.0) * random.uniform(0.9, 1.1) * w * h / (640 * 640)
        # complexity = 3.46 * w * h / (640 * 640)
        tile_list = [Tiled_image(w, h, complexity, 0)] * partition
        self._assign_tiles_no_scheduling(tile_list)

    def get_image_targetfuse(self, W, H):
        partition, w, h = self._get_partition_size(W, H)
        hard = random.choice([0, 1])
        # complexity = (181.7 if hard else 112.4) * w * h / (640 * 640)
        complexity = 3.4 * random.uniform(0.9, 1.1) * w * h / (640 * 640)
        tile_list = [Tiled_image(w, h, complexity, 0)] * partition
        self._assign_tiles(tile_list)

    def get_image_kodan(self, W, H):
        partition, w, h = self._get_partition_size(W, H)
        hard = random.choice([0, 1])
        # complexity = (181.7 if hard else 112.4) * w * h / (640 * 640)
        complexity = 3.4 * random.uniform(0.9, 1.1) * w * h / (640 * 640)
        tile_list = [Tiled_image(w, h, complexity, 0)] * partition
        self._assign_tiles(tile_list)

    def update_task(self, total_step_in_sec): # update the task of the devices，return the number of tiles processed
        tile_num = 0
        for device in self.device_list:
            device.downclock() # 如果温度过高，就降频
            if device.is_superheat():
                device.set_power_headroom(0)
                device.set_cooling("True")
            tile_num += device.process_image(total_step_in_sec)
        return tile_num
    
    def update_task_no_runtime(self, total_step_in_sec):
        tile_num = 0
        for device in self.device_list:
            if device.is_superheat():
                device.set_power_headroom(0)
                device.set_cooling("True")
            tile_num += device.process_image(total_step_in_sec)
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
            if self.device_list[i].get_cooling() == "True":
                if self.device_list[i].in_working_temperature():
                    self.device_list[i].set_cooling("False")
                    self.device_list[i].set_power_headroom(power_allocations[i])
                else:
                    self.device_list[i].set_power_headroom(0)
            else:
                self.device_list[i].set_power_headroom(power_allocations[i])

    def power_allocation_no_runtime(self, available_power):
        for device in self.device_list:
            if device.get_cooling() == "True":
                if device.in_working_temperature():
                    device.set_cooling("False")
                    device.set_power_headroom(available_power/self.N)
                else:
                    device.set_power_headroom(0)
            else:
                device.set_power_headroom(available_power/self.N)

    def get_power(self): # get the total power of the devices
        return sum(device.get_power() for device in self.device_list)
    
    def get_device_temperature(self):
        return [device.get_temperature() for device in self.device_list]
    
    # 这两处改动是为了防止一个设备过热，但是另一个设备还能继续工作的情况
    # 只有当两个设备同时过热，才会让整个计算系统停止工作
    def is_device_superheat(self):
        return all(device.is_superheat() for device in self.device_list)
    
    def in_working_temperature(self):
        return any(device.in_working_temperature() for device in self.device_list)
    
    def update_temperature(self, delta_t):
        return [device.calc_temperature(delta_t) for device in self.device_list]
        
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
