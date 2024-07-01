## 文件结构
* `configuration`：放置配置文件的文件夹
* `log`：存储输出内容的文件夹
* `utils`：包含模拟器中需要用到的一些类与函数
* `simulator.py`：模拟器程序

## 运行方法
```bash
python simulator.py ./configuration ./log
```

## 代码结构
* DateTime: 模拟日期时间
  * 初始化参数：年、月、日、时、分、秒、纳秒。`__init__(self, year, month, day, hour, minute, second, nanosecond)`
  * `get_year()`, `get_month()`, `get_day()`, `get_hour()`, `get_minute()`, `get_second()`, `get_nanosecond()`: 获取日期时间的年、月、日、时、分、秒、纳秒
  * `update(*args)`: 更新日期时间
* Sensor: 模拟传感器
  * 初始化参数：传感器位置、全局时间、ID。`__init__(self, eci_posn, global_time, id)`。其中 `global_time` 与 `eci_posn` 为引用传递，保持与模拟器中的时间和位置同步。
  * `get_id()`: 获取传感器的ID
  * `get_eci_posn()`: 获取传感器的位置
  * `get_prev_eci_posn()`: 获取传感器的上一次位置
  * `get_global_time()`: 获取传感器的全局时间
  * `get_prev_sense_date_time()`: 获取传感器的上一次感知时间
  * `set_eci_posn(eci_posn)`: 设置传感器的位置
  * `update()`: 更新传感器上一次感知时间和位置
* Capacitor: 模拟电容器
  * 初始化参数：电容量、等效串联电阻、ID，电荷量默认为0。`__init__(self, capacitance_farad, esr_ohm, id)`
  * `get_capacitance_farad()`: 获取电容器的电容量
  * `get_esr_ohm()`: 获取电容器的等效串联电阻
  * `get_charge_coulomb()`: 获取电容器的电荷量
  * `set_charge_coulomb(charge)`: 设置电容器的电荷量
  * `get_id()`: 获取电容器的ID
* SolarArray: 太阳能电池板
  * 初始化参数：开路电压、面积、效率、ID。`__init__(self, open_circuit_voltage_volt, surface_area_m2, efficiency, id)`
  * `get_open_circuit_voltage_volt()`: 获取太阳能电池板的开路电压
  * `get_surface_area_m2()`: 获取太阳能电池板的面积
  * `get_efficiency()`: 获取太阳能电池板的效率
  * `get_id()`: 获取太阳能电池板的ID
  * `get_current_ampere()`: 获取太阳能电池板的电流
  * `set_current_ampere(current)`: 设置太阳能电池板的电流
  * `set_irradiance_wpm2(irradiance_wpm2)`: 设置太阳能电池板的辐照度
* Device: 模拟设备，包括相机 `Camera`、电脑 `Computer`、信号发送端 `Tx`、信号接收端 `Rx`
  * 初始化参数：无，初始化后 `state` 为 `OFF`，`power` 为 0
  * `set_state(state)`: 设置设备的状态
  * `get_state()`: 获取设备的状态
  * `set_prev_state(state)`: 设置设备的上一次状态
  * `get_prev_state()`: 获取设备的上一次状态
  * `set_node_voltage(voltage)`: 设置设备的节点电压
  * `get_node_voltage()`: 获取设备的节点电压
  * `get_power()`: 获取设备的功率
  * Camera: 相机
    * `set_image_time_s(image_time_s)`: 设置相机的拍照时间
    * `get_image_time_s()`: 获取相机的拍照时间
    * `set_readout_time_s(readout_time_s)`: 设置相机的读取时间
    * `get_readout_time_s()`: 获取相机的读取时间
    * `set_image_task_count(image_task_count)`: 设置相机还需要进行的拍照次数
    * `get_image_task_count()`: 获取相机还需要进行的拍照次数
    * `set_readout_task_count(readout_task_count)`: 设置相机还需要进行的读取次数
    * `get_readout_task_count()`: 获取相机还需要进行的读取次数
  * Computer: 电脑
    * `set_compute_time_s(compute_time_s)`: 设置电脑的计算时间
    * `get_compute_time_s()`: 获取电脑的计算时间
    * `set_compute_task_count(compute_task_count)`: 设置电脑还需要进行的计算次数
    * `get_compute_task_count()`: 获取电脑还需要进行的计算次数
  * Tx: 信号发送端
    * `set_tx_time_s(transmit_time_s)`: 设置信号发送端的发送时间
    * `get_tx_time_s()`: 获取信号发送端的发送时间
    * `set_tx_task_count(transmit_task_count)`: 设置信号发送端还需要进行的发送次数
    * `get_tx_task_count()`: 获取信号发送端还需要进行的发送次数
  * Rx: 信号接收端
    * `set_rx_time_s(receive_time_s)`: 设置信号接收端的接收时间
    * `get_rx_time_s()`: 获取信号接收端的接收时间
* Satellite: 卫星
  * 初始化参数：tle 文件、全局时间。`__init__(self, tle_file, global_time)`。其中 `global_time` 为引用传递，保持与模拟器中的时间同步。
  * `set_id(id)`: 设置卫星的ID
  * `get_id()`: 获取卫星的ID
  * `set_local_time(local_time)`: 设置卫星的本地时间
  * `get_local_time()`: 获取卫星的本地时间
  * `get_eci_posn(eci_posn)`: 设置卫星的位置
  * `update(*args)`: 更新卫星的时间，同时根据时间更新卫星的位置
  * `set_gnd_id_com(gnd_id_com)`: 设置卫星的地面通信站ID
  * `get_gnd_id_com()`: 获取卫星的地面通信站ID
* GroundStation: 地面通信站
  * 初始化参数：经度、纬度、高度、时间、ID。`__init__(self, lat, lon, hae, date_time, id)`。其中 `date_time` 为引用传递，`global_time` 保持与模拟器中的时间同步。
  * `get_hae()`: 获取地面通信站的高度
  * `get_lat()`: 获取地面通信站的纬度
  * `get_lon()`: 获取地面通信站的经度
  * `get_id()`: 获取地面通信站的ID
  * `get_global_time()`: 获取地面通信站的全局时间
  * `get_local_time()`: 获取地面通信站的本地时间
  * `update(*args)`: 更新地面通信站的时间，同时更新地面在在ECI坐标系中的位置


  