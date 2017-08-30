import pymysql
import numpy as np
import json
import sys
import os
import matplotlib
import traceback
from datetime import datetime
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import dates

# Maximum number of records to save
MAXRECORDS = 360

# Datafile and path
PATH = '/home/hass/.homeassistant/'
IMGPATH = '/home/hass/images/'
#PATH = './'
DATAFILE = PATH + 'hassplotdata.json'
CREDFILE = PATH + 'hassdb.json'
LOGFILE  = PATH + 'hass_plots.log'

# Colors
COLORS    = ['#3E9BD8', '#ED5E2F', '#5DA846', '#F4B011']
BACKCOLOR = COLORS
COLORMAP = {'blue': COLORS[0], 'red': COLORS[1], 'green': COLORS[2], 'yellow': COLORS[3]}
ALPHA     = 0.15

# Define dictionaries of sensors, each dictionary will be comined into a single
# waveform in the plot
#
# Temperature Plot waveforms

TEMP_LIVINGROOM = {
    "Living Room Temp": "sensor.living_room_temperature"
}
TEMP_BEDROOM = {
    "Bedroom Temp": "sensor.bedroom_temperature"
}
TEMP_OUTDOORS = {
    "Outdoor Temp": "sensor.pws_temp_f"
}
# Internet Speed waveforms
INTERNET_DOWN = {
    "Download": "sensor.speedtest_download"
}
INTERNET_DOWN_FAST = {
    "Download_fastcom": "sensor.fastcom_download"
}
INTERNET_UPLOAD = {
    "Upload": "sensor.speedtest_upload"
}
HUMIDITY_LIVING_ROOM = {
    "Living Room Dew Point": "sensor.thermo_dew_point"
}
HUMIDITY_OUTDOORS = {
    "Outdoor Dew Point": "sensor.pws_dewpoint_f"
}

# Stuff to track but not plot for now
UNPLOTTED = {
    "PMON1 Current": "sensor.power_mon_current",
    "PMON1 Voltage": "sensor.power_mon_voltage",
    "PMON1 Power": "sensor.power_mon_power",
    "Pressure": "sensor.pws_pressure_mb",
    "Living Room Humidity": "sensor.living_room_humidity",
    "Outdoor Humidity": "sensor.pws_relative_humidity"
}


# Master list of dictionaries to simplify getting data
ALL_LISTS = [
    TEMP_LIVINGROOM,
    TEMP_BEDROOM,
    TEMP_OUTDOORS,
    INTERNET_DOWN,
    INTERNET_DOWN_FAST,
    INTERNET_UPLOAD,
    HUMIDITY_LIVING_ROOM,
    HUMIDITY_OUTDOORS,
    UNPLOTTED
]

class HassLog(object):
    def __init__(self, file):
        self.log_file = file
        self.now = '{:%Y-%b-%d %H:%M:%S}'.format(datetime.now())
        if not os.path.isfile(self.log_file):
            init_text = 'GENERATED ON {}\n'.format(self.now)
            self.log(init_text, type='w')

    def log(self, text, type='a'):
        with open(self.log_file, type) as f:
            if isinstance(text, str):
                f.write('{} {}\n'.format(self.now, text))
            else:
                f.write('{}\n'.format(self.now))
                for line in text:
                    f.write(line)



