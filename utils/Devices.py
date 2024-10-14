from Scheduler import Scheduler
from Scheduler import Device
from Scheduler import Tiled_image
import math
import yaml

class Camera:
    image_duration_s = 0.031260
    readout_duration_s = 0.838860
    state = 'OFF' 
    prev_state = 'OFF'
    node_voltage = 0
    image_time_s = 0.0
    readout_time_s = 0.0
    image_task_count = 0
    readout_task_count = 0
    # awake voltage: 5.0v
    
    def __init__(self):
        self.state = 'OFF'
    
    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage

    def get_node_voltage(self):
        return self.node_voltage
    
    def set_image_time_s(self, image_time_s):
        self.image_time_s = image_time_s

    def get_image_time_s(self):
        return self.image_time_s
    
    def set_readout_time_s(self, readout_time_s):
        self.readout_time_s = readout_time_s

    def get_readout_time_s(self):
        return self.readout_time_s
    
    def set_image_task_count(self, image_task_count):
        self.image_task_count = image_task_count

    def get_image_task_count(self):
        return self.image_task_count
    
    def set_readout_task_count(self, readout_task_count):
        self.readout_task_count = readout_task_count

    def get_readout_task_count(self):
        return self.readout_task_count
    
    def get_power(self):
        if self.state == 'OFF':
            return 0
        elif self.state == 'IMAGING':
            return 3.5
        elif self.state == 'READOUT':
            return 2.5
            
# computer 相当于对所有计算设备的抽象
class Computer:
    task_duration_s = 0.044860
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    compute_time_s = 0.0
    compute_task_count = 0
    power_budget = 0
    prev_power_budget = 0
    # awake voltage: 6.75v
    # sleep power: 0.5w, work power: 11.3272w  from cote
    
    def __init__(self, config):
        self.state = 'OFF'
        self.scheduler = Scheduler(config) # 创建一个调度器
        self.power_budget_threshold = config['power_budget_threshold'] # power_budget 变化量超过这个值时，需要重新分配功率 # TODO 参考了mobi-com的数据
        self.image_w, self.image_h = config['image_w'], config['image_h'] # TODO 卫星拍到的一张图片的大小，参考cote的数据
    
    ####################### Device 类自身数据 #######################
    def set_state(self, state):
        self.state = state
        self.scheduler.set_device_state(state)

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage

    def get_node_voltage(self):
        return self.node_voltage

    ####################### 辅助函数，在工作流程中不起作用 #######################
    def get_partition_size(self):
        return math.ceil(self.image_w / 400) * math.ceil(self.image_h / 400) # TODO 
    
    ####################### 调用 Scheduler 的接口 #######################
    def get_compute_task_count(self): # 返回的是batch的数量
        return self.scheduler.get_task_num()

    def update_task(self, total_step_in_sec): # 返回处理好的tile的个数，要传给后面的tx设备
        if self.scheduler.is_device_superheat():
            self.set_state('OFF')
            return 0
        return self.scheduler.update_task(total_step_in_sec)

    def assign_task(self): # 这里出现了内存泄漏问题，已解决
        self.scheduler.get_image(self.image_w, self.image_h)

    def get_power(self): # 分为 OFF 和 WORK 两种状态，WORK 时的功率需要根据任务量来计算
        if self.state == 'OFF':
            return 0
        elif self.state == 'WORK':
            return self.scheduler.get_power()
        
    def set_power_budget(self, power_budget):
        self.prev_power_budget = self.power_budget
        self.power_budget = power_budget
        if abs(self.power_budget - self.prev_power_budget) > self.power_budget_threshold:
            self.scheduler.power_allocation(self.power_budget)

    def get_device_temperature(self):
        return self.scheduler.get_device_temperature()
    
    def in_working_temperature(self):
        return self.scheduler.in_working_temperature()

    def update_temperature(self, total_step_in_sec):
        self.scheduler.update_temperature(total_step_in_sec/60)

    def clear_buffer(self):
        self.scheduler.clear_buffer()

