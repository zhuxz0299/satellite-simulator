import math
import constant as const


def calc_julian_day_from_ymd(year, month, day):
    jd = (day - 32075 
          + 1461 * (year + 4800 + (month - 14) // 12) // 4 
          + 367 * (month - 2 - (month - 14) // 12 * 12) // 12 
          - 3 * ((year + 4900 + (month - 14) // 12) // 100) // 4)
    return jd - 0.5 - 1 # TODO -1 is a fudge factor

def calc_sec_since_midnight(hour, minute, second):
    return hour * 3600 + minute * 60 + second


def calc_sun_eci_posn_km(julian_day, second, nanosecond):
    JD = julian_day + (second + nanosecond / const.NANOSECOND_PER_SECOND) / const.SECOND_PER_DAY
    n = JD - 2451545.0
    g_deg = 357.528 + 0.9856003 * n
    g_rad = g_deg * const.RAD_PER_DEG
    R_au = 1.00014 - 0.01671 * math.cos(g_rad) - 0.00014 * math.cos(2 * g_rad)
    L_deg = 280.460 + 0.9856474 * n
    lambda_deg = L_deg + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)
    lambda_rad = lambda_deg * const.RAD_PER_DEG
    epsilon_deg = 23.439 - 0.0000004 * n
    epsilon_rad = epsilon_deg * const.RAD_PER_DEG
    sun_eci_posn_km = \
        [
            const.KM_PER_AU * R_au * math.cos(lambda_rad),
            const.KM_PER_AU * R_au * math.sin(lambda_rad) * math.cos(epsilon_rad),
            const.KM_PER_AU * R_au * math.sin(lambda_rad) * math.sin(epsilon_rad)
        ]
    return sun_eci_posn_km


def calc_separation_vector(end, start):
    return [end[0] - start[0], end[1] - start[1], end[2] - start[2]]


def calc_angular_radius(radius_km, distance_km):
    return math.asin(radius_km / distance_km)


def magnitude(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)


def dot_product(vector1, vector2):
    return vector1[0] * vector2[0] + vector1[1] * vector2[1] + vector1[2] * vector2[2]


def calc_angle_between(vector1, vector2):
    return math.acos(dot_product(vector1, vector2) / (magnitude(vector1) * magnitude(vector2)))


def calc_sun_occlusion_factor(sat_eci_km, sun_eci_km, flag=False): # TODO remove flag
    earth_eci_km = [0, 0, 0]
    sat_to_earth = calc_separation_vector(earth_eci_km, sat_eci_km)
    sat_to_sun = calc_separation_vector(sun_eci_km, sat_eci_km)
    ang_radius_earth = calc_angular_radius(const.WGS_84_A, magnitude(sat_to_earth))
    ang_radius_sun = calc_angular_radius(const.SUN_RADIUS_KM, magnitude(sat_to_sun))
    ang_between_earth_sun = calc_angle_between(sat_to_earth, sat_to_sun)
    intersection_chord_length_radicand = (
        (-1.0 * ang_between_earth_sun + ang_radius_sun - ang_radius_earth) *
        (-1.0 * ang_between_earth_sun - ang_radius_sun + ang_radius_earth) *
        (-1.0 * ang_between_earth_sun + ang_radius_sun + ang_radius_earth) *
        (ang_between_earth_sun + ang_radius_sun + ang_radius_earth)
    )
    if flag:
        print("sat_to_earth", sat_to_earth)
        print("sat_to_sun", sat_to_sun)
        print("ang_radius_earth", ang_radius_earth)
        print("ang_radius_sun", ang_radius_sun)
        print("ang_between_earth_sun", ang_between_earth_sun)
        print("intersection_chord_length_radicand", intersection_chord_length_radicand)

    if ang_between_earth_sun >= (ang_radius_earth + ang_radius_sun):
        return 0.0
    elif intersection_chord_length_radicand <= 0.0:
        return 1.0
    else:
        return (
            ang_radius_sun ** 2.0 * math.acos(
                (ang_between_earth_sun ** 2.0 + ang_radius_sun ** 2.0 - ang_radius_earth ** 2.0) /
                (2.0 * ang_between_earth_sun * ang_radius_sun)) +
            ang_radius_earth ** 2.0 * math.acos(
                (ang_between_earth_sun ** 2.0 + ang_radius_earth ** 2.0 - ang_radius_sun ** 2.0) /
                (2.0 * ang_between_earth_sun * ang_radius_earth)) -
            0.5 * math.sqrt(
                (-1.0 * ang_between_earth_sun + ang_radius_sun + ang_radius_earth) *
                (ang_between_earth_sun + ang_radius_sun - ang_radius_earth) *
                (ang_between_earth_sun - ang_radius_sun + ang_radius_earth) *
                (ang_between_earth_sun + ang_radius_sun + ang_radius_earth)
            )) / (const.PI * ang_radius_sun ** 2.0)


def calc_tdiff_min(year_event, month_event, day_event, hour_event, minute_event, second_event, nanosecond_event, year_epoch, month_epoch, day_epoch, hour_epoch, minute_epoch, second_epoch, nanosecond_epoch):
    event_jd = calc_julian_day_from_ymd(year_event, month_event, day_event)
    event_sc = calc_sec_since_midnight(hour_event, minute_event, second_event)
    event_ns = nanosecond_event
    epoch_jd = calc_julian_day_from_ymd(year_epoch, month_epoch, day_epoch)
    epoch_sc = calc_sec_since_midnight(hour_epoch, minute_epoch, second_epoch)
    epoch_ns = nanosecond_epoch
    return (event_jd - epoch_jd) * const.MINUTE_PER_DAY + (event_sc - epoch_sc)/const.SECOND_PER_MINUTE + (event_ns - epoch_ns)/const.NANOSECOND_PER_SECOND/const.SECOND_PER_MINUTE


def sgp4(bstar, i0, o0, e0, w0, m0, n0, tsince):
    # Recover mean motion and semimajor axis     # line001-line013 boilerplate
    a1 = (const.STR3_KE/n0)**const.STR3_TWO_THIRDS  # eq01,line014
    cosi0 = math.cos(i0)                            # line015
    thetar2 = cosi0*cosi0                           # eq10,line016
    thetar2t3m1 = thetar2*3-1.0                     # line017
    # omit line018
    beta0r2 = 1.0-e0*e0                            # line019
    beta0 = math.sqrt(beta0r2)                      # eq12, line020
    delta1 = 1.5*const.STR3_K2*thetar2t3m1/(a1*a1*beta0*beta0r2)  # eq02,line021
    a0 = a1*(1-0.5*const.STR3_TWO_THIRDS*delta1-delta1*delta1-(134.0/81.0)*delta1*delta1*delta1)  # eq03,line022
    delta0 = 1.5*const.STR3_K2*thetar2t3m1/(a0*a0*beta0*beta0r2)  # eq04,line023
    n0pp = n0/(1.0+delta0)                         # eq05,line024
    a0pp = a0/(1.0-delta0)                         # eq06,line025
    # Check if perigee height is less than 220 km   // line026-line033 comments
    isimp = False                                   # line034
    if a0pp*(1-e0)/const.STR3_DU_PER_ER < (220/const.STR3_KM_PER_ER+const.STR3_DU_PER_ER):
        isimp = True                                # line035
    # line036-line039 comments
    # Set constants based on perigee height
    q0msr4temp = ((const.STR3_Q0 - const.STR3_S0) * const.STR3_DU_PER_ER / const.STR3_KM_PER_ER) ** 4.0
    stemp = const.STR3_DU_PER_ER * (1.0 + const.STR3_S0 / const.STR3_KM_PER_ER)
    perigee = (a0pp * (1.0 - e0) - const.STR3_DU_PER_ER) * const.STR3_KM_PER_ER
    if perigee <= 98.0:
        stemp = 20.0
        q0msr4temp = ((const.STR3_Q0 - stemp) * const.STR3_DU_PER_ER / const.STR3_KM_PER_ER) ** 4.0
        stemp = stemp / const.STR3_KM_PER_ER + const.STR3_DU_PER_ER
    elif perigee < 156.0:
        stemp = perigee - const.STR3_S0
        q0msr4temp = ((const.STR3_Q0 - stemp) * const.STR3_DU_PER_ER / const.STR3_KM_PER_ER) ** 4.0
        stemp = stemp / const.STR3_KM_PER_ER + const.STR3_DU_PER_ER

    q0msr4 = q0msr4temp                # QOMS24   // eq09,line041
    s = stemp                          # S4       // line040
    xi = 1.0 / (a0pp - s)              # TSI      // eq11,line050
    eta = a0pp * e0 * xi               # eq13,line051
    etar2 = eta * eta  # // line052
    e0eta = e0 * eta                   # EETA     // line053
    psi = abs(1.0 - etar2)            # PSISQ    // line054
    q0msr4txir4 = q0msr4 * xi ** 4.0   # COEF     // line055
    q0msr4txir4dpsir3p5 = q0msr4txir4 / psi ** 3.5  # COEF1    // line056

    c2 = (q0msr4txir4dpsir3p5 * n0pp *
          (a0pp * (1.0 + 1.5 * etar2 + 4.0 * e0eta + e0eta * etar2) +
           0.75 * const.STR3_K2 * xi / psi * thetar2t3m1 *
           (8.0 + 24.0 * etar2 + 3.0 * etar2 * etar2)))  # eq14,line057
    c1 = bstar * c2  # eq15,line059
    sini0 = math.sin(i0)  # SINIO    // line060
    a30dk2 = (const.STR3_A30 / const.STR3_K2 * const.STR3_DU_PER_ER ** 3.0)  # A3OVK2  #omit? line061
    c3 = (q0msr4txir4 * xi * a30dk2 * n0pp * const.STR3_DU_PER_ER * sini0 / e0)  # eq16,line062
    nthetar2a1 = -thetar2 + 1.0  # X1MTH2  # line063
    c4 = (2.0 * n0pp * q0msr4txir4dpsir3p5 * a0pp * beta0r2 *
          ((2.0 * eta * (1.0 + e0eta) + 0.5 * e0 + 0.5 * eta * etar2) -
           (2.0 * const.STR3_K2 * xi / (a0pp * psi)) *
              (-3.0 * thetar2t3m1 * (1.0 + 1.5 * etar2 - 2.0 * e0eta - 0.5 * e0eta * etar2) +
               0.75 * nthetar2a1 * (2.0 * etar2 - e0eta - e0eta * etar2) *
               math.cos(2.0 * w0))))  # eq17,line064

    thetar4 = thetar2 * thetar2                           # line070
    pinvsq = 1.0 / (a0pp * a0pp * beta0r2 * beta0r2)     # line049
    k2m3pinvsqn0pp = const.STR3_K2 * 3.0 * pinvsq * n0pp  # TEMP1 line071
    k2r2m3pinvsqr2n0pp = k2m3pinvsqn0pp * const.STR3_K2 * pinvsq  # TEMP2 line072
    k4m1p25pinvsqr2n0pp = const.STR3_K4 * 1.25 * pinvsq * pinvsq * n0pp  # TEMP3 line073
    mdt = (n0pp +
           k2m3pinvsqn0pp * thetar2t3m1 * beta0 * 0.5 +
           k2r2m3pinvsqr2n0pp * (13.0 - 78.0 * thetar2 + 137.0 * thetar4) * beta0 * 0.0625)  # line074
    n5thetar2a1 = -5.0 * thetar2 + 1.0                    # X1M5TH line076
    wdt = (k2m3pinvsqn0pp * n5thetar2a1 * -0.5 +
           k2r2m3pinvsqr2n0pp * (7.0 - 114.0 * thetar2 + 395.0 * thetar4) * 0.0625 +
           k4m1p25pinvsqr2n0pp * (3.0 - 36.0 * thetar2 + 49.0 * thetar4))  # line077
    odt = (-1.0 * k2m3pinvsqn0pp * cosi0 +
           k2r2m3pinvsqr2n0pp * (4.0 * cosi0 - 19.0 * cosi0 * thetar2) * 0.5 +
           k4m1p25pinvsqr2n0pp * cosi0 * (3.0 - 7.0 * thetar2) * 2.0)  # line080
    mdf = m0 + mdt * tsince                                # eq22,line105
    wdf = w0 + wdt * tsince                                # eq23,line106
    odf = o0 + odt * tsince                                # eq24,line107
    uo = -3.5 * beta0r2 * k2m3pinvsqn0pp * cosi0 * c1      # l79+ line084
    tsincer2 = tsince * tsince                               # line110
    mptemp = mdf                                             # line109
    wtemp = wdf                                              # line108
    uatemp = 1.0 - c1 * tsince                               # TEMPA line112
    uetemp = bstar * c4 * tsince                             # TEMPE line113
    ultemp = 1.5 * c1 * tsincer2                             # TEMPL l85+ line114
    if not isimp:
        c1r2 = c1 * c1                                        # line092
        c5 = 2.0 * q0msr4txir4dpsir3p5 * a0pp * beta0r2 * (1.0 + 2.75 * (etar2 + e0eta) + e0eta * etar2)  # eq18,line069
        d2 = 4.0 * a0pp * xi * c1r2                            # eq19,line093
        d3 = d2 * xi * c1 * (17.0 * a0pp + s) / 3.0            # eq20,line095
        d4 = 0.5 * d2 * xi * xi * c1r2 * a0pp * (221.0 * a0pp + 31.0 * s) / 3.0  # eq21,line096
        deltaw = bstar * c3 * math.cos(w0) * tsince                 # eq25,line116
        deltam = -1.0 * const.STR3_TWO_THIRDS * q0msr4txir4 * bstar * const.STR3_DU_PER_ER / e0eta * \
            ((1.0 + eta * math.cos(mdf)) ** 3.0 - (1.0 + eta * math.cos(m0)) ** 3.0)  # eq26,line117
        mptemp = mptemp + deltaw + deltam                      # line119
        wtemp = wtemp - deltaw - deltam                        # line120
        uatemp = uatemp - d2 * tsincer2 - d3 * tsincer2 * tsince - d4 * tsince * tsincer2 * tsince  # line123
        uetemp = uetemp + bstar * c5 * (math.sin(mptemp) - math.sin(m0))  # line124
        ultemp = ultemp + \
            (d2 + 2.0 * c1r2) * tsincer2 * tsince + \
            0.25 * (3.0 * d3 + 12.0 * c1 * d2 + 10.0 * c1r2 * c1) * tsince * tsincer2 * tsince + \
            0.2 * (3.0 * d4 + 12.0 * c1 * d3 + 6.0 * d2 * d2 + 30.0 * c1r2 * d2 + 15.0 * c1r2 * c1r2) * tsince * tsincer2 * tsince * tsince  # line125
    mp = mptemp                                      # eq27,line109
    w = wtemp                                        # eq28,line108
    o = odf + uo * tsincer2                         # eq29,line111
    a = a0pp * (uatemp ** 2.0)                      # eq31,line127
    e = e0 - uetemp                                 # eq30,line128
    l = mp + w + o + n0pp * ultemp                  # eq32,line129
    beta = math.sqrt(1.0 - e * e)                   # eq33,line130
    n = const.STR3_KE / (a ** 1.5)                  # eq34,line131
    # Long period periodics                         # line132-line134 comments
    axn = e * math.cos(w)                                    # eq35,line135
    ull = 0.125 * a30dk2 * sini0 * (3.0 + 5.0 * cosi0) / (1.0 + cosi0)  # XLCOF line086
    ll = axn * ull / (a * beta * beta)                         # eq36,line137
    uaynl = 0.25 * a30dk2 * sini0                                # AYCOF line087
    aynl = uaynl / (a * beta * beta)                            # eq37,line138
    lt = l + ll                                                 # eq38,line139
    ayn = e * math.sin(w) + aynl                                # eq39,line140
    # Solve Kepler's equation                       # line141-line143 comments
    # FMOD /////////////////////////////////////////////////////// # FUNC FMOD
    utemp = (lt - o) % const.STR3_TWO_PI             # eq40,line144
    if utemp < 0.0:
        utemp += const.STR3_TWO_PI
    u = utemp
    # FMOD /////////////////////////////////////////////////////// # END  FMOD
    eawprev = u                                      # eq43,line145
    for i in range(10):                             # line146
        eawcurr = eawprev + \
            (u - ayn * math.cos(eawprev) + axn * math.sin(eawprev) - eawprev) / \
            (1.0 - ayn * math.sin(eawprev) - axn * math.cos(eawprev))  # eq41,line153
        if abs(eawcurr - eawprev) <= 1.0e-6:         # line154
            break                                    # omit line151
        eawprev = eawcurr                            # line155
    # line156-line158 comments
    eaw = eawprev
    # Short period periodics
    sineaw = math.sin(eaw)                                    # line147
    coseaw = math.cos(eaw)                                    # line148
    ecose = axn * coseaw + ayn * sineaw                       # eq44,line159
    esine = axn * sineaw - ayn * coseaw                       # eq45,line160
    elr2 = axn * axn + ayn * ayn                               # eq46,line161
    pl = a * (1.0 - elr2)                                    # eq47,line163
    r = a * (1.0 - ecose)                                    # eq48,line164
    rdt = const.STR3_KE * math.sqrt(a) * esine / r            # eq49,line166
    rfdt = const.STR3_KE * math.sqrt(pl) / r                 # eq50,line167
    cosu = a * (coseaw - axn + ayn * esine / (1.0 + math.sqrt(1.0 - elr2))) / r   # eq51,line171
    sinu = a * (sineaw - ayn - axn * esine / (1.0 + math.sqrt(1.0 - elr2))) / r   # eq52,line172
    # ACTAN /////////////////////////////////////////////////// # FUNC ACTAN
    lowerutemp = 0.0
    if cosu == 0.0:
        if sinu == 0.0:
            lowerutemp = 0.0
        elif sinu > 0.0:
            lowerutemp = const.STR3_HALF_PI
        else:
            lowerutemp = const.STR3_THREE_HALVES_PI
    elif cosu > 0.0:
        if sinu == 0.0:
            lowerutemp = 0.0
        elif sinu > 0.0:
            lowerutemp = math.atan(sinu / cosu)
        else:
            lowerutemp = const.STR3_TWO_PI + math.atan(sinu / cosu)
    else:
        lowerutemp = const.STR3_PI + math.atan(sinu / cosu)
    # ACTAN /////////////////////////////////////////////////// # END  ACTAN
    loweru = lowerutemp                                     # eq53,line173
    sin2u = 2.0 * sinu * cosu  # line174
    cos2u = 2.0 * cosu * cosu - 1.0  # line175
    # omit line176
    # omit line177
    # omit line178
    # line179-line181 comments
    deltar = 0.5 * const.STR3_K2 * nthetar2a1 * cos2u / pl   # eq54fline182
    deltau = -0.25 * const.STR3_K2 * (7.0 * thetar2 - 1.0) * sin2u / (pl * pl)  # eq55fline183
    deltao = 1.5 * const.STR3_K2 * cosi0 * sin2u / (pl * pl)  # eq56fline184
    deltai = 1.5 * const.STR3_K2 * cosi0 * sini0 * cos2u / (pl * pl)  # eq57fline185
    deltardt = -1.0 * const.STR3_K2 * n * nthetar2a1 * sin2u / pl  # eq58fline186
    deltarfdt = const.STR3_K2 * n * (nthetar2a1 * cos2u + 1.5 * thetar2t3m1) / pl  # eq59fline187
    rk = r * (1.0 - 1.5 * const.STR3_K2 * math.sqrt(1.0 - elr2) * thetar2t3m1 / (pl * pl)) + deltar  # eq60,line182
    uk = u + deltau            # eq61,line183
    ok = o + deltao            # eq62,line184
    ik = i0 + deltai           # eq63,line185
    rkdt = rdt + deltardt      # eq64,line186
    rfkdt = rfdt + deltarfdt   # eq65,line187
    # Unit orientation vectors                      # line188-line190 comments
    sinuk = math.sin(uk)  # line191
    cosuk = math.cos(uk)  # line192
    sinik = math.sin(ik)  # line193
    cosik = math.cos(ik)  # line194
    sinok = math.sin(ok)  # line195
    cosok = math.cos(ok)  # line196
    mx = -1.0 * sinok * cosik  # eq68,line197
    my = cosok * cosik         # eq69,line198
    mz = sinik                 # eq70
    nx = cosok                 # eq71
    ny = sinok                 # eq72
    nz = 0.0                   # eq73
    ux = mx * sinuk + nx * cosuk   # eq66,line199
    uy = my * sinuk + ny * cosuk   # |   ,line200
    uz = mz * sinuk + nz * cosuk   # -   ,line201
    vx = mx * cosuk - nx * sinuk   # eq67,line202
    vy = my * cosuk - ny * sinuk   # |   ,line203
    vz = mz * cosuk - nz * sinuk   # -   ,line204
    # Position and velocity                         # line205-line207 comments
    px = rk * ux               # eq74,line208
    py = rk * uy               # |   ,line209
    pz = rk * uz               # -   ,line210
    sx = rkdt * ux + rfkdt * vx   # eq75,line211
    sy = rkdt * uy + rfkdt * vy   # |   ,line212
    sz = rkdt * uz + rfkdt * vz   # -   ,line213
    # Return ECI position
    eciPosn = [
        px * const.STR3_KM_PER_ER / const.STR3_DU_PER_ER,
        py * const.STR3_KM_PER_ER / const.STR3_DU_PER_ER,
        pz * const.STR3_KM_PER_ER / const.STR3_DU_PER_ER]
    return eciPosn


def calc_max_power_w(charge_c, capacitance_f, current_a, esr_ohm):
    epsilon = 1e-6
    return (esr_ohm * current_a + charge_c / capacitance_f) ** 2 / (4 * esr_ohm) - epsilon # epsilon to avoid invalid discriminant

def calc_node_voltage_discriminant(charge_c, capacitance_f, current_a, esr_ohm, power_w):
    return (charge_c / capacitance_f + current_a * esr_ohm) ** 2 - 4 * power_w * esr_ohm


def calc_node_voltage(discriminant, charge_c, capacitance_f, current_a, esr_ohm):
    return 0.5 * (charge_c / capacitance_f + current_a * esr_ohm + math.sqrt(discriminant))

def calc_altitude_km(eci_posn_sat): # DONE
    r = math.sqrt(eci_posn_sat[0] ** 2 + eci_posn_sat[1] ** 2)
    if r == 0:
        return magnitude(eci_posn_sat) - const.WGS_84_A * (1 - const.WGS_84_F)
    z = eci_posn_sat[2]
    if z == 0:
        return magnitude(eci_posn_sat) - const.WGS_84_A
    a = const.WGS_84_A
    b = (-1 if z < 0 else 1) * const.WGS_84_A * (1 - const.WGS_84_F)
    e = (b * z - (a**2 - b**2)) / (a * r)
    f = (b * z + (a**2 - b**2)) / (a * r)
    p = (4 / 3) * (e * f + 1)
    q = 2 * (e**2 - f**2)
    d = p**3 + q**2
    vp = 0
    if d < 0:
        vp = 2 * math.sqrt(-p) * math.cos(math.acos(q / (p * math.sqrt(-p))) / 3)
    else:
        vp = (math.sqrt(d) - q)**(1/3) - (q + math.sqrt(d))**(1/3)
    if vp**2 < abs(p):
        vp = -(vp**3 + 2 * q) / (3 * p)
    v = vp
    g = (math.sqrt(e**2 + v) + e) / 2
    t = math.sqrt(g**2 + (f - v * g) / (2 * g - e)) - g
    lat = math.atan(a * (1 - t**2) / (2 * b * t))
    return (r - a * t) * math.cos(lat) + (z - b) * math.sin(lat)

def calc_subpoint_latitude(eci_posn_sat):
    r = math.sqrt(eci_posn_sat[0] ** 2 + eci_posn_sat[1] ** 2)
    if r == 0:
        return magnitude(eci_posn_sat) - const.WGS_84_A * (1 - const.WGS_84_F)
    z = eci_posn_sat[2]
    if z == 0:
        return magnitude(eci_posn_sat) - const.WGS_84_A
    a = const.WGS_84_A
    b = (-1 if z < 0 else 1) * const.WGS_84_A * (1 - const.WGS_84_F)
    e = (b * z - (a**2 - b**2)) / (a * r)
    f = (b * z + (a**2 - b**2)) / (a * r)
    p = (4 / 3) * (e * f + 1)
    q = 2 * (e**2 - f**2)
    d = p**3 + q**2
    vp = 0
    if d < 0:
        vp = 2 * math.sqrt(-p) * math.cos(math.acos(q / (p * math.sqrt(-p))) / 3)
    else:
        vp = (math.sqrt(d) - q)**(1/3) - (q + math.sqrt(d))**(1/3)
    if vp**2 < abs(p):
        vp = -(vp**3 + 2 * q) / (3 * p)
    v = vp
    g = (math.sqrt(e**2 + v) + e) / 2
    t = math.sqrt(g**2 + (f - v * g) / (2 * g - e)) - g
    return math.atan(a * (1 - t**2) / (2 * b * t)) / const.RAD_PER_DEG

def calc_gmst_rad_from_ut1(julian_day, second, nanosecond):
    t_u = (julian_day - 2451545.0) / 36525.0
    gmst_0h_sec = 24110.54841 + 8640184.812866 * t_u + 0.093104 * t_u**2 - 6.2e-6 * t_u**3
    rpinv = 1.002737909350795 + 5.9006e-11 * t_u - 5.9e-15 * t_u**2
    gmst_sec = gmst_0h_sec + (second + nanosecond / const.NANOSECOND_PER_SECOND) * rpinv
    gmst_sec = gmst_sec % const.SECOND_PER_DAY
    if gmst_sec < 0:
        gmst_sec += const.SECOND_PER_DAY
    return 2 * const.PI * gmst_sec / const.SECOND_PER_DAY

def calc_subpoint_longitude(julian_day, second, nanosecond, eci_posn_sat):
    zrot = calc_gmst_rad_from_ut1(julian_day, second, nanosecond)
    return (math.atan2(eci_posn_sat[1], eci_posn_sat[0]) - zrot) / const.RAD_PER_DEG

def calc_great_circle_arc(az1_deg, el1_deg, az2_deg, el2_deg):
    az1 = az1_deg * const.RAD_PER_DEG
    el1 = el1_deg * const.RAD_PER_DEG
    az2 = az2_deg * const.RAD_PER_DEG
    el2 = el2_deg * const.RAD_PER_DEG
    daz = abs(az1 - az2)
    return math.atan2(
        math.sqrt((math.cos(el2) * math.sin(daz))**2 + (math.cos(el1) * math.sin(el2) - math.sin(el1) * math.cos(el2) * math.cos(daz))**2),
        math.sin(el1) * math.sin(el2) + math.cos(el1) * math.cos(el2) * math.cos(daz)
    )

def dt_lla_to_eci(julian_day, second, nanosecond, lat, lon, alt):
    zrot = calc_gmst_rad_from_ut1(julian_day, second, nanosecond)
    c = const.WGS_84_A / math.sqrt(1 + const.WGS_84_F * (const.WGS_84_F - 2) * math.sin(lat)**2)
    s = (const.WGS_84_F - 1)**2 * c
    eci_posn = [
        (c + alt) * math.cos(lat) * math.cos(zrot + lon),
        (c + alt) * math.cos(lat) * math.sin(zrot + lon),
        (s + alt) * math.sin(lat)
    ]
    return eci_posn

def dt_eci_to_sez(julian_day, second, nanosecond, lat, lon, eci_vector):
    zrot = calc_gmst_rad_from_ut1(julian_day, second, nanosecond)
    s = \
        math.sin(lat) * math.cos(zrot + lon) * eci_vector[0] + \
        math.sin(lat) * math.sin(zrot + lon) * eci_vector[1] - \
        math.cos(lat) * eci_vector[2]
    e = -math.sin(zrot + lon) * eci_vector[0] + math.cos(zrot + lon) * eci_vector[1]
    z = \
        math.cos(lat) * math.cos(zrot + lon) * eci_vector[0] + \
        math.cos(lat) * math.sin(zrot + lon) * eci_vector[1] + \
        math.sin(lat) * eci_vector[2]
    sez_vector = [s, e, z]
    return sez_vector

def calc_elevation_deg(julian_day, second, nanosecond, lat, lon, alt, eci_posn_sat):
    eci_posn_gnd = dt_lla_to_eci(julian_day, second, nanosecond, lat, lon, alt)
    dx = eci_posn_sat[0] - eci_posn_gnd[0]
    dy = eci_posn_sat[1] - eci_posn_gnd[1]
    dz = eci_posn_sat[2] - eci_posn_gnd[2]
    dist = math.sqrt(dx**2 + dy**2 + dz**2)
    eci_vector = [dx, dy, dz]
    sez_vector = dt_eci_to_sez(julian_day, second, nanosecond, lat, lon, eci_vector)
    return math.asin(sez_vector[2] / dist) / const.RAD_PER_DEG
    

# if __name__ == '__main__':
#     print(calc_julian_day_from_ymd(2021, 1, 1))
