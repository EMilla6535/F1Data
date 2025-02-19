import os
import time
import datetime
from datetime import datetime
import numpy as np
from app.utils.utils import loadDataFromDisk


def fixLapStartEnd(laps_data):
    # Fix: Case when the first lap_start|lap_end pair is a single None lap.
    # if laps_data[0]['is_pit_out_lap'] == True and laps_data[1]['is_pit_out_lap'] == True:
    #     laps_data = laps_data[1:]
    if laps_data[0]['is_pit_out_lap'] == True and laps_data[1]['is_pit_out_lap'] == True:
        laps_data = laps_data[1:]
    fixed_laps = {'lap_start': [], 'lap_end': []}
    for lap_n in range(len(laps_data)):
        if laps_data[lap_n]['is_pit_out_lap'] or lap_n == 0:
            fixed_laps['lap_start'].append(lap_n)
            if lap_n != 0:
                fixed_laps['lap_end'].append(lap_n)
    fixed_laps['lap_end'].append(len(laps_data) + 1)
    return fixed_laps

def checkTimeDelta(start, final, duration):
    delta_time = (datetime.fromisoformat(final) - datetime.fromisoformat(start)).total_seconds()
    return delta_time <= duration and delta_time >= 0

def pointDistance(xi, xf, yi, yf):
    return np.sqrt((xf - xi)**2 + (yf - yi)**2)

def getTotalDistance(x, y):
    result = 0.0
    for i in range(len(x) - 1):
        result += pointDistance(x[i], x[i + 1], y[i], y[i + 1])
    return result

def getDataVector(x_data, y_data, x_init, y_init):
    return [x_data - x_init, y_data - y_init]

def getLocationsInLap(locations, x_start, y_start, aux_vector):
    locations = locations[0]
    result = []
    for i in range(len(locations)):
        #print(len(locations[0]))
        x_value = locations[i]['x']
        y_value = locations[i]['y']
        data_vector = getDataVector(x_value, y_value, x_start, y_start)
        dot_result = np.dot(aux_vector, data_vector)
        if i < int(len(locations) * 0.1):
            if dot_result >= 0:
                result.append(locations[i])
        elif i > int(len(locations) * 0.9):
            if dot_result < 0:
                result.append(locations[i])
        else:
            result.append(locations[i])
    return result

def getNormalizedTelemetry(locations, telemetry, x_start, y_start, track_len):
    total_dist = np.sum([pointDistance(locations[i]['x'], locations[i+1]['x'], locations[i]['y'], locations[i+1]['y'])
                         for i in range(len(locations) - 1)])

    total_dist += pointDistance(x_start, locations[0]['x'], y_start, locations[0]['y'])
    total_dist += pointDistance(locations[-1]['x'], x_start, locations[-1]['y'], y_start)

    offset = pointDistance(x_start, locations[0]['x'], y_start, locations[0]['y']) / track_len

    lap_perc = total_dist / track_len

    init_date = datetime.fromisoformat(locations[0]['date'])
    last_date = datetime.fromisoformat(locations[-1]['date'])

    total_lap_time = (last_date - init_date).total_seconds()

    result = {'x_tel': [], 'y_tel': []}
    for i in range(len(telemetry)):
        tel_date = datetime.fromisoformat(telemetry[i]['date'])
        if tel_date >= init_date and tel_date <= last_date:
            result['x_tel'].append((((tel_date - init_date).total_seconds() / total_lap_time) * lap_perc) + offset)
            result['y_tel'].append(telemetry[i])
    return result