class HassPlot(object):
    def __init__(self, plot_name, plot_axis, plot_lines, dual_axis=False,
                 line_axis=[], custom_colors=None):
        ''' Basic plot object '''

        ''' Dual axis option added to allow 'un-alike' data on the same plot,
        'un-alike' could mean in units or order of magnitude,
        e.g. Voltage/Current, Upload/Download speeds, etc
        Single Axis Mode:
        plot_name  - Use in file name generation only
        plot_axis  - String for the y-axis label
        plot_lines - List of HassLine objects that are the lines to be plotted
        dual_axis  - Do not pass, or set to false
        line_axis  - Do not pass, or doesn't matter...
        Dual Axis Mode:
        plot_name  - Same as Single Axis Mode
        plot_axis  - You now have 2 y axes. This is a list of strings with
                     y-labels for each axis
        plot_lines - Same as Single Axis Mode
        dual_axis  - Set to True
        line_axis  - List with 0 or 1 entry for each object in plot_lines list.
                     0 means corresponding line to be plotted on top axis
                     1 means corresponding line to be plotted on bottom axis
        '''
        ''' Actually 'dual axis' should probably be another class altogether'''

        self.plot_name = plot_name
        self.plot_axis = plot_axis
        self.plot_lines = plot_lines
        self.dual_axis = dual_axis
        self.line_axis = line_axis

        if custom_colors is None:
            self.colors = COLORS
            self.backcolors = COLORS
        else:
            self.colors = custom_colors
            self.backcolors = custom_colors

        # Components broken into seperate functions so they can be overriden
        # by child classes as necessary
        self.plot_setup()
        self.plot_axes()
        self.plot_draw()
        self.plot_save()

    def plot_setup(self):
        ''' Setup plot styles '''
        plt.style.use('fivethirtyeight')
        font = {'weight': 'normal', 'size': 8}
        matplotlib.rc('font', **font)
        matplotlib.rc('lines', linewidth=4)
        matplotlib.rc({'axes.titlesize': 'medium'})

    def plot_axes(self):
        ''' Generate plot axes '''
        self.fig = plt.figure()

        # Generate axes depending on single or dual axis mode
        # Set labels and invert x-axis of all
        if self.dual_axis:
            self.ax1 = self.fig.add_subplot(211)
            self.ax1.set_ylabel(self.plot_axis[0])
            self.ax1.set_xlabel('Days Ago')

            self.ax2 = self.fig.add_subplot(212, sharex=self.ax1)
            self.ax2.set_ylabel(self.plot_axis[1])
            self.ax2.set_xlabel('Days Ago')
        else:
            self.ax1 = self.fig.add_subplot(111)
            self.ax1.set_ylabel(self.plot_axis)
            self.ax1.set_xlabel('Days Ago')

    def plot_draw(self):
        '''Draw actual plot and legends'''
        # This plot needs inverted x-axis
        self.ax1.invert_xaxis()

        for i, line in enumerate(self.plot_lines):
            # Grab data from HassLine object
            data_avg = line.line_data_avg
            data_min = line.line_data_min
            data_max = line.line_data_max

            # Define time axis
            time = np.linspace(len(data_avg), 1, len(data_avg))

            # Which axis is this going on?
            if self.dual_axis:
                if self.line_axis[i] == 0:
                    ax = self.ax1
                else:
                    ax = self.ax2
            else:
                ax = self.ax1

            # Actually plot line and min/max fill between
            ax.plot(time, data_avg, color=self.colors[i],
                    label=line.line_name)
            ax.fill_between(time, data_min, data_max, alpha=ALPHA,
                            edgecolor=self.backcolors[i],
                            facecolor=self.backcolors[i])

        self.ax1.legend(loc='best')
        if self.dual_axis:
            self.ax2.legend(loc='best')

    def plot_save(self):
        '''Save figure to file'''
        plt.tight_layout()
        plt.savefig(IMGPATH + self.plot_name + '.png')


class HassScatter(HassPlot):
    ''' Scatter Plot '''

    def plot_draw(self):
        '''Draw actual plot and save to file'''
        for i, line in enumerate(self.plot_lines):
            if i == 0:
                # First line is x-axis, grab it and move on to next
                x_data = line.line_data_avg
                self.ax1.set_xlabel(line.line_name)
            else:
                # Assume you already have x axis data, grab y and plot
                y_data = line.line_data_avg

                # X and Y may have different point counts, get the smallest
                points = np.minimum(len(y_data), len(x_data))

                # Actually plot line and min/max fill between
                self.ax1.scatter(x_data[-points:], y_data[-points:],
                                 c=range(points), cmap="jet_r",
                                 label=line.line_name)


