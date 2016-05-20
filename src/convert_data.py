"""
============
Convert data
============

A module that provides functions to read a .csv file and convert the 
contained information into convenient formats that can be used for feature
extraction.
"""

import csv
import datetime

import numpy as np
import holidays


# Maps the date categories onto integer codes
label_mapping = {
	'S-B - intern (901106)' : 0,
	'ISO Zertifizierung smO (2990191)' : 1,
	'ISO Zertifizierung SWO Netz (2910667)' : 2,
	'E - intern (901107)' : 3,
	'E - MPM (2900041)' : 4,
	'E - smartTT' : 5,
	'S-B - smartTT2.0 (901106)' : 6,
	'Noch nicht zugeordnet' : 7
	}

# holidays_2015 = [
# 	datetime.date(year=2015, month=1, day=1),  # Neujahrstag
# 	datetime.date(year=2015, month=4, day=3),  # Karfreitag
# 	datetime.date(year=2015, month=4, day=6),  # Ostermontag
# 	datetime.date(year=2015, month=5, day=1),  # 1. Mai/ Tag der Arbeit
# 	datetime.date(year=2015, month=5, day=14),  # Christi Himmelfahrt
# 	datetime.date(year=2015, month=5, day=25),  # Pfingstmontag
# 	datetime.date(year=2015, month=10, day=3),  # Tag der deutschen Einheit
# 	datetime.date(year=2015, month=12, day=25),  # 1. Weihnachtsfeiertag
# 	datetime.date(year=2015, month=12, day=26)  # 2. Weihnachtsfeiertag
# 	]
# holidays_2016 = [
# 	datetime.date(year=2016, month=1, day=1),  # Neujahrstag
# 	datetime.date(year=2016, month=3, day=25),  # Karfreitag
# 	datetime.date(year=2016, month=3, day=28),  # Ostermontag
# 	datetime.date(year=2016, month=5, day=1),  # 1. Mai/ Tag der Arbeit
# 	datetime.date(year=2016, month=5, day=5),  # Christi Himmelfahrt
# 	datetime.date(year=2016, month=5, day=16),  # Pfingstmontag
# 	datetime.date(year=2016, month=10, day=3),  # Tag der deutschen Einheit
# 	datetime.date(year=2016, month=12, day=25),  # 1. Weihnachtsfeiertag
# 	datetime.date(year=2016, month=12, day=26)  # 2. Weihnachtsfeiertag
# 	]
# holidays_2017 = [
# 	datetime.date(year=2017, month=1, day=1),  # Neujahrstag
# 	datetime.date(year=2017, month=4, day=24),  # Karfreitag
# 	datetime.date(year=2017, month=4, day=17),  # Ostermontag
# 	datetime.date(year=2017, month=5, day=1),  # 1. Mai/ Tag der Arbeit
# 	datetime.date(year=2017, month=5, day=25),  # Christi Himmelfahrt
# 	datetime.date(year=2017, month=6, day=5),  # Pfingstmontag
# 	datetime.date(year=2017, month=10, day=3),  # Tag der deutschen Einheit
# 	datetime.date(year=2017, month=10, day=31),  # Reformationstag
# 	datetime.date(year=2017, month=12, day=25),  # 1. Weihnachtsfeiertag
# 	datetime.date(year=2017, month=12, day=26)  # 2. Weihnachtsfeiertag
# 	]


def get_features(filename):
	return extract_features(convert_data(load_data(filename)))

def load_data(filename):
	"""Loads each row of a .csvfile and puts them into a list.

	The output is a list containing rows of the input file as list 
	entries. Each entry is itself another list containing all the column
	entries of the file.

	Args:
		filename: The input file name as a string. Needs to be a .csv.

	Returns:
		A list containing the rows of the file.

	"""
	raw_data = []
	with open('../res/'+filename+'.csv', newline='') as f:
		data_reader = csv.reader(f, delimiter=';')
		for row in data_reader:
			raw_data.append(row)
		del raw_data[0]
	return raw_data