class Driver:
    def __init__(self, driver_fname, filepath, race_format='standard'):
        self.dfn = driver_fname
        self.filepath = filepath
        
        formats = {'standard': ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Race'], 
                   'sprint': ['Practice 1', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race']}
        if race_format == 'standard' or race_format == 'sprint':
            self.sessions = formats[race_format]
        else:
            self.sessions = formats['standard']
        
    def openDataFile(self, file_type, session_name):
        driver_file = f"Driver_{self.dfn}/Driver_{self.dfn}_{session_name}_{file_type}.json"
        data = loadDataFromDisk(self.filepath + '/' + driver_file)
        #data = loadDataFromDisk(self.filepath + driver_file)
        return data
    
    def getLapsBySessions(self):
        result = {}
        for sn in self.sessions:
            try:
                temp_l = self.openDataFile('laps', sn)
                result[sn] = [item['lap_duration'] for item in temp_l if item['lap_duration'] is not None]
            except FileNotFoundError:
                print("File not found at getLapsBySessions()")
                result[sn] = []
        return result
    
    def getLapsByStints(self):
        result = {}
        for sn in self.sessions:
            try:
                temp_l = self.openDataFile('laps', sn)
                temp_s = self.openDataFile('stints', sn)
                fixed_laps = fixLapStartEnd(temp_l)
                relevant_data = {'lap_duration': [item['lap_duration'] for item in temp_l],
                                 'lap_start': fixed_laps['lap_start'],
                                 'lap_end': fixed_laps['lap_end'], 
                                 'compound': [item['compound'] for item in temp_s]}
                stint_data = []
                for i in range(len(relevant_data['lap_start'])):
                    temp_buffer = relevant_data['lap_duration'][relevant_data['lap_start'][i]:relevant_data['lap_end'][i]]
                    temp_buffer = [item for item in temp_buffer if item is not None]
                    stint_data.append({'compound': relevant_data['compound'][i], 'lap_times': temp_buffer})
                if len(stint_data) > 0:
                    result[sn] = stint_data
            except FileNotFoundError:
                print("File not found at getLapsByStints()")
                #result[sn] = []
        return result
    
    def getLapsByCompounds(self):
        result = {}
        for sn in self.sessions:
            try:
                temp_l = self.openDataFile('laps', sn)
                temp_s = self.openDataFile('stints', sn)
                fixed_laps = fixLapStartEnd(temp_l)
                relevant_data = {'compound': [item['compound'] for item in temp_s],
                                 'lap_duration': [item['lap_duration'] for item in temp_l],
                                 'lap_start': fixed_laps['lap_start'],
                                 'lap_end': fixed_laps['lap_end']}
                comp_data = {item: [] for item in list(set(relevant_data['compound']))}
                for comp in list(set(relevant_data['compound'])):
                    laps_data = [{'lap_start': relevant_data['lap_start'][_], 'lap_end': relevant_data['lap_end'][_]} 
                                  for _ in range(len(relevant_data['compound'])) 
                                  if relevant_data['compound'][_] == comp]
                    stint_data = []
                    for i in range(len(laps_data)):
                        buffer = [item for item in relevant_data['lap_duration'][laps_data[i]['lap_start']:laps_data[i]['lap_end']]]
                        buffer = [item for item in buffer if item is not None]
                        stint_data.append(buffer)
                    comp_data[comp] = stint_data
                result[sn] = comp_data
            except FileNotFoundError:
                print("File not found at getLapsByCompounds()")
                result[sn] = []
        return result
    
    # getFastestLap(session)
    def getFastestLap(self):
        # collect all lap_duration and lap_number from every session
        session_laps = {}
        for sn in self.sessions:
            try:
                temp_l = self.openDataFile('laps', sn)
                session_laps[sn] = [{'lap_duration': item['lap_duration'], 'date_start': item['date_start']} 
                                  for item in temp_l if item['lap_duration'] is not None]
            except FileNotFoundError:
                print("File not found at getFastestLap()")
                session_laps[sn] = []
        
        # find the minimum lap_duration and save session_name and lap_number
        fl = {'lap_duration': 50000, 'date_start': '', 'session': '', 'car_telemetry': [], 'car_location': []}
        for k, v in session_laps.items():
            if len(v) > 0:
                for item in v:
                    if item['lap_duration'] <= fl['lap_duration']:
                        fl['lap_duration'] = item['lap_duration']
                        fl['date_start'] = item['date_start']
                        fl['session'] = k
        
        # load car telemetry and car location of the session
        if fl['date_start'] != '':
            car_tel = self.openDataFile('car_data', fl['session'])
            car_loc = self.openDataFile('location', fl['session'])
            fl['car_telemetry'] = [item for item in car_tel if checkTimeDelta(fl['date_start'], item['date'], fl['lap_duration'])]
            fl['car_location'] = [item for item in car_loc if checkTimeDelta(fl['date_start'], item['date'], fl['lap_duration'])]
        
        # return {'lap_duration', 'date_start', 'session', 'car_telemetry', 'car_location'}
        return fl
    
    

class DriverLocTel(Driver):
    def __init__(self, driver_fname, filepath, start_point, start_angle, track_len, race_format='standard'):
        self.dfn = driver_fname
        self.filepath = filepath
        self.x_start, self.y_start = start_point
        self.start_angle = start_angle
        self.dir_vector = [np.cos(start_angle), np.sin(start_angle)]
        self.track_len = track_len
        formats = {'standard': ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Race'], 
                   'sprint': ['Practice 1', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race']}
        if race_format == 'standard' or race_format == 'sprint':
            self.sessions = formats[race_format]
        else:
            self.sessions = formats['standard']
    
    # getCarTelemetry(session, lap[s])
    def getCarTelemetry(self, session, laps):
        # collect lap information based in sessions and laps
        # Note about laps: it represents the index starting
        # from 0 of all non None lap_duration laps
        try:
            temp_l = self.openDataFile('laps', session)
            temp_laps = [{'lap_duration': item['lap_duration'], 'date_start': item['date_start']} 
                          for item in temp_l if item['lap_duration'] is not None]
            result = []
            for i in laps:
                if i >= 0 and i < len(temp_laps):
                    result.append(temp_laps[i])
            # load car telemetry
            car_tel = self.openDataFile('car_data', session)
            tel_data = []
            if len(result) > 0:
                for i in range(len(result)):
                    tel_data.append([item for item in car_tel if checkTimeDelta(result[i]['date_start'], item['date'], result[i]['lap_duration'])])
        except FileNotFoundError:
            print("File not found at getCarTelemetry()")
            tel_data = []
        
        return tel_data

    def getCarTelemetryByLap(self, laps):
        # collect lap information based in laps indexes
        next_len = 0
        prev_len = 0
        tel_data = []
        for session in self.sessions:
            try:
                temp_l = self.openDataFile('laps', session)
                temp_laps = [{'lap_duration': item['lap_duration'], 'date_start': item['date_start']}
                              for item in temp_l if item['lap_duration'] is not None]
                next_len = len(temp_laps)
                result = []
                for i in laps:
                    if i >= prev_len and i < next_len:
                        result.append(temp_laps[i])
                
                car_tel = self.openDataFile('car_data', session)
                if len(result) > 0:
                    for i in range(len(result)):
                        tel_data.append([item for item in car_tel if checkTimeDelta(result[i]['date_start'], item['date'], result[i]['lap_duration'])])
                prev_len = next_len

            except FileNotFoundError:
                print("File not found at getCarTelemetryByLap()")
        
        return tel_data
    
    # getCarLocation(session, lap[s])
    def getCarLocation(self, session, laps):
        # collect lap information based in sessions and laps
        # Note about laps: it represents the index starting
        # from 0 of all non None lap_duration laps
        try:
            temp_l = self.openDataFile('laps', session)
            temp_laps = [{'lap_duration': item['lap_duration'], 'date_start': item['date_start']} 
                          for item in temp_l if item['lap_duration'] is not None]
            result = []
            for i in laps:
                if i >= 0 and i < len(temp_laps):
                    result.append(temp_laps[i])
            # load car telemetry
            car_loc = self.openDataFile('location', session)
            loc_data = []
            if len(result) > 0:
                for i in range(len(result)):
                    loc_data.append([item for item in car_loc if checkTimeDelta(result[i]['date_start'], item['date'], result[i]['lap_duration'])])
            loc_data = [getLocationsInLap(loc_data, self.x_start, self.y_start, self.dir_vector)]
        except FileNotFoundError:
            print("File not found at getCarLocation()")
            loc_data = []
        
        return loc_data