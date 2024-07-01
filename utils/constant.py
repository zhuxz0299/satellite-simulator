# Unit conversions
MONTH_PER_YEAR = 12
HOUR_PER_DAY = 24
MINUTE_PER_HOUR = 60
SECOND_PER_MINUTE = 60
NANOSECOND_PER_SECOND = 1000000000
MINUTE_PER_DAY = 1440
SECOND_PER_DAY = 86400
SECOND_PER_HOUR = MINUTE_PER_HOUR * SECOND_PER_MINUTE
RAD_PER_DEG = 0.01745329251994329577
RAD_PER_REV = 6.28318530717958647692
M_PER_KM = 1000
KM_PER_AU = 149597870.7

# cote/references/hoots1980models.pdf
STR3_KE =  0.743669161e-1; 
STR3_DU_PER_ER = 1.0;      
STR3_J2 =  1.082616e-3;    
STR3_J3 = -0.253881e-5;    
STR3_J4 = -1.655970e-6;    
STR3_K2 =  5.413080e-4;    
STR3_K4 =  0.62098875e-6;  
STR3_RAD_PER_DEG = 0.174532925e-1; 
STR3_PI = 3.14159265;              
STR3_HALF_PI = 1.57079633;         
STR3_Q0 = 120.0;                   
STR3_S0 = 78.0;                    
STR3_TWO_THIRDS = 0.66666667;      
STR3_TWO_PI = 6.2831853;           
STR3_THREE_HALVES_PI = 4.71238898; 
STR3_KM_PER_ER = 6378.135;         
STR3_MIN_PER_DAY = 1440.0;         
STR3_A30 = 0.253881e-5;            
STR3_RAD_PER_REV = 6.2831853;      

# World Geodetic System 1984 (WGS 84)
# See cote/references/dod2014wgs.pdf
WGS_84_A  = 6378.137;          # Earth semimajor axis km
WGS_84_WE = 7.292115e-5;       # Earth angular velocity rad/sec
WGS_84_F  = 1.0/298.257223563; # Flattening
WGS_84_C  = 2.99792458e8;      # Speed of light in vacuum m/s

# Contemporary precision constants
QUARTER_PI         = 0.78539816339744830962; # pi/4
HALF_PI            = 1.57079632679489661923; # pi/2
PI                 = 3.14159265358979323846; # pi (ref. value)
TWO_PI             = 6.28318530717958647692; # 2*pi
INV_QUARTER_PI     = 1.27323954473516268615; # 4/pi
INV_HALF_PI        = 0.63661977236758134308; # 2/pi
INV_PI             = 0.31830988618379067154; # 1/pi
INV_TWO_PI         = 0.15915494309189533577; # 1/(2*pi)
BOLTZMANN_CONSTANT = 1.380649e-23;           # J/K

# ASTM E-490-00 Standard Extraterrestrial Spectrum Reference 2000
SOLAR_CONSTANT = 1366.1; # Units: watt per meter squared

SUN_RADIUS_KM = 695700.0; # radius of the Sun in kilometers

# other constants
SPEED_OF_LIGHT_KM_S = 299792.458; # speed of light in km/s