class Computer_no_scheduling:
    task_duration_s = 0.044860
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    compute_time_s = 0.0
    compute_task_count = 0
    power_budget = 0
    prev_power_budget = 0
    # awake voltage: 6.75v
    # sleep power: 0.5w, work power: 11.3272w  from cote
    
    def __init__(self, config):
        self.state = 'OFF'
        self.scheduler = Scheduler(config) # 创建一个调度器
        self.power_budget_threshold = config['power_budget_threshold'] # power_budget 变化量超过这个值时，需要重新分配功率 # TODO 参考了mobi-com的数据
        self.image_w, self.image_h = config['image_w'], config['image_h'] # TODO 卫星拍到的一张图片的大小，参考cote的数据
    
    ####################### Device 类自身数据 #######################
    def set_state(self, state):
        self.state = state
        self.scheduler.set_device_state(state)

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage

    def get_node_voltage(self):
        return self.node_voltage

    ####################### 辅助函数，在工作流程中不起作用 #######################
    def get_partition_size(self):
        return math.ceil(self.image_w / 400) * math.ceil(self.image_h / 400) # TODO 
    
    ####################### 调用 Scheduler 的接口 #######################
    def get_compute_task_count(self): # 返回的是batch的数量
        return self.scheduler.get_task_num()

    def update_task(self, total_step_in_sec): # 返回处理好的tile的个数，要传给后面的tx设备
        if self.scheduler.is_device_superheat():
            self.set_state('OFF')
            return 0
        return self.scheduler.update_task(total_step_in_sec)

    def assign_task(self):
        self.scheduler.get_image_no_scheduling(self.image_w, self.image_h)

    def get_power(self): # 分为 OFF 和 WORK 两种状态，WORK 时的功率需要根据任务量来计算
        if self.state == 'OFF':
            return 0
        elif self.state == 'WORK':
            return self.scheduler.get_power()
        
    def set_power_budget(self, power_budget):
        self.prev_power_budget = self.power_budget
        self.power_budget = power_budget
        if abs(self.power_budget - self.prev_power_budget) > self.power_budget_threshold:
            self.scheduler.power_allocation(self.power_budget)

    def get_device_temperature(self):
        return self.scheduler.get_device_temperature()
    
    def in_working_temperature(self):
        return self.scheduler.in_working_temperature()

    def update_temperature(self, total_step_in_sec):
        self.scheduler.update_temperature(total_step_in_sec/60)

    def clear_buffer(self):
        self.scheduler.clear_buffer()

class Computer_no_runtime:
    task_duration_s = 0.044860
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    compute_time_s = 0.0
    compute_task_count = 0
    power_budget = 0
    prev_power_budget = 0
    # awake voltage: 6.75v
    # sleep power: 0.5w, work power: 11.3272w  from cote
    
    def __init__(self, config):
        self.state = 'OFF'
        self.scheduler = Scheduler(config) # 创建一个调度器
        self.power_budget_threshold = config['power_budget_threshold'] # power_budget 变化量超过这个值时，需要重新分配功率 # TODO 参考了mobi-com的数据
        self.image_w, self.image_h = config['image_w'], config['image_h'] # TODO 卫星拍到的一张图片的大小，参考cote的数据
    
    ####################### Device 类自身数据 #######################
    def set_state(self, state):
        self.state = state
        self.scheduler.set_device_state(state)

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage

    def get_node_voltage(self):
        return self.node_voltage

    ####################### 辅助函数，在工作流程中不起作用 #######################
    def get_partition_size(self):
        return math.ceil(self.image_w / 400) * math.ceil(self.image_h / 400) # TODO 
    
    ####################### 调用 Scheduler 的接口 #######################
    def get_compute_task_count(self): # 返回的是batch的数量
        return self.scheduler.get_task_num()

    def update_task(self, total_step_in_sec): # 返回处理好的tile的个数，要传给后面的tx设备
        if self.scheduler.is_device_superheat():
            self.set_state('OFF')
            return 0
        return self.scheduler.update_task_no_runtime(total_step_in_sec)

    def assign_task(self):
        self.scheduler.get_image(self.image_w, self.image_h)

    def get_power(self): # 分为 OFF 和 WORK 两种状态，WORK 时的功率需要根据任务量来计算
        if self.state == 'OFF':
            return 0
        elif self.state == 'WORK':
            return self.scheduler.get_power()
        
    def set_power_budget(self, power_budget):
        self.prev_power_budget = self.power_budget
        self.power_budget = power_budget
        if abs(self.power_budget - self.prev_power_budget) > self.power_budget_threshold:
            self.scheduler.power_allocation_no_runtime(self.power_budget)

    def get_device_temperature(self):
        return self.scheduler.get_device_temperature()
    
    def in_working_temperature(self):
        return self.scheduler.in_working_temperature()

    def update_temperature(self, total_step_in_sec):
        self.scheduler.update_temperature(total_step_in_sec/60)

    def clear_buffer(self):
        self.scheduler.clear_buffer()


