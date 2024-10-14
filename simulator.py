import sys
import os
import yaml
current_dir = os.path.dirname(os.path.realpath(__file__))
utils_dir = os.path.join(current_dir, "utils")
sys.path.append(utils_dir)

from utils import constant as const
from utils import utilities
from utils.Devices import *
from utils.Capacitor import Capacitor
from utils.SolarArray import SolarArray
from utils.DateTime import DateTime
from utils.Satellite import Satellite
from utils.Sensor import Sensor
from utils.GroundStation import GroundStation


# --------------------------------- global variables ---------------------------------#
# file path
date_time_file = None
time_step_file = None
num_step_file = None
satellite_file_list = []
solar_array_file_list = []
capacitor_file_list = []
sensor_sat_file_list = []
ground_station_file_list = []

# config data
num_step = None
hour_step = None
minute_step = None
second_step = None
nanosecond_step = None
total_step_in_sec = None
date_time = None
satellite_list = []
satid_to_sat = dict()
satid_to_occlusion_factor = dict()
satid_to_solar_array = dict()
satid_to_capacitor = dict()
satid_to_camera = dict()
satid_to_computer = dict()
satid_to_rx = dict()
satid_to_tx = dict()
satid_to_node_voltage = dict()
satid_to_sensor = dict()
satid_to_thresh_coeff = dict()
satid_to_threshold_km = dict()
ground_station_list = []
gndid_to_gnd = dict()
computer_config = dict()


def get_conf_files(config_path):
    global date_time_file, time_step_file, num_step_file, satellite_file_list, solar_array_file_list, capacitor_file_list, sensor_sat_file_list, ground_station_file_list
    # check if the configuration file exists
    if not os.path.exists(config_path):
        print("Configuration file does not exist")
        return

    for root, dirs, files in os.walk(config_path):  # 该函数会递归的输出所有文件夹信息
        for file in files:
            file_path = os.path.join(root, file)
            if file == "date-time.dat":
                date_time_file = file_path
            elif file == "time-step.dat":
                time_step_file = file_path
            elif file == "num-steps.dat":
                num_step_file = file_path
            elif file.endswith(".sat"):
                satellite_file_list.append(file_path)
            elif file.startswith("solar-array-sat-"):
                solar_array_file_list.append(file_path)
            elif file.startswith("capacitor-sat-"):
                capacitor_file_list.append(file_path)
            elif file.startswith("sensor-sat-"):
                sensor_sat_file_list.append(file_path)
            elif file.endswith(".gnd"):
                ground_station_file_list.append(file_path)


