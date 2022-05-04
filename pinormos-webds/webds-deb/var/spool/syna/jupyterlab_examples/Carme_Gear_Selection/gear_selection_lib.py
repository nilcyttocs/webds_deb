import numpy
import struct
import tunePDNR_covMat_v3

debug = False

pdnr_tuning = []
pdnr_index = 0

baseline_frames = 16
gram_data_frames = 16
covmat_cmd_arg = [baseline_frames & 0xff, (baseline_frames >> 8) & 0xff, gram_data_frames & 0xff, (gram_data_frames >> 8) & 0xff]

def log(message):
    if debug:
        print(message)
    else:
        pass

def convert_chunk(i):
    return struct.unpack('<f', bytearray(i))[0]

def convert_to_float(i, n):
    for x in range(0, len(i), n):
        chunk = i[x:n+x]
        if len(chunk) < n:
            break
        yield convert_chunk(chunk)

def set_static_config(tc, static):
    tc.sendCommand(56)
    v = tc.getResponse(3)
    arg = tc.decoder.encodeStaticConfig(static)
    tc.sendCommand(57, arg)
    v = tc.getResponse(3)
    tc.sendCommand(55)
    v = tc.getResponse(3)

def set_dynamic_config(tc, dynamic):
    tc.setDynamicConfig(dynamic)

def set_pdnr(static, basisAmpStdevTransRx, basisVectorsTransRx, basisAmpStdevAbsRx, basisVectorsAbsRx, basisAmpStdevAbsTx, basisVectorsAbsTx):
    static['ifpConfig.pdnrConfigs[0].basisAmpStdevTransRx'] = basisAmpStdevTransRx
    static['ifpConfig.pdnrConfigs[0].basisVectorsTransRx'] = basisVectorsTransRx
    static['ifpConfig.pdnrConfigs[0].basisAmpStdevAbsRx'] = basisAmpStdevAbsRx
    static['ifpConfig.pdnrConfigs[0].basisVectorsAbsRx'] = basisVectorsAbsRx
    static['ifpConfig.pdnrConfigs[0].basisAmpStdevAbsTx'] = basisAmpStdevAbsTx
    static['ifpConfig.pdnrConfigs[0].basisVectorsAbsTx'] = basisVectorsAbsTx

def set_pdnr_to_zeros(static):
    set_pdnr(static,
             [0] * len(static['ifpConfig.pdnrConfigs[0].basisAmpStdevTransRx']),
             [0] * len(static['ifpConfig.pdnrConfigs[0].basisVectorsTransRx']),
             [0] * len(static['ifpConfig.pdnrConfigs[0].basisAmpStdevAbsRx']),
             [0] * len(static['ifpConfig.pdnrConfigs[0].basisVectorsAbsRx']),
             [0] * len(static['ifpConfig.pdnrConfigs[0].basisAmpStdevAbsTx']),
             [0] * len(static['ifpConfig.pdnrConfigs[0].basisVectorsAbsTx']))

def set_trans_sensing_freqs(static, integDur, rstretchDur):
    static['integDur'][2] = integDur
    static['daqParams.freqTable[2].rstretchDur'] = rstretchDur

def set_absTx_sensing_freqs(static, integDur, rstretchDur):
    static['integDur'][4] = integDur
    static['daqParams.freqTable[4].rstretchDur'] = rstretchDur

def set_absRx_sensing_freqs(static, integDur, rstretchDur):
    static['integDur'][3] = integDur
    static['daqParams.freqTable[3].rstretchDur'] = rstretchDur

def set_trans_gears(tc, gears, num_gears):
    if not gears:
        return
    integDur = gears[0]
    rstretchDur = [0] * num_gears
    for idx in range(1, len(gears)):
        rstretchDur[idx] = gears[idx] - integDur
    tc.reset()
    static = tc.getStaticConfig()
    set_trans_sensing_freqs(static, integDur, rstretchDur)
    set_static_config(tc, static)
    tc.commitConfig()

def set_abs_gears(tc, gears, num_gears):
    if not gears:
        return
    integDur = gears[0]
    rstretchDur = [0] * num_gears
    for idx in range(1, len(gears)):
        rstretchDur[idx] = gears[idx] - integDur
    tc.reset()
    static = tc.getStaticConfig()
    set_absTx_sensing_freqs(static, integDur, rstretchDur)
    set_absRx_sensing_freqs(static, integDur, rstretchDur)
    set_static_config(tc, static)
    tc.commitConfig()

def clear_pdnr_tuning():
    global pdnr_tuning
    global pdnr_index
    pdnr_tuning = []
    pdnr_index = 0