class Computer_targetfuse:
    task_duration_s = 0.044860
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    compute_time_s = 0.0
    compute_task_count = 0
    power_budget = 0
    prev_power_budget = 0
    # awake voltage: 6.75v
    # sleep power: 0.5w, work power: 11.3272w  from cote
    
    def __init__(self, config):
        self.state = 'OFF'
        self.scheduler = Scheduler(config) # 创建一个调度器
        self.power_budget_threshold = config['power_budget_threshold'] # power_budget 变化量超过这个值时，需要重新分配功率 # TODO 参考了mobi-com的数据
        self.image_w, self.image_h = config['image_w'], config['image_h'] # TODO 卫星拍到的一张图片的大小，参考cote的数据
    
    ####################### Device 类自身数据 #######################
    def set_state(self, state):
        self.state = state
        self.scheduler.set_device_state(state)

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage

    def get_node_voltage(self):
        return self.node_voltage

    ####################### 辅助函数，在工作流程中不起作用 #######################
    def get_partition_size(self):
        return math.ceil(self.image_w / 400) * math.ceil(self.image_h / 400) # TODO 
    
    ####################### 调用 Scheduler 的接口 #######################
    def get_compute_task_count(self): # 返回的是batch的数量
        return self.scheduler.get_task_num()

    def update_task(self, total_step_in_sec): # 返回处理好的tile的个数，要传给后面的tx设备
        if self.scheduler.is_device_superheat():
            self.set_state('OFF')
            return 0
        return self.scheduler.update_task_no_runtime(total_step_in_sec)

    def assign_task(self):
        self.scheduler.get_image_targetfuse(self.image_w, self.image_h)

    def get_power(self): # 分为 OFF 和 WORK 两种状态，WORK 时的功率需要根据任务量来计算
        if self.state == 'OFF':
            return 0
        elif self.state == 'WORK':
            return self.scheduler.get_power()
        
    def set_power_budget(self, power_budget):
        self.prev_power_budget = self.power_budget
        self.power_budget = power_budget
        if abs(self.power_budget - self.prev_power_budget) > self.power_budget_threshold:
            self.scheduler.power_allocation_no_runtime(self.power_budget)

    def get_device_temperature(self):
        return self.scheduler.get_device_temperature()
    
    def in_working_temperature(self):
        return self.scheduler.in_working_temperature()

    def update_temperature(self, total_step_in_sec):
        self.scheduler.update_temperature(total_step_in_sec/60)

    def clear_buffer(self):
        self.scheduler.clear_buffer()