def read_data_from_config(sim_type = "space_exit"):
    global num_step, hour_step, minute_step, second_step, nanosecond_step, total_step_in_sec, date_time, satellite_list, satid_to_sat, satid_to_occlusion_factor, satid_to_solar_array, satid_to_capacitor, satid_to_node_voltage, satid_to_camera, satid_to_computer, satid_to_rx, satid_to_tx, satid_to_sensor, satid_to_thresh_coeff, satid_to_threshold_km, ground_station_list, gndid_to_gnd, computer_config
    # DONE read num-step.dat, to get the number of steps
    with open(num_step_file, 'r') as num_step_handle:
        next(num_step_handle)
        num_step = int(num_step_handle.readline())

    # DONE read date-time.dat, to get the initial date-time
    with open(date_time_file, 'r') as date_time_handle:
        next(date_time_handle)
        time_list = date_time_handle.readline().split(',')
        year = int(time_list[0])
        month = int(time_list[1])
        day = int(time_list[2])
        hour = int(time_list[3])
        minute = int(time_list[4])
        second = int(time_list[5])
        nanosecond = int(time_list[6])
        date_time = DateTime(year, month, day, hour, minute, second, nanosecond)

    # DONE read time-step.dat, to get the time step
    with open(time_step_file, 'r') as time_step_handle:
        next(time_step_handle)
        line = time_step_handle.readline()
        line = line.split(",")
        hour_step = int(line[0])
        minute_step = int(line[1])
        second_step = int(line[2])
        nanosecond_step = int(line[3])
        total_step_in_sec = hour_step * const.SECOND_PER_HOUR + minute_step * const.SECOND_PER_MINUTE + second_step + nanosecond_step / const.NANOSECOND_PER_SECOND

    # DONE read satellite files, to get the satellite information
    for satellite_file in satellite_file_list:
        with open(satellite_file, 'r') as sat_handle:
            next(sat_handle)
            line = sat_handle.readline()
            line = line.split(",")
            sat_year, sat_month, sat_day, sat_hour, sat_minute, sat_second, sat_nanosecond, id = \
                int(line[0]), int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7])
            sat_time = DateTime(sat_year, sat_month, sat_day, sat_hour, sat_minute, sat_second, sat_nanosecond)
            satellite_list.append(Satellite(satellite_file, date_time))
            satellite_list[-1].set_id(id)
            satellite_list[-1].set_local_time(sat_time)
            satid_to_sat[id] = satellite_list[-1]

    def sort_rule(s): return s.get_id()
    satellite_list = sorted(satellite_list, key=sort_rule)

    # DONE read solar array files, to get the solar array information
    for solar_array_file in solar_array_file_list:
        with open(solar_array_file, 'r') as solar_array_handle:
            next(solar_array_handle)
            line = solar_array_handle.readline()
            line = line.split(",")
            open_circuit_voltage = float(line[0])
            surface_area_m2 = float(line[1])
            efficiency = float(line[2])
            id = int(line[3])
            satid_to_solar_array[id] = SolarArray(open_circuit_voltage, surface_area_m2, efficiency, id)
        jd = utilities.calc_julian_day_from_ymd(date_time.get_year(), date_time.get_month(), date_time.get_day())
        sec = utilities.calc_sec_since_midnight(date_time.get_hour(), date_time.get_minute(), date_time.get_second())
        ns = date_time.get_nanosecond()
        sun_eci_posn_km = utilities.calc_sun_eci_posn_km(jd, sec, ns)
        sat_eci_posn_km = satid_to_sat[id].get_eci_posn()
        sun_occlusion_factor = utilities.calc_sun_occlusion_factor(sat_eci_posn_km, sun_eci_posn_km)
        satid_to_occlusion_factor[id] = sun_occlusion_factor
        irradiance_wpm2 = -1352.44 * sun_occlusion_factor + const.SOLAR_CONSTANT
        satid_to_solar_array[id].set_irradiance_wpm2(irradiance_wpm2)

    # DONE read capacitor files, to get the capacitor information
    for capacitor_file in capacitor_file_list:
        with open(capacitor_file, 'r') as capacitor_handle:
            next(capacitor_handle)
            line = capacitor_handle.readline()
            line = line.split(",")
            line = [float(x) for x in line]
            capacitance_farad = line[0]
            esr_ohm = line[1]
            charge_coulomb = line[2]
            id = int(line[3])
        satid_to_capacitor[id] = Capacitor(capacitance_farad, esr_ohm, id)
        satid_to_capacitor[id].set_charge_coulomb(charge_coulomb)

    # DONE set the parameters of camera, computer, etc.
    with open("computer_cfg/computer.yaml", 'r') as computer_handle:
        computer_config = yaml.safe_load(computer_handle)
    for satellite in satellite_list:
        sat_id = satellite.get_id()
        satid_to_camera[sat_id] = Camera()
        if sim_type == "space_exit":
            satid_to_computer[sat_id] = Computer(computer_config)
        elif sim_type == "base":
            satid_to_computer[sat_id] = Computer_base(computer_config)
        elif sim_type == "no_runtime":
            satid_to_computer[sat_id] = Computer_no_runtime(computer_config)
        elif sim_type == "no_scheduling":
            satid_to_computer[sat_id] = Computer_no_scheduling(computer_config)
        elif sim_type == "target_fuse":
            satid_to_computer[sat_id] = Computer_targetfuse(computer_config)
        elif sim_type == "kodan":
            satid_to_computer[sat_id] = Computer_kodan(computer_config)
        else:
            raise ValueError("Invalid simulation type")
        satid_to_rx[sat_id] = Rx()
        satid_to_tx[sat_id] = Tx()

    # DONE set the devices to the initial state, and get the initial node voltage
    for satellite in satellite_list:
        sat_id = satellite.get_id()

        # 这里是为了得到computer模块最多能够消耗的功率，作为一个上限
        power_w = utilities.calc_max_power_w(
            satid_to_capacitor[sat_id].get_charge_coulomb(),
            satid_to_capacitor[sat_id].get_capacitance_farad(),
            satid_to_solar_array[sat_id].get_current_ampere(),
            satid_to_capacitor[sat_id].get_esr_ohm(),
        )

        if (power_w < satid_to_camera[sat_id].get_power() + satid_to_rx[sat_id].get_power() + satid_to_tx[sat_id].get_power()):
            satid_to_camera[sat_id].set_state('OFF')
            satid_to_computer[sat_id].set_state('OFF')
            satid_to_rx[sat_id].set_state('OFF')
            satid_to_tx[sat_id].set_state('OFF')
            
        satid_to_computer[sat_id].set_power_budget(power_w - satid_to_camera[sat_id].get_power() - satid_to_rx[sat_id].get_power() - satid_to_tx[sat_id].get_power())

        # power_w = satid_to_camera[sat_id].get_power() + satid_to_computer[sat_id].get_power() + satid_to_rx[sat_id].get_power() + satid_to_tx[sat_id].get_power()
        node_voltage_discriminant = utilities.calc_node_voltage_discriminant(
            satid_to_capacitor[sat_id].get_charge_coulomb(),
            satid_to_capacitor[sat_id].get_capacitance_farad(),
            satid_to_solar_array[sat_id].get_current_ampere(),
            satid_to_capacitor[sat_id].get_esr_ohm(),
            power_w
        )

        # if (node_voltage_discriminant < 0):
        #     satid_to_camera[sat_id].set_state('OFF')
        #     satid_to_computer[sat_id].set_state('OFF')
        #     satid_to_rx[sat_id].set_state('OFF')
        #     satid_to_tx[sat_id].set_state('OFF')
        #     power_w = satid_to_camera[sat_id].get_power() + satid_to_computer[sat_id].get_power() + satid_to_rx[sat_id].get_power() + satid_to_tx[sat_id].get_power()
        #     node_voltage_discriminant = utilities.calc_node_voltage_discriminant(
        #         satid_to_capacitor[sat_id].get_charge_coulomb(),
        #         satid_to_capacitor[sat_id].get_capacitance_farad(),
        #         satid_to_solar_array[sat_id].get_current_ampere(),
        #         satid_to_capacitor[sat_id].get_esr_ohm(),
        #         power_w
        #     )
        node_voltage = utilities.calc_node_voltage(
            node_voltage_discriminant,
            satid_to_capacitor[sat_id].get_charge_coulomb(),
            satid_to_capacitor[sat_id].get_capacitance_farad(),
            satid_to_solar_array[sat_id].get_current_ampere(),
            satid_to_capacitor[sat_id].get_esr_ohm()
        )
        satid_to_camera[sat_id].set_node_voltage(node_voltage)
        satid_to_computer[sat_id].set_node_voltage(node_voltage)
        satid_to_rx[sat_id].set_node_voltage(node_voltage)
        satid_to_tx[sat_id].set_node_voltage(node_voltage)
        satid_to_node_voltage[sat_id] = node_voltage

    # DONE define sensors
    for sensor_sat_file in sensor_sat_file_list:
        with open(sensor_sat_file, 'r') as sensor_sat_handle:
            next(sensor_sat_handle)
            line = sensor_sat_handle.readline()
            line = line.split(",")
            line = [float(x) for x in line]
            bits_per_sense = int(line[0])
            pixel_count_w = int(line[1])
            pixel_size_m = float(line[2])
            focal_length_m = float(line[3])
            pixel_count_h = int(line[4])
            id = int(line[5])
            posn = satid_to_sat[id].get_eci_posn()
            satid_to_thresh_coeff[id] = max(pixel_count_h, pixel_count_w) * pixel_size_m / focal_length_m
        satid_to_sensor[id] = Sensor(posn, date_time, id)

    # ground station
    for ground_station_file in ground_station_file_list:
        with open(ground_station_file, 'r') as ground_station_handle:
            next(ground_station_handle)
            line = ground_station_handle.readline()
            line = line.split(",")
            line = [float(x) for x in line]
            id, lat, lon, hae = int(line[0]), line[1], line[2], line[3]
            ground_station_list.append(GroundStation(lat, lon, hae, date_time, id))
            gndid_to_gnd[id] = ground_station_list[-1]
    ground_station_list = sorted(ground_station_list, key=lambda x: x.get_id())

    # DONE other simulation data
    for satellite in satellite_list:
        sat_id = satellite.get_id()
        satid_to_threshold_km[sat_id] = satid_to_thresh_coeff[sat_id] * utilities.calc_altitude_km(satellite.get_eci_posn())