class HassScatterKWH(HassPlot):
    ''' Scatter Plot specifically for KWH data '''

    def plot_draw(self):
        '''Draw actual plot and save to file'''
        for i, line in enumerate(self.plot_lines):
            if i == 0:
                # First line is x-axis, grab it and move on to next
                x_data = line.line_data_avg
                self.ax1.set_xlabel(line.line_name)
            else:
                # Assume you already have x axis data, grab y and plot
                y_data = line.line_data_max - line.line_data_min

                # X and Y may have different point counts, get the smallest
                points = np.minimum(len(y_data), len(x_data))

                # Actually plot line and min/max fill between
                self.ax1.scatter(x_data[-points:], y_data[-points:],
                                 c=range(points), cmap="jet_r", label=line.line_name)


class HassLine(object):
    def __init__(self, line_name, line_data):
        self.line_name = line_name
        self.line_data_avg = []
        self.line_data_min = []
        self.line_data_max = []

        self.line_combine(line_data)

    def line_combine(self, line_data):
        ''' Calculate Avg/Min/Max of what may be several sensors worth of data.
        Data may come in of varying lengths, so take care to account for
        this'''
        # Get number of items to average
        num_items = len(line_data)

        # Per item length
        lens = np.array([len(i) for i in line_data])

        # Max length
        len_max = lens.max()

        # Create 'squared up' matrix, but fill with NaN
        # Using NaN and numpy.nan* methods in order to not impact calculations
        # when a data point is missing
        line_data_sq = np.ones((num_items, len_max, 3)) * float('nan')

        # Populate final matrix, assuming if we're missing data, its the oldest
        # data, pad front with NaN. This means this will break if you REMOVE a
        # sensor instead of add one, I'll deal with this when it becomes
        # relevant...
        for i in range(num_items):
            line_data_sq[i, len_max - lens[i]:, :] = line_data[i]

        # Get avg/min/max data sets
        line_data_avg = line_data_sq[:, :, 0]
        line_data_min = line_data_sq[:, :, 1]
        line_data_max = line_data_sq[:, :, 2]

        # Use numpy.nan* to calculate avg/min/max and set class variables
        self.line_data_avg = np.nanmean(line_data_avg, axis=0)
        self.line_data_min = np.nanmin(line_data_min, axis=0)
        self.line_data_max = np.nanmax(line_data_max, axis=0)


class HassData(object):
    def __init__(self, dbname, dbhost, dbuid, dbpass):
        self.datafile = DATAFILE
        self.dbname = dbname
        self.dbhost = dbhost
        self.dbuid = dbuid
        self.dbpass = dbpass
        self.cursor = None
        self.plotdata = {}

    def connect(self):
        '''Method connects to database'''
        conn = pymysql.connect(host=self.dbhost,
                               user=self.dbuid,
                               passwd=self.dbpass,
                               db=self.dbname)
        self.cursor = conn.cursor()
        return self.cursor

    def get_stats_24(self, sensor):
        '''Function to get last 24 hours worth of data for a given sensor and
        return average/min/max'''

        # Get last day's data for sensor
        sql_cmd = ("SELECT state, last_changed "
                   "FROM states "
                   "WHERE entity_id = '" + sensor + "' "
                   "AND state != 'unknown' "
                   "AND last_changed >= NOW() - INTERVAL 1 DAY")
        self.cursor.execute(sql_cmd)
        data = self.cursor.fetchall()

        values = []
        time_stamps = []

        # Convert data to usable format
        for x in data:
            time_stamps.append(dates.date2num(x[1]))
            values.append(float(x[0]))

        # Calculate stats: Trapezoid average, min and max
        value_avg = np.trapz(values, time_stamps) / (time_stamps[-1] -
                                                     time_stamps[0])
        value_min = np.amin(values)
        value_max = np.amax(values)

        return [value_avg, value_min, value_max]

    def read_data(self):
        '''Read in existing datafile if it exists, otherwise create empty
        dictionary'''
        try:
            with open(DATAFILE, 'r') as f:
                self.plotdata = json.load(f)
        except:
            pass

    def write_data(self):
        '''Dump data back to datafile'''
        with open(DATAFILE, 'w') as f:
            json.dump(self.plotdata, f)

    def add_data(self, sensor_list):
        '''Adds/purges data to dictionary'''
        for sensor in sensor_list:
            if sensor in self.plotdata:
                # Pre-existing key, add the data appropriately
                num_records = len(self.plotdata[sensor])

                if num_records < MAXRECORDS:
                    # Less than max records currently stored, add this one
                    self.plotdata[sensor].append(
                        self.get_stats_24(sensor_list[sensor]))
                else:
                    # Otherwise, throw away old points and add this one
                    self.plotdata[sensor] = self.plotdata[sensor][(
                        num_records - MAXRECORDS + 1):] + [self.get_stats_24(
                            sensor_list[sensor])]
            else:
                # New key, add the data
                self.plotdata[sensor] = [self.get_stats_24(
                    sensor_list[sensor])]

    def get_data(self, sensor_list):
        '''Get data (for plotting) of a specific sensor_list'''
        data = []
        for sensor in sensor_list:
            data.append(self.plotdata[sensor])

        return data

