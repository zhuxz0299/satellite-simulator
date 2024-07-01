import constant as const
import utilities as util
import copy

def clip(value, min, max):
    return max if value > max else min if value < min else value

class GroundStation:
    def __init__(self, lat, lon, hae, date_time, id, log=None):
        self.hae = hae
        self.local_time = copy.deepcopy(date_time)
        self.global_time = date_time
        self.id = id
        self.log = log
        self.lat = max(-const.HALF_PI, min(lat * const.RAD_PER_DEG, const.HALF_PI))
        self.lon = max(-const.PI, min(lon * const.RAD_PER_DEG, const.PI))
        jd = util.calc_julian_day_from_ymd(self.local_time.get_year(), self.local_time.get_month(), self.local_time.get_day())
        sec = util.calc_sec_since_midnight(self.local_time.get_hour(), self.local_time.get_minute(), self.local_time.get_second())
        ns = self.local_time.get_nanosecond()
        self.eci_posn = util.dt_lla_to_eci(jd, sec, ns, self.lat, self.lon, self.hae)

    def get_hae(self): 
        return self.hae
    
    def get_lat(self):
        return self.lat
    
    def get_lon(self):
        return self.lon
    
    def get_eci_posn(self):
        return self.eci_posn
    
    def get_local_time(self):
        return self.local_time
    
    def get_global_time(self):
        return self.global_time
    
    def get_id(self):
        return self.id
    
    def get_log(self):
        return self.log
    
    def update(self, *args):
        self.local_time.update(*args)
        jd = util.calc_julian_day_from_ymd(self.local_time.get_year(), self.local_time.get_month(), self.local_time.get_day())
        sec = util.calc_sec_since_midnight(self.local_time.get_hour(), self.local_time.get_minute(), self.local_time.get_second())
        ns = self.local_time.get_nanosecond()
        self.eci_posn = util.dt_lla_to_eci(jd, sec, ns, self.lat, self.lon, self.hae)