class Computer_kodan:
    task_duration_s = 0.044860
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    compute_time_s = 0.0
    compute_task_count = 0
    power_budget = 0
    prev_power_budget = 0
    # awake voltage: 6.75v
    # sleep power: 0.5w, work power: 11.3272w  from cote
    
    def __init__(self, config):
        self.state = 'OFF'
        self.scheduler = Scheduler(config) # 创建一个调度器
        self.power_budget_threshold = config['power_budget_threshold'] # power_budget 变化量超过这个值时，需要重新分配功率 # TODO 参考了mobi-com的数据
        self.image_w, self.image_h = config['image_w'], config['image_h'] # TODO 卫星拍到的一张图片的大小，参考cote的数据
    
    ####################### Device 类自身数据 #######################
    def set_state(self, state):
        self.state = state
        self.scheduler.set_device_state(state)

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage

    def get_node_voltage(self):
        return self.node_voltage

    ####################### 辅助函数，在工作流程中不起作用 #######################
    def get_partition_size(self):
        return math.ceil(self.image_w / 400) * math.ceil(self.image_h / 400) # TODO 
    
    ####################### 调用 Scheduler 的接口 #######################
    def get_compute_task_count(self): # 返回的是batch的数量
        return self.scheduler.get_task_num()

    def update_task(self, total_step_in_sec): # 返回处理好的tile的个数，要传给后面的tx设备
        if self.scheduler.is_device_superheat():
            self.set_state('OFF')
            return 0
        return self.scheduler.update_task_no_runtime(total_step_in_sec)

    def assign_task(self):
        self.scheduler.get_image_kodan(self.image_w, self.image_h)

    def get_power(self): # 分为 OFF 和 WORK 两种状态，WORK 时的功率需要根据任务量来计算
        if self.state == 'OFF':
            return 0
        elif self.state == 'WORK':
            return self.scheduler.get_power()
        
    def set_power_budget(self, power_budget):
        self.prev_power_budget = self.power_budget
        self.power_budget = power_budget
        if abs(self.power_budget - self.prev_power_budget) > self.power_budget_threshold:
            self.scheduler.power_allocation_no_runtime(self.power_budget)

    def get_device_temperature(self):
        return self.scheduler.get_device_temperature()
    
    def in_working_temperature(self):
        return self.scheduler.in_working_temperature()

    def update_temperature(self, total_step_in_sec):
        self.scheduler.update_temperature(total_step_in_sec/60)

    def clear_buffer(self):
        self.scheduler.clear_buffer()

class Computer_base:
    # N = 0 # number of devices
    task_duration_s = 0.044860
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    compute_time_s = 0.0
    compute_task_count = 0
    power_budget = 0
    prev_power_budget = 0
    # awake voltage: 6.75v
    
    def __init__(self, config):
        self.state = 'OFF'
        # self.N = config['N']
        # self.device_list = []
        # for i in range(self.N):
        #     with open(config['cfg_path'][0], 'r') as f:
        #         device_config = yaml.safe_load(f)
        #     self.device_list.append(Device(device_config))
        self.scheduler = Scheduler(config) # 创建一个调度器
        self.power_budget_threshold = config['power_budget_threshold'] # power_budget 变化量超过这个值时，需要重新分配功率 # 参考了mobi-com的数据
        self.image_w, self.image_h = config['image_w'], config['image_h'] # 卫星拍到的一张图片的大小，参考cote的数据
        # self.T_wait = config['T_wait']

    # ####################### 辅助函数 #######################
    # def _get_partition_size(self, W, H):
    #     w, h = 400, 400
    #     partition = math.ceil(W / w) * math.ceil(H / h)
    #     return partition, w, h
    
    ####################### Device 类自身数据 #######################
    def set_state(self, state):
        self.state = state
        self.scheduler.set_device_state(state)

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage

    def get_node_voltage(self):
        return self.node_voltage
        
    ####################### 辅助函数，在工作流程中不起作用 #######################
    def get_partition_size(self):
        return math.ceil(self.image_w / 400) * math.ceil(self.image_h / 400) # TODO 
    
    ####################### 调用 Scheduler 的接口 #######################
    def get_compute_task_count(self): # 返回的是batch的数量
        return self.scheduler.get_task_num()
    
    def update_task(self, total_step_in_sec):
        if self.scheduler.is_device_superheat():
            self.set_state('OFF')
            return 0
        return self.scheduler.update_task_no_runtime(total_step_in_sec)
    
    def assign_task(self):
        self.scheduler.get_image_no_scheduling(self.image_w, self.image_h)

    def get_power(self): # 分为 OFF 和 WORK 两种状态，WORK 时的功率需要根据任务量来计算
        if self.state == 'OFF':
            return 0
        elif self.state == 'WORK':
            return self.scheduler.get_power()
        
    def set_power_budget(self, power_budget):
        self.prev_power_budget = self.power_budget
        self.power_budget = power_budget
        if abs(self.power_budget - self.prev_power_budget) > self.power_budget_threshold:
            self.scheduler.power_allocation_no_runtime(self.power_budget)

    def get_device_temperature(self):
        return self.scheduler.get_device_temperature()
    
    def in_working_temperature(self):
        return self.scheduler.in_working_temperature()

    def update_temperature(self, total_step_in_sec):
        self.scheduler.update_temperature(total_step_in_sec/60)

    def clear_buffer(self):
        self.scheduler.clear_buffer()
    
    # ####################### 任务处理模块 #######################
    # # 返回当前未处理任务数量
    # def get_compute_task_count(self):
    #     return sum(device.get_batch_num() for device in self.device_list)

    # # 执行任务，返回处理好的tile的个数
    # def update_task(self, total_step_in_sec): # 返回处理好的tile的个数，要传给后面的tx设备
    #     tile_num = 0
    #     for device in self.device_list:
    #         # 和有scheduler的相比没有降频操作
    #         if device.is_superheat():
    #             self.set_state('OFF')
    #             return 0
    #         tile_num += device.process_image(total_step_in_sec)
    #         device.calc_temperature(total_step_in_sec / 60) # delta_t 的单位是min
    #     return tile_num

    # # 分配任务
    # def assign_task(self):
    #     partition, w, h = self._get_partition_size(self.image_w, self.image_h)
    #     complexity = 3.46 * w * h / (640 * 640) # TODO 复杂度还需要修改
    #     tile_list = [Tiled_image(w, h, complexity, 0)] * partition
    #     tile_num, cnt = len(tile_list), 0
    #     while cnt < tile_num:
    #         for device in self.device_list:
    #             if cnt >= tile_num:
    #                 break
    #             device.add_tile(tile_list[cnt])
    #             cnt += 1
    #     for device in self.device_list:
    #         device.group_tiles()

    # ####################### 温度控制 #######################
    # def get_device_temperature(self):
    #     return [device.get_temperature() for device in self.device_list]
    
    # def in_working_temperature(self):
    #     return all(device.in_working_temperature() for device in self.device_list)
    
    # ####################### 功耗控制 #######################
    # def get_power(self): # 分为 OFF 和 WORK 两种状态，WORK 时的功率需要根据任务量来计算
    #     if self.state == 'OFF':
    #         return 0
    #     elif self.state == 'WORK':
    #         return sum(device.get_power() for device in self.device_list)
        
    # def set_power_budget(self, power_budget):
    #     self.prev_power_budget = self.power_budget
    #     self.power_budget = power_budget
    #     if abs(self.power_budget - self.prev_power_budget) > self.power_budget_threshold:
    #         device_power_headroom = power_budget / self.N
    #         for device in self.device_list:
    #             device.set_power_headroom(device_power_headroom)

    # def clear_buffer(self):
    #     for device in self.device_list:
    #         device.queue = []
    #         device.batches = []
    #         device.total_complexity = 0
    #         device.resource = 0
    #         device.compute_time_s = 0.0
        