def log_file_init(log_path):
    for satellite in satellite_list:
        sat_id = satellite.get_id()
        sensor_trigger_file = os.path.join(log_path, f"{sat_id}-sensor-trigger.csv")
        with open(sensor_trigger_file, 'w') as sensor_trigger_handle:
            sensor_trigger_handle.write("date_time, altidute_km, x_km, y_km, z_km\n")
        device_state_file = os.path.join(log_path, f"{sat_id}-device-state.csv")
        with open(device_state_file, 'w') as device_state_handle:
            device_state_handle.write("date_time, camera_state, computer_state, rx_state, tx_state\n")
        communication_file = os.path.join(log_path, f"{sat_id}-communication.csv")
        with open(communication_file, 'w') as communication_handle:
            communication_handle.write("date_time, gnd_id\n")
        energy_system_file = os.path.join(log_path, f"{sat_id}-energy-system.csv")
        with open(energy_system_file, 'w') as energy_system_handle:
            energy_system_handle.write("date_time, node_voltage, computer_power, total_load_current_ampere, solar_array_ampere, capacitor_charge_coulomb\n")
        device_temperature_file = os.path.join(log_path, f"{sat_id}-device-temperature.csv")
        with open(device_temperature_file, 'w') as device_temperature_handle:
            device_temperature_handle.write("date_time, computer_temperature\n")
    