def log_traceback(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
    LOGGER.log(tb_lines)

def main():
    just_plot = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'just_plot':
            just_plot = True
            LOGGER.log('just plotting')

    # Get credentials
    with open(CREDFILE) as json_data:
        d = json.load(json_data)

    h = HassData(d['dbname'], d['dbhost'], d['dbuid'], d['dbpass'])

    # Connect
    if not just_plot:
        LOGGER.log('Connecting...')
        h.connect()
    # Read any old data from JSON file
    h.read_data()
    # Grab and append new data from database
    if not just_plot:
        for each_dict in ALL_LISTS:
            h.add_data(each_dict)
        # Write full data back to JSON file
        h.write_data()

    # Create Plot Objects and draw final figures
    LOGGER.log('Plotting...')
    HassPlot(plot_name='Climate',
             plot_axis='Temp [F]',
             plot_lines=[
                 HassLine('Living Room', h.get_data(TEMP_LIVINGROOM)),
                 HassLine('Outdoors', h.get_data(TEMP_OUTDOORS)),
                 HassLine('Bedroom', h.get_data(TEMP_BEDROOM)),
                 HassLine('Living Room', h.get_data(HUMIDITY_LIVING_ROOM)),
                 HassLine('Outdoors', h.get_data(HUMIDITY_OUTDOORS))
             ],
             dual_axis=True,
             line_axis=[0, 0, 0, 1, 1],
             custom_colors=[COLORMAP['blue'], COLORMAP['red'], COLORMAP['green'], COLORMAP['blue'], COLORMAP['red']])

    HassPlot(plot_name='Internet',
             plot_axis=['Speed [Mb/s]', 'Speed [Mb/s]'],
             plot_lines=[
                 HassLine('Download (Speedtest)', h.get_data(INTERNET_DOWN)),
                 HassLine('Download (Fast.com)', h.get_data(INTERNET_DOWN_FAST)),
                 HassLine('Upload', h.get_data(INTERNET_UPLOAD))
             ],
             dual_axis=True,
             line_axis=[0, 0, 1],
             custom_colors=[COLORMAP['blue'], COLORMAP['green'], COLORMAP['red']])

    # HassPlot(plot_name='Humidity',
             # plot_axis='RH [%]',
             # plot_lines=[
                 # HassLine('Living Room', h.get_data(HUMIDITY_LIVING_ROOM)),
                 # HassLine('Outdoors', h.get_data(HUMIDITY_OUTDOORS))
             # ])

    LOGGER.log('Complete!')

if __name__ == '__main__':
    LOGGER = HassLog(LOGFILE)
    try:
        main()
    except Exception as e:
        log_traceback(e)
        print(e)
