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
            

class Computer:
    task_duration_s = 0.044860
    state = 'OFF'
    prev_state = 'OFF'
    node_voltage = 0
    compute_time_s = 0.0
    compute_task_count = 0
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
    
    def set_compute_time_s(self, compute_time_s):
        self.compute_time_s = compute_time_s

    def get_compute_time_s(self):
        return self.compute_time_s
    
    def set_compute_task_count(self, compute_task_count):
        self.compute_task_count = compute_task_count

    def get_compute_task_count(self):
        return self.compute_task_count
    
    def get_power(self):
        if self.state == 'OFF':
            return 0
        elif self.state == 'SLEEP':
            return 0.5
        elif self.state == 'WORK':
            return 11.3272
        
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
    tx_duration_s = 0.044860 # TODO check this value
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
        