def main():
    COULOMB_COMPUTER, COULOMB_TX, COULOMB_CAMERA = 50, 45, 40
    # check command line arguments
    if len(sys.argv) != 4:
        print("Usage: python {} {} {}".format(sys.argv[0], "path to configuration", "path to log", "sim type"))
        print("sim type: space_exit, base, no_runtime, no_scheduling, target_fuse, kodan")
        print("Example: python {} {} {}".format(sys.argv[0], "config", "log", "space_exit"))
        return

    # configuration file and log file
    config_path = sys.argv[1]
    log_path = sys.argv[2]
    sim_type = sys.argv[3]

    get_conf_files(config_path)
    read_data_from_config(sim_type)
    global satellite_list
    first_sat = satellite_list[0] # TODO 测试仅有一个卫星的情况
    satellite_list = [first_sat]
    log_file_init(log_path)

    step_count = 0
    sensor_image_num, trans_tile_num = 0, 0 # 记录sensor触发的次数和transmit的tile数
    partition_size = satid_to_computer[first_sat.get_id()].get_partition_size()
    while step_count < num_step: 
        # --------------------- simulation loop --------------------- #
        jd = utilities.calc_julian_day_from_ymd(date_time.get_year(), date_time.get_month(), date_time.get_day())
        sec = utilities.calc_sec_since_midnight(date_time.get_hour(), date_time.get_minute(), date_time.get_second())
        ns = date_time.get_nanosecond()
        sun_eci_posn_km = utilities.calc_sun_eci_posn_km(jd, sec, ns)  # get the sun position
        for satellite in satellite_list:
            sat_id = satellite.get_id()
            sat_eci_posn_km = satellite.get_eci_posn()  # get the satellite position
            sat_alt_km = utilities.calc_altitude_km(sat_eci_posn_km) # get the satellite altitude

            ##################################### solar array power calculation #####################################
            sun_occlusion_factor = utilities.calc_sun_occlusion_factor(sat_eci_posn_km, sun_eci_posn_km)
            satid_to_occlusion_factor[sat_id] = sun_occlusion_factor
            irradiance_w_per_m2 = -1352.44 * sun_occlusion_factor + const.SOLAR_CONSTANT
            satid_to_solar_array[sat_id].set_irradiance_wpm2(irradiance_w_per_m2)
            if satid_to_solar_array[sat_id].get_open_circuit_voltage() < satid_to_node_voltage[sat_id] and satid_to_solar_array[sat_id].get_current_ampere() > 0:
                satid_to_solar_array[sat_id].set_current_ampere(0)

            ##################################### capacitor charge calculation #####################################
            capacitor_charge_coulomb = satid_to_capacitor[sat_id].get_charge_coulomb()
            total_load_current_ampere = (satid_to_camera[sat_id].get_power() + satid_to_computer[sat_id].get_power() + satid_to_rx[sat_id].get_power() + satid_to_tx[sat_id].get_power()) / satid_to_node_voltage[sat_id]
            capacitor_charge_coulomb += (satid_to_solar_array[sat_id].get_current_ampere() - total_load_current_ampere) * total_step_in_sec
            if capacitor_charge_coulomb < 0:
                capacitor_charge_coulomb = 0
            satid_to_capacitor[sat_id].set_charge_coulomb(capacitor_charge_coulomb)

            # log the energy system data
            if step_count % 1000 == 0:
                energy_system_file = os.path.join(log_path, f"{sat_id}-energy-system.csv")
                with open(energy_system_file, 'a') as energy_system_handle:
                    energy_system_handle.write(f"{satellite.get_local_time()}, {satid_to_node_voltage[sat_id]}, {satid_to_computer[sat_id].get_power()}, {total_load_current_ampere}, {satid_to_solar_array[sat_id].get_current_ampere()}, {satid_to_capacitor[sat_id].get_charge_coulomb()}\n")
                device_temperature_file = os.path.join(log_path, f"{sat_id}-device-temperature.csv")
                with open(device_temperature_file, 'a') as device_temperature_handle:
                    device_temperature_handle.write(f"{satellite.get_local_time()}, {satid_to_computer[sat_id].get_device_temperature()}\n")
            
            ##################################### simulate the camera #####################################
            if satid_to_camera[sat_id].get_state() == 'IMAGING':
                image_time_s = satid_to_camera[sat_id].get_image_time_s()
                image_task_count = satid_to_camera[sat_id].get_image_task_count()
                readout_task_count = satid_to_camera[sat_id].get_readout_task_count()
                image_duration_s = satid_to_camera[sat_id].image_duration_s
                while image_time_s > image_duration_s and image_task_count > 0:
                    image_time_s -= image_duration_s
                    image_task_count -= 1
                    readout_task_count += 1
                satid_to_camera[sat_id].set_image_time_s(image_time_s)
                satid_to_camera[sat_id].set_image_task_count(image_task_count)
                satid_to_camera[sat_id].set_readout_task_count(readout_task_count)
                if image_task_count == 0:
                    satid_to_camera[sat_id].set_state('READOUT')
            elif satid_to_camera[sat_id].get_state() == 'READOUT':
                readout_time_s = satid_to_camera[sat_id].get_readout_time_s()
                readout_task_count = satid_to_camera[sat_id].get_readout_task_count()
                # compute_task_count = satid_to_computer[sat_id].get_compute_task_count()
                readout_duration_s = satid_to_camera[sat_id].readout_duration_s
                while readout_time_s > readout_duration_s and readout_task_count > 0:
                    readout_time_s -= readout_duration_s
                    readout_task_count -= 1
                    satid_to_computer[sat_id].assign_task() # 自动给computer分配一个任务
                    if satid_to_computer[sat_id].get_state() == 'OFF' and satid_to_capacitor[sat_id].get_charge_coulomb() > COULOMB_COMPUTER: # 如果电量充足，就打开computer
                        satid_to_computer[sat_id].set_state('WORK')
                satid_to_camera[sat_id].set_readout_time_s(readout_time_s)
                satid_to_camera[sat_id].set_readout_task_count(readout_task_count)
                # satid_to_computer[sat_id].set_compute_task_count(compute_task_count)
                if readout_task_count == 0:
                    satid_to_camera[sat_id].set_state('OFF')

            # if satid_to_computer[sat_id].get_state() == 'WORK':
            #     compute_time_s = satid_to_computer[sat_id].get_compute_time_s()
            #     compute_task_count = satid_to_computer[sat_id].get_compute_task_count()
            #     tx_task_count = satid_to_tx[sat_id].get_tx_task_count()
            #     task_duration_s = satid_to_computer[sat_id].task_duration_s
            #     while compute_time_s > task_duration_s and compute_task_count > 0:
            #         compute_time_s -= task_duration_s
            #         compute_task_count -= 1
            #         tx_task_count += 1
            #     satid_to_computer[sat_id].set_compute_time_s(compute_time_s)
            #     satid_to_computer[sat_id].set_compute_task_count(compute_task_count)
            #     satid_to_tx[sat_id].set_tx_task_count(tx_task_count)
            #     if compute_task_count == 0:
            #         satid_to_computer[sat_id].set_state('OFF')

            ##################################### simulate the computer #####################################
            if satid_to_computer[sat_id].get_state() == 'WORK':
                tile_num = satid_to_computer[sat_id].update_task(total_step_in_sec)
                tx_task_count = satid_to_tx[sat_id].get_tx_task_count()
                satid_to_tx[sat_id].set_tx_task_count(tx_task_count + tile_num)
                if satid_to_computer[sat_id].get_power() == 0: # 在开机状态下，如果功率不足，就会自动关机
                    satid_to_computer[sat_id].set_state('OFF')

            satid_to_computer[sat_id].update_temperature(total_step_in_sec)

            ##################################### simulate satellite sensor #####################################
            prev_sense_posn = satid_to_sensor[sat_id].get_prev_sense_posn()
            prev_sense_date_time = satid_to_sensor[sat_id].get_prev_sense_date_time()
            prev_sense_jd = utilities.calc_julian_day_from_ymd(
                prev_sense_date_time.get_year(), prev_sense_date_time.get_month(), prev_sense_date_time.get_day()
            )
            prev_sense_sec = utilities.calc_sec_since_midnight(
                prev_sense_date_time.get_hour(), prev_sense_date_time.get_minute(), prev_sense_date_time.get_second()
            )
            prev_sense_ns = prev_sense_date_time.get_nanosecond()
            prev_sense_lat = utilities.calc_subpoint_latitude(prev_sense_posn)
            prev_sense_lon = utilities.calc_subpoint_longitude(prev_sense_jd, prev_sense_sec, prev_sense_ns, prev_sense_posn)
            sat_lat = utilities.calc_subpoint_latitude(sat_eci_posn_km)
            sat_lon = utilities.calc_subpoint_longitude(jd, sec, ns, sat_eci_posn_km)
            dist_km = utilities.calc_great_circle_arc(sat_lon, sat_lat, prev_sense_lon, prev_sense_lat) * const.WGS_84_A
            if dist_km >= satid_to_threshold_km[sat_id]:
                image_task_count = satid_to_camera[sat_id].get_image_task_count()
                satid_to_camera[sat_id].set_image_task_count(image_task_count + 1)
                satid_to_camera[sat_id].set_state('IMAGING')
                satid_to_threshold_km[sat_id] = satid_to_thresh_coeff[sat_id] * sat_alt_km
                satid_to_sensor[sat_id].update() # update the prev sense position and time
                sensor_image_num += 1
                # log the data
                sensor_trigger_file = os.path.join(log_path, f"{sat_id}-sensor-trigger.csv")
                with open(sensor_trigger_file, 'a') as sensor_trigger_handle:
                    sensor_trigger_handle.write(f"{satellite.get_local_time()}, ")
                    sensor_trigger_handle.write(f"{sat_alt_km}, {sat_eci_posn_km[0]}, {sat_eci_posn_km[1]}, {sat_eci_posn_km[2]}\n")

            ##################################### communication system #####################################
            if satellite.get_gnd_id_com() is not None: # if the satellite is communicating with a ground station
                gnd_id = satellite.get_gnd_id_com()
                ground_station = gndid_to_gnd[gnd_id]
                gnd_lat = ground_station.get_lat()
                gnd_lon = ground_station.get_lon()
                gnd_hae = ground_station.get_hae()
                # 如果卫星在通信范围内，且通信系统是关闭的，且有任务需要发送，则打开通信系统
                if satid_to_tx[sat_id].get_state() == 'OFF' and satid_to_tx[sat_id].get_tx_task_count() > 0 and satid_to_capacitor[sat_id].get_charge_coulomb() > COULOMB_TX:
                    satid_to_tx[sat_id].set_state('TX')
                # if the satellite is not in the communication range, then turn off the communication system
                if utilities.calc_elevation_deg(jd, sec, ns, gnd_lat, gnd_lon, gnd_hae, sat_eci_posn_km) <= 10:
                    satellite.set_gnd_id_com(None)
                    satid_to_tx[sat_id].set_state('OFF')
                    satid_to_rx[sat_id].set_state('OFF')
                    satid_to_computer[sat_id].clear_buffer() # TODO 在经过了通信之后，清空所有任务，即将通信作为一次deadline
                    satid_to_tx[sat_id].set_tx_task_count(0)
                    satid_to_camera[sat_id].set_image_task_count(0)
                    satid_to_camera[sat_id].set_readout_task_count(0)
                    # log
                    communication_file = os.path.join(log_path, f"{sat_id}-communication.csv")
                    with open(communication_file, 'a') as communication_handle:
                        communication_handle.write(f"{satellite.get_local_time()}, {gnd_id} (end), sensor_tile_num = {sensor_image_num * partition_size}, trans_tile_num = {trans_tile_num} \n")
            if satellite.get_gnd_id_com() is None: # if the satellite is not communicating with a ground station
                for ground_station in ground_station_list:
                    gnd_lat = ground_station.get_lat()
                    gnd_lon = ground_station.get_lon()
                    gnd_hae = ground_station.get_hae()
                    gnd_id = ground_station.get_id()
                    if utilities.calc_elevation_deg(jd, sec, ns, gnd_lat, gnd_lon, gnd_hae, sat_eci_posn_km) > 10:
                        satellite.set_gnd_id_com(gnd_id)
                        # log 
                        communication_file = os.path.join(log_path, f"{sat_id}-communication.csv")
                        with open(communication_file, 'a') as communication_handle:
                            communication_handle.write(f"{satellite.get_local_time()}, {gnd_id}\n")
                        satid_to_tx[sat_id].set_state('TX')
                        satid_to_rx[sat_id].set_state('RX')
                        satid_to_rx[sat_id].set_rx_time_s(-sat_alt_km / const.SPEED_OF_LIGHT_KM_S)  # consider the time delay
                        satid_to_tx[sat_id].set_tx_time_s(-sat_alt_km / const.SPEED_OF_LIGHT_KM_S)
                        break
            if satid_to_tx[sat_id].get_state() == 'TX':
                tx_time_s = satid_to_tx[sat_id].get_tx_time_s()
                tx_task_count = satid_to_tx[sat_id].get_tx_task_count()
                tx_duration_s = satid_to_tx[sat_id].tx_duration_s
                while tx_time_s > tx_duration_s and tx_task_count > 0:
                    tx_time_s -= tx_duration_s
                    tx_task_count -= 1
                    trans_tile_num += 1
                satid_to_tx[sat_id].set_tx_time_s(tx_time_s)
                satid_to_tx[sat_id].set_tx_task_count(tx_task_count)
                if tx_task_count == 0:
                    satid_to_tx[sat_id].set_state('OFF')
            if satid_to_rx[sat_id].get_state() == 'RX':
                rx_time_s = satid_to_rx[sat_id].get_rx_time_s()
                rx_duration_s = satid_to_rx[sat_id].rx_duration_s
                if rx_time_s > rx_duration_s:  # all the information is received
                    rx_time_s = 0
                    satid_to_rx[sat_id].set_state('OFF')
                satid_to_rx[sat_id].set_rx_time_s(rx_time_s)

            ##################################### log the data #####################################
            if (satid_to_camera[sat_id].get_state() != satid_to_camera[sat_id].get_prev_state()) or (satid_to_computer[sat_id].get_state() != satid_to_computer[sat_id].get_prev_state()) or (satid_to_rx[sat_id].get_state() != satid_to_rx[sat_id].get_prev_state()) or (satid_to_tx[sat_id].get_state() != satid_to_tx[sat_id].get_prev_state()):
                device_state_file = os.path.join(log_path, f"{sat_id}-device-state.csv")
                with open(device_state_file, 'a') as device_state_handle:
                    device_state_handle.write(f"{satellite.get_local_time()}, ")
                    device_state_handle.write(f"{satid_to_camera[sat_id].get_state()}, {satid_to_computer[sat_id].get_state()}, {satid_to_rx[sat_id].get_state()}, {satid_to_tx[sat_id].get_state()}\n")
                    image_task_count = satid_to_camera[sat_id].get_image_task_count()
                    readout_task_count = satid_to_camera[sat_id].get_readout_task_count()
                    compute_task_count = satid_to_computer[sat_id].get_compute_task_count()
                    tx_task_count = satid_to_tx[sat_id].get_tx_task_count()
                    computer_power = satid_to_computer[sat_id].get_power()
                    device_state_handle.write(f"image_task_count = {image_task_count}, readout_task_count = {readout_task_count}, compute_task_count = {compute_task_count}, tx_task_count = {tx_task_count}, computer_power = {computer_power}\n")


            
        # --------------------- update simulation to the next step --------------------- #
        date_time.update(hour_step, minute_step, second_step, nanosecond_step)
        
        for satellite in satellite_list:
            sat_id = satellite.get_id()
            satellite.update(hour_step, minute_step, second_step, nanosecond_step)
            sat_eci_posn_km = satellite.get_eci_posn()

            ##################################### record the previous state #####################################
            satid_to_camera[sat_id].set_prev_state(satid_to_camera[sat_id].get_state())
            satid_to_computer[sat_id].set_prev_state(satid_to_computer[sat_id].get_state())
            satid_to_rx[sat_id].set_prev_state(satid_to_rx[sat_id].get_state())
            satid_to_tx[sat_id].set_prev_state(satid_to_tx[sat_id].get_state())

            ##################################### update the time of the devices #####################################
            if satid_to_camera[sat_id].get_state() == 'IMAGING':
                image_time_s = satid_to_camera[sat_id].get_image_time_s()
                satid_to_camera[sat_id].set_image_time_s(image_time_s + total_step_in_sec)
            elif satid_to_camera[sat_id].get_state() == 'READOUT':
                readout_time_s = satid_to_camera[sat_id].get_readout_time_s()
                satid_to_camera[sat_id].set_readout_time_s(readout_time_s + total_step_in_sec)
            # computer 的部分在上面已经更新了，包括增加compute_time_s的部分
            # if satid_to_computer[sat_id].get_state() == 'WORK':
            #     compute_time_s = satid_to_computer[sat_id].get_compute_time_s()
            #     satid_to_computer[sat_id].set_compute_time_s(compute_time_s + total_step_in_sec)
            if satid_to_tx[sat_id].get_state() == 'TX':
                tx_time_s = satid_to_tx[sat_id].get_tx_time_s()
                satid_to_tx[sat_id].set_tx_time_s(tx_time_s + total_step_in_sec)
            if satid_to_rx[sat_id].get_state() == 'RX':
                rx_time_s = satid_to_rx[sat_id].get_rx_time_s()
                satid_to_rx[sat_id].set_rx_time_s(rx_time_s + total_step_in_sec)

            ##################################### update the position of the sensor #####################################
            satid_to_sensor[sat_id].set_eci_posn(sat_eci_posn_km)

            ##################################### update the power of the satellite #####################################
            power_w = utilities.calc_max_power_w(
                satid_to_capacitor[sat_id].get_charge_coulomb(),
                satid_to_capacitor[sat_id].get_capacitance_farad(),
                satid_to_solar_array[sat_id].get_current_ampere(),
                satid_to_capacitor[sat_id].get_esr_ohm(),
            )
            # power_w = \
            #     satid_to_camera[sat_id].get_power() + satid_to_computer[sat_id].get_power() + satid_to_rx[sat_id].get_power() + satid_to_tx[sat_id].get_power()
            if (power_w < satid_to_camera[sat_id].get_power() + satid_to_rx[sat_id].get_power() + satid_to_tx[sat_id].get_power()):
                satid_to_camera[sat_id].set_state('OFF')
                satid_to_computer[sat_id].set_state('OFF')
                satid_to_rx[sat_id].set_state('OFF')
                satid_to_tx[sat_id].set_state('OFF')

            # 电量较低时限制设备的使用，防止因为正反馈导致电量耗尽
            if satid_to_capacitor[sat_id].get_charge_coulomb() < COULOMB_COMPUTER:
                satid_to_computer[sat_id].set_state('OFF')
            if satid_to_capacitor[sat_id].get_charge_coulomb() < COULOMB_TX:
                satid_to_tx[sat_id].set_state('OFF')
            if satid_to_capacitor[sat_id].get_charge_coulomb() < COULOMB_CAMERA:
                satid_to_camera[sat_id].set_state('OFF')

            # 更新budget
            computer_power_budget = power_w - satid_to_camera[sat_id].get_power() - satid_to_rx[sat_id].get_power() - satid_to_tx[sat_id].get_power()
            satid_to_computer[sat_id].set_power_budget(computer_power_budget)
            
            node_voltage_discriminant = utilities.calc_node_voltage_discriminant(
                satid_to_capacitor[sat_id].get_charge_coulomb(),
                satid_to_capacitor[sat_id].get_capacitance_farad(),
                satid_to_solar_array[sat_id].get_current_ampere(),
                satid_to_capacitor[sat_id].get_esr_ohm(),
                power_w
            )

            # if (node_voltage_discriminant < 0):
            #     satid_to_camera[sat_id].set_state('OFF')
            #     satid_to_computer[sat_id].set_state('OFF')
            #     satid_to_rx[sat_id].set_state('OFF')
            #     satid_to_tx[sat_id].set_state('OFF')
            #     power_w = \
            #         satid_to_camera[sat_id].get_power() + satid_to_computer[sat_id].get_power() + satid_to_rx[sat_id].get_power() + satid_to_tx[sat_id].get_power()
            #     node_voltage_discriminant = utilities.calc_node_voltage_discriminant(
            #         satid_to_capacitor[sat_id].get_charge_coulomb(),
            #         satid_to_capacitor[sat_id].get_capacitance_farad(),
            #         satid_to_solar_array[sat_id].get_current_ampere(),
            #         satid_to_capacitor[sat_id].get_esr_ohm(),
            #         power_w
            #     )

            node_voltage = utilities.calc_node_voltage(
                node_voltage_discriminant,
                satid_to_capacitor[sat_id].get_charge_coulomb(),
                satid_to_capacitor[sat_id].get_capacitance_farad(),
                satid_to_solar_array[sat_id].get_current_ampere(),
                satid_to_capacitor[sat_id].get_esr_ohm(),
            )
            satid_to_camera[sat_id].set_node_voltage(node_voltage)
            satid_to_computer[sat_id].set_node_voltage(node_voltage)
            satid_to_rx[sat_id].set_node_voltage(node_voltage)
            satid_to_tx[sat_id].set_node_voltage(node_voltage)
            satid_to_node_voltage[sat_id] = node_voltage

            ##################################### update the ground stations #####################################
            for ground_station in ground_station_list:
                ground_station.update(hour_step, minute_step, second_step, nanosecond_step)
        step_count += 1


def test():
    with open("computer_cfg/computer.yaml", 'r') as computer_handle:
        computer_config = yaml.safe_load(computer_handle)
    cfg_path = computer_config['cfg_path']
    print(cfg_path)


if __name__ == "__main__":
    main()
