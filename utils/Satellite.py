from DateTime import DateTime
import constant as const
import utilities as util
import copy

class Satellite:
    def __init__(self, tle_file, global_time, log=None):
        self.tle_file = tle_file
        # 需要读入的数据形如：
        # year,month,day,hour,minute,second,nanosecond,id
        # 2020,10,26,22,49,36,275547261,0449380004
        # STARLINK-1082
        # 1 44938U 20001AA  20300.89853219  .00000374  00000-0  44815-4 0  9991
        # 2 44938  53.0008 124.4612 0001664  87.1986 272.9192 15.05581769 44740
        self.global_time = (global_time)
        self.local_time = copy.deepcopy(global_time)  # local time set for satellite
        self.tle_epoch = copy.deepcopy(global_time)  # validity of TLE is centered at this time
        self.log = log
        self.bstar = None
        self.inclination = None
        self.raan = None
        self.eccentricity = None
        self.arg_of_perigee = None
        self.mean_anomaly = None
        self.mean_motion = None
        self.eci_posn = None
        self.gnd_id_com = None # ground station id for communication
        # get the satellite id
        with open(self.tle_file, 'r') as tle_handle:
            for line in tle_handle:
                if line.startswith("1 "):
                    line1 = line
                elif line.startswith("2 "):
                    line2 = line
        self.id = int(line1[2:7])
        # TODO dt = get_tle_epoch(tle_file), tile_epoch = dt
        self.bstar = float(line1[53:54] + "0." + line1[54:59] + "e" + line1[59:61])
        self.inclination = float(line2[8:16])*const.STR3_RAD_PER_DEG
        self.raan = float(line2[17:25])*const.STR3_RAD_PER_DEG
        self.eccentricity = float("0." + line2[26:33])
        self.arg_of_perigee = float(line2[34:42])*const.STR3_RAD_PER_DEG
        self.mean_anomaly = float(line2[43:51])*const.STR3_RAD_PER_DEG
        self.mean_motion = float(line2[52:63])*const.STR3_RAD_PER_REV/const.STR3_MIN_PER_DAY

        tdiff_min = util.calc_tdiff_min(self.local_time.get_year(), self.local_time.get_month(), self.local_time.get_day(), self.local_time.get_hour(), self.local_time.get_minute(), self.local_time.get_second(), self.local_time.get_nanosecond(), self.tle_epoch.get_year(), self.tle_epoch.get_month(), self.tle_epoch.get_day(), self.tle_epoch.get_hour(), self.tle_epoch.get_minute(), self.tle_epoch.get_second(), self.tle_epoch.get_nanosecond())

        sgp4_posn = util.sgp4(self.bstar, self.inclination, self.raan, self.eccentricity, self.arg_of_perigee, self.mean_anomaly, self.mean_motion, tdiff_min)
        self.eci_posn = [sgp4_posn[0], sgp4_posn[1], sgp4_posn[2]]
        # print(self.eci_posn)

    def set_id(self, id):
        self.id = id
    
    def get_id(self):
        return self.id

    def set_local_time(self, local_time):
        self.local_time = local_time
        tdiff_min = util.calc_tdiff_min(self.local_time.get_year(), self.local_time.get_month(), 
                                        self.local_time.get_day(), self.local_time.get_hour(), 
                                        self.local_time.get_minute(), self.local_time.get_second(), 
                                        self.local_time.get_nanosecond(), self.tle_epoch.get_year(), 
                                        self.tle_epoch.get_month(), self.tle_epoch.get_day(), 
                                        self.tle_epoch.get_hour(), self.tle_epoch.get_minute(), 
                                        self.tle_epoch.get_second(), self.tle_epoch.get_nanosecond())
        sgp4_posn = util.sgp4(self.bstar, self.inclination, self.raan, self.eccentricity, self.arg_of_perigee, self.mean_anomaly, self.mean_motion, tdiff_min)
        self.eci_posn = [sgp4_posn[0], sgp4_posn[1], sgp4_posn[2]]
    
    def get_local_time(self):
        return self.local_time

    def get_eci_posn(self):
        return self.eci_posn
    
    def update(self, *args):
        self.local_time.update(*args)
        tdiff_min = util.calc_tdiff_min(self.local_time.get_year(), self.local_time.get_month(), 
                                        self.local_time.get_day(), self.local_time.get_hour(), 
                                        self.local_time.get_minute(), self.local_time.get_second(), 
                                        self.local_time.get_nanosecond(), self.tle_epoch.get_year(), 
                                        self.tle_epoch.get_month(), self.tle_epoch.get_day(), 
                                        self.tle_epoch.get_hour(), self.tle_epoch.get_minute(), 
                                        self.tle_epoch.get_second(), self.tle_epoch.get_nanosecond())
        sgp4_posn = util.sgp4(self.bstar, self.inclination, self.raan, self.eccentricity, self.arg_of_perigee, self.mean_anomaly, self.mean_motion, tdiff_min)
        self.eci_posn = [sgp4_posn[0], sgp4_posn[1], sgp4_posn[2]]

    def set_gnd_id_com(self, gnd_id_com):
        self.gnd_id_com = gnd_id_com

    def get_gnd_id_com(self):
        return self.gnd_id_com

if __name__ == '__main__':
    tle_file = "configuration\sat-0449380004-starlink-1082.sat"
    global_time = DateTime(2021, 1, 1, 0, 0, 0, 0)
    sat = Satellite(tle_file, global_time)