def pre_pdnr_sweep(tc, int_durs, num_gears):
    tc.reset()
    static = tc.getStaticConfig()
    set_pdnr_to_zeros(static)
    static['adnsEnabled'] = 1
    set_static_config(tc, static)
    dynamic = tc.getDynamicConfig()
    dynamic['disableNoiseMitigation'] = 1
    dynamic['inhibitFrequencyShift'] = 1
    dynamic['requestedFrequency'] = 0
    dynamic['requestedFrequencyAbs'] = 0
    set_dynamic_config(tc, dynamic)
    rx_count = static['rxCount']
    tx_count = static['txCount']
    pdnr_tuning.append([])
    for int_dur in int_durs:
        raw_reports = []
        float_reports = []
        set_trans_sensing_freqs(static, int_dur, [0] * num_gears)
        set_absTx_sensing_freqs(static, int_dur, [0] * num_gears)
        set_absRx_sensing_freqs(static, int_dur, [0] * num_gears)
        set_static_config(tc, static)
        tc.sendCommand(0xC3, covmat_cmd_arg)
        r = tc.getResponse()
        log('Received response to COMM_CMD_GET_PDNR_COVMAT')
        while True:
            report = tc.getReport()
            raw_reports.append(report)
            if len(raw_reports) >= 3:
                break
        log('Received %d reports\n' % (len(raw_reports)))
        for report in raw_reports:
            converted = list(convert_to_float(report[1][8:-4], 4))
            #log(report)
            log('Report index %d' % (report[1][0]))
            log('%d data entries' % (len(converted)))
            log(converted)
            log('\n')
            float_reports.append(converted)
        float_reports[0] = numpy.array(float_reports[0]).reshape(-1, rx_count)
        float_reports[1] = numpy.array(float_reports[1]).reshape(-1, rx_count)
        float_reports[2] = numpy.array(float_reports[2]).reshape(-1, 20)
        config = {
            'updatePdnrConfigData': False,
            'imageRxes': static['imageRxes'],
            'adnsEnabled': static['adnsEnabled'],
            'ifpConfig.pdnrConfigs[0].basisAmpStdevAbsRx': static['ifpConfig.pdnrConfigs[0].basisAmpStdevAbsRx']
        }
        pdnr = tunePDNR_covMat_v3.pdnrTuningFromCovMats(config, 1, gram_data_frames, tx_count, float_reports[0], float_reports[1], float_reports[2])
        pdnr['basisAmpStdevTransRx'] = [float(s) for s in pdnr['basisAmpStdevTransRx'].split(',')]
        pdnr['basisVectorsTransRx'] = [int(s) for s in pdnr['basisVectorsTransRx'].split(',')]
        pdnr['basisAmpStdevAbsRx'] = [float(s) for s in pdnr['basisAmpStdevAbsRx'].split(',')]
        pdnr['basisVectorsAbsRx'] = [int(s) for s in pdnr['basisVectorsAbsRx'].split(',')]
        pdnr['basisAmpStdevAbsTx'] = [float(s) for s in pdnr['basisAmpStdevAbsTx'].split(',')]
        pdnr['basisVectorsAbsTx'] = [int(s) for s in pdnr['basisVectorsAbsTx'].split(',')]
        pdnr_tuning[-1].append(pdnr)
    log(pdnr_tuning)

def pdnr_sweep(tc, int_durs, num_gears):
    global pdnr_index
    noise_output = [[], [], []]
    tc.reset()
    static = tc.getStaticConfig()
    dynamic = tc.getDynamicConfig()
    dynamic['disableNoiseMitigation'] = 0
    dynamic['inhibitFrequencyShift'] = 1
    dynamic['requestedFrequency'] = 0
    dynamic['requestedFrequencyAbs'] = 0
    set_dynamic_config(tc, dynamic)
    for idx, int_dur in enumerate(int_durs):
        raw_reports = []
        float_reports = []
        set_pdnr(static,
                 pdnr_tuning[pdnr_index][idx]['basisAmpStdevTransRx'],
                 pdnr_tuning[pdnr_index][idx]['basisVectorsTransRx'],
                 pdnr_tuning[pdnr_index][idx]['basisAmpStdevAbsRx'],
                 pdnr_tuning[pdnr_index][idx]['basisVectorsAbsRx'],
                 pdnr_tuning[pdnr_index][idx]['basisAmpStdevAbsTx'],
                 pdnr_tuning[pdnr_index][idx]['basisVectorsAbsTx'])
        set_trans_sensing_freqs(static, int_dur, [0] * num_gears)
        set_absTx_sensing_freqs(static, int_dur, [0] * num_gears)
        set_absRx_sensing_freqs(static, int_dur, [0] * num_gears)
        static['forceFreshReport'] = 1
        set_static_config(tc, static)
        tc.sendCommand(0xC3, covmat_cmd_arg)
        r = tc.getResponse()
        log('Received response to COMM_CMD_GET_PDNR_COVMAT')
        while True:
            report = tc.getReport()
            raw_reports.append(report)
            if len(raw_reports) >= 3:
                break
        log('Received %d reports\n' % (len(raw_reports)))
        noise_output[0].append(next(convert_to_float(raw_reports[0][1][4:8], 4)))
        noise_output[1].append(next(convert_to_float(raw_reports[0][1][4:8], 4)))
        noise_output[2].append(next(convert_to_float(raw_reports[0][1][4:8], 4)))
    pdnr_index += 1
    log(noise_output)
    return noise_output
