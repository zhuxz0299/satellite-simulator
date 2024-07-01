class SolarArray:
    def __init__(self, open_circuit_voltage, surface_area_m2, efficiency, id):
        self.open_circuit_voltage = open_circuit_voltage
        self.surface_area_m2 = surface_area_m2
        self.efficiency = efficiency
        self.current_ampere = 0
        self.id = id
        
    def get_open_circuit_voltage(self):
        return self.open_circuit_voltage
    
    def get_surface_area_m2(self):
        return self.surface_area_m2
    
    def get_efficiency(self):
        return self.efficiency
    
    def get_current_ampere(self):
        return self.current_ampere
    
    def set_current_ampere(self, current_ampere):
        self.current_ampere = current_ampere

    def set_irradiance_wpm2(self, irradiance_wpm2):
        self.current_ampere = self.efficiency * self.surface_area_m2 * irradiance_wpm2 / self.open_circuit_voltage
    
    def get_id(self):
        return self.id
