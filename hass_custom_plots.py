'''
Name: hass_custom_plots.py
Author: Kevin Fronczak
Date: April 23, 2017 
Desc: This script is run as a cronjob and grabs the 24hr avg, min, max
datapoints for a given sensor.  The datapoint is saved to a json file
and a new image created that can be displayed by the frontend via
the local file camera platform.
'''

import os
import pymysql
import json
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import figure
from matplotlib import dates

NDAYS = 1
PATH = '/home/hass/.homeassistant/'
CREDFILE = PATH + 'hassdb.json'
DATAFILE = PATH + 'hassplotdata.json'
PLOTPATH = '/home/hass/images/'

''' List of sensor and names to use in plot '''
# Note: each list is represetnative of a single plot
TEMPERATURES = ['sensor.living_room_temperature',
                'sensor.pws_temp_f']

INTERNET = ['sensor.speedtest_download']

ENTITIES = {'Temperature': TEMPERATURES,
            'Internet': INTERNET}

MIN_MAX_PLOTS = ['sensor.living_room_temperature', 'sensor.speedtest_download']

def main():
    ''' Get credentials '''
    with open(CREDFILE) as json_data:
        d = json.load(json_data)
    
    hass = HassPlotting(d['dbname'], d['dbhost'], d['dbuid'], d['dbpass'])
    
    hass.connect()
    mydata = {}
    for plotname, sensortype in ENTITIES.items():
        mydata[plotname] = {}
        result = hass.get_data(ENTITIES[plotname])
        for key, value in result[1].items():
            mydata[plotname][key] = {str(result[0]): result[1][key]}
    data = hass.save_data(mydata)
    for sensor_type in data:
        hass.plot_data(sensor_type, data[sensor_type])


class HassPlotting(object):
    def __init__(self, dbname, dbhost, dbuid, dbpass):
        self.datafile = DATAFILE
        self.dbname = dbname
        self.dbhost = dbhost
        self.dbuid = dbuid
        self.dbpass = dbpass
        self.cursor = None

    def connect(self):
        '''Method connects to database'''
        conn = pymysql.connect(host=self.dbhost,
                               user=self.dbuid,
                               passwd=self.dbpass,
                               db=self.dbname)
        self.cursor = conn.cursor()
        return self.cursor

    def get_data(self, sensors):
        '''Get data for list of sensors'''
        value_array = {}
        for entity in sensors:
            self.cursor.execute("SELECT state, last_changed FROM states WHERE entity_id = '"+entity+"' AND state != 'unknown'")
            value_array[entity]     = []
            now = datetime.datetime.now() - datetime.timedelta(days=NDAYS)
            current_time = dates.date2num(now)-NDAYS
            now_string = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
            value_sum = 0
            value_min = 8191
            value_max = -8191
            count = 0;
            for x in self.cursor.fetchall():
                current_value = float(x[0])
                stored_time = dates.date2num(x[1])
                if stored_time >= current_time - 1:
                    if current_value > value_max:
                        value_max = current_value
                    elif current_value < value_min:
                        value_min = current_value
                    value_sum += current_value
                    count += 1
            value_sum = value_sum / count
            value_array[entity] = [value_sum, value_min, value_max, now_string]
        return [current_time, value_array]
    
    def save_data(self, data):
        '''Save new data to json file'''
        new_data = {}
        if os.path.isfile(DATAFILE):
            with open(DATAFILE) as dfile:
                old_data = json.load(dfile)
            for sensor_type in data:
                new_data[sensor_type] = {}
                for sensor in data[sensor_type]:
                    new_data[sensor_type][sensor] = self.merge_dicts(data[sensor_type][sensor], old_data[sensor_type][sensor])
        else:
            new_data = data

        with open(DATAFILE, 'w') as outfile:
            json.dump(new_data, outfile)
        return new_data
        
    def plot_data(self, figname, data_dict):
        font = {'weight' : 'normal', 'size' : 6}
        matplotlib.rc('font', **font)
        matplotlib.rc('lines', linewidth=4)
        matplotlib.rc({'axes.titlesize' : 'medium'})
        plt.style.use('fivethirtyeight')
        fig = plt.figure()
        plt.hold(True)
        plt.grid(b = 'on')
        # Get the data to plot, first
        for sensor in data_dict:
            xvals = []
            yavg = []
            ymin = []
            ymax = []
            xarray = []
            for x in sorted(data_dict[sensor]):
                y = data_dict[sensor][x]
                xvals.append(y[3])
                yavg.append(y[0])
                ymin.append(y[1])
                ymax.append(y[2])
                xarray.append(float(x))
            plt.xticks(xarray, xvals)

            if sensor in MIN_MAX_PLOTS:
                plt.fill_between(x=xarray, y1=ymin, y2=ymax, facecolor='seagreen',interpolate=False, alpha=0.3)
                plt.plot(xarray, yavg, label=sensor)
            else:
                plt.plot(xarray, yavg, label=sensor)
           
        plt.legend(loc="lower left", fancybox=True, framealpha=0.4)
        plt.title(figname)
        plt.xlabel('Time')
        plt.locator_params(axis='y', nticks=5)
        plt.locator_params(axis='y', nticks=5)
        plt.savefig(PLOTPATH + figname + '.png')
    
    def merge_dicts(self, x, y):
        '''Given two dicts, merge them'''
        z = x.copy()
        z.update(y)
        return z

if __name__ == '__main__':
    main()