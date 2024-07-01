class Capacitor:
    def __init__(self, capacitance_farad, esr_ohm, id):
        self.capacitance_farad = capacitance_farad
        self.esr_ohm = esr_ohm
        self.charge_coulomb = 0.0
        self.id = id

    def get_capacitance_farad(self):
        return self.capacitance_farad
    
    def get_esr_ohm(self):
        return self.esr_ohm
    
    def get_charge_coulomb(self):
        return self.charge_coulomb
    
    def set_charge_coulomb(self, charge_coulomb):
        self.charge_coulomb = charge_coulomb
        return self.charge_coulomb
    
    def get_id(self):
        return self.id
        