import copy

class Sensor:
    def __init__(self, eci_posn, global_time, id, log=None):
        self.prev_sense_posn = eci_posn
        self.prev_sense_date_time = copy.deepcopy(global_time)
        self.eci_posn = eci_posn # identical with 'posn' in Satellite class
        self.global_time = global_time
        self.id = id
        self.log = log

    def get_prev_sense_posn(self):
        return self.prev_sense_posn
    
    def get_prev_sense_date_time(self):
        return self.prev_sense_date_time
    
    def get_eci_posn(self):
        return self.eci_posn
    
    def get_global_time(self):
        return self.global_time
    
    def get_id(self):
        return self.id
    
    def set_eci_posn(self, eci_posn):
        self.eci_posn = eci_posn

    def update(self):
        self.prev_sense_posn = self.eci_posn
        self.prev_sense_date_time = copy.deepcopy(self.global_time)

        
        

    
    