def convert_data(raw_data):
	"""Converts the data read from a file into a convenient format.

	Calls the 'load_data' function in order to retrieve information from
	the given input .csv file. This data is then converted into a format
	that can be used later.
	The exact starting point is converted into a 'datetime.datetime' object.  
    The end time is also are converted into 'datetime.datetime' object.
	The string labels are converted into a coding scheme of integers defined
	at the top of the module.

	Args:
		filename: The input file name as a string. Needs to be a .csv.

	Returns:
		A list of which entries are lists containing the data in convenient formats.
		This list can be used by 'extract_features' in order to retrieve a numeric 
		array.
	"""
	data = []
	for i in range(len(raw_data)):
		data_i = []
		# Convert begin. i.e. date+starttime
		data_i.append(convert_datetime(raw_data[i][0], raw_data[i][1]))

		# Convert end. i.e. date+endtime
		data_i.append(convert_datetime(raw_data[i][0], raw_data[i][2]))

		# Convert label
		data_i.append(convert_label(raw_data[i][3]))
		
		# Appends the complete date to the list
		data.append(data_i)		

	return data


# Feature extraction

def extract_features(data):
	"""Creates a feature matrix out of the raw data.

	Takes the formatted data out of the 'convert_data' function and
	extracts 10 numerical features out of it.

	Args:
		data: A formatted list of input data generated by 'convert_data'.

	Returns:
		A numpy array of dimension (len(data), 12) containing numeric 
		features.

		The 1st column holds the ordinal of each date (The count from 
		2015-01-01) and hence, the absolute time.
		The 2nd column holds the year of the date.
		The 3rd column holds the month of the date.
		The 4th column holds the day of the year.
		The 5th column holds the day of the month.
		The 6th column holds the day of the week, where 0 is Monday and
		6 is Sunday.
		The 7th column holds whether the day is on weekend (1) or not (0).
		The 8th column holds the week of the year.
		The 9th column holds the week of the month.
		The 10th column holds whether the date is a holiday(1) or not (0).
	"""
	time_range = 8
	num_features_per_date = 12
	
	features = np.zeros((len(data), num_features_per_date*time_range))
	initial_date = datetime.date(2015, 1, 1)
	holiday_dates = holidays.Germany(state='NI', years=[2015, 2016, 2017, 2018, 2019, 2020])

	for i, sample in enumerate(data):

		## Features concerning the date
		
		date = data[i][0].date
		for time_offset in range(time_range):
			day = date + datetime.timedelta(days=time_offset-time_range/2)
			offset = time_offset*num_features_per_date

			# Ordinal of day
			features[i,0+offset] = day.toordinal() - initial_date.toordinal()
			# Year
			features[i,1+offset] = day.year
			# Month of year
			features[i,2+offset] = day.month
			# Day of year
			features[i,3+offset] = day.toordinal() \
				- datetime.date(day.year, 1, 1).toordinal() + 1
			# Day of month
			features[i,4+offset] = day.day
			# Weekday
			features[i,5+offset] = day.weekday()
			# Weekend 1 / week 0
			features[i,6+offset] = features[i,5+offset] == 5 or \
				features[i,5+offset] == 6
			# Week of year # TODO: Kalenderwoche
			features[i,7+offset] = np.floor(features[i,3] / 7)
			# Week of month
			features[i,8+offset] = np.floor(features[i,4] / 7)
			# Holiday
			features[i,9+offset] = day in holiday_dates
			# Specific holidays
			try:
				holiday = holiday_dates[day]
				# Christmas
				if holiday == 'Erster Weihnachtstag' or \
					holiday == 'Zweiter Weihnachtstag':
					features[i,10+offset] = 1
				# Easter
				elif holiday == 'Ostermontag':
					features[i,11+offset] = 1
			except KeyError:
				features[i,10+offset] = 0
				features[i,11+offset] = 0

			# TODO: Brückentag

		

		

		## Features concerning the time
		
		default_names = ['Ordinal', 'Year', 'Month', 'Day of Year', 'Day of Month',
			'Weekday', 'Weekend', 'Week of year', 'Week of month', 'Holiday',
			'Christmas', 'Easter']
		names = []
		for i in range(time_range):
			for name in default_names:
				names.append(name+' of day {}'.format(i-4))

	return features, names


# Conversion helpers

def convert_datetime(date_str, time_str):
	date_list = [int(x) for x in date_str.split(sep='.')]
	time_list = [int(x) for x in time_str.split(sep=':')]
	return datetime.datetime(date_list[2], date_list[1], date_list[0], time_list[0], time_list[1], time_list[2])


def convert_label(label_str):
	labels = label_str.split(sep=',')
	return [label_mapping[label] for label in labels]