class Rx:
    rx_duration_s = 0.044860 # TODO check this value
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    rx_time_s = 0.0
    # awake voltage: 6.75v
    
    def __init__(self):
        self.state = 'OFF'
    
    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage
    
    def get_node_voltage(self):
        return self.node_voltage
    
    def set_rx_time_s(self, rx_time_s):
        self.rx_time_s = rx_time_s

    def get_rx_time_s(self):
        return self.rx_time_s
    
    def get_power(self):
        if self.state == 'OFF':
            return 0
        elif self.state == 'RX':
            return 2.5
        
class Tx:
    tx_duration_s = 0.0032 # TODO 处理后文件大小定为40KB(DynamicDet)，传输速率为100Mbps(参考starlink数据)
    tx_image_duration_s = 3.02 # 图片大小为4096*3072，传输速率为100Mbps，假设是RGB图片(4096*3072*24/100e6 = 3.02)
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    tx_time_s = 0.0
    tx_task_count = 0
    # awake voltage: 6.75v
    
    def __init__(self):
        self.state = 'OFF'
    
    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state
    
    def set_prev_state(self, prev_state):
        self.prev_state = prev_state

    def get_prev_state(self):
        return self.prev_state
    
    def set_node_voltage(self, node_voltage):
        self.node_voltage = node_voltage

    def get_node_voltage(self):
        return self.node_voltage
    
    def set_tx_time_s(self, tx_time_s):
        self.tx_time_s = tx_time_s

    def get_tx_time_s(self):
        return self.tx_time_s
    
    def set_tx_task_count(self, tx_task_count):
        self.tx_task_count = tx_task_count

    def get_tx_task_count(self):
        return self.tx_task_count
    
    def get_power(self):
        if self.state == 'OFF':
            return 0
        elif self.state == 'TX':
            return 9.0
        