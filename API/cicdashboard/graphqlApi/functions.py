""" HELPER FUNCTIONS
This script contains helper functions for the main dashbaord solution.
"""

# common imports
import graphene
import calendar
import collections
from . import models
from django.conf import settings
from django.core.cache import cache
from collections import Counter,OrderedDict
from datetime import datetime,date,timedelta
from graphene.types.generic import GenericScalar
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db.models.functions import TruncMonth, Coalesce, TruncDay
from django.db.models import Count, Sum, F, Case, When, Value, CharField

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


""" FILTER VARIABLES
The variables below define some of the common filter values used.
"""

token_list = ['Sarafu']
gender_list = ["Male", "Female", "Other", "Unknown"]
transfer_subtypes = ['STANDARD', 'AGENT_OUT', 'DISBURSEMENT', 'RECLAMATION','UNKNOWN']
spend_type_list = ['Education', 'Environment', 'Farming/Labour', 'Food/Water', 'Fuel/Energy', 'Health', 'Other', 'Savings Group', 'System', 'Shop', 'Transport', 'Unknown']

def create_filter_items(gender, spend_type, token_name, tx_type):
	gender_filter = gender_list if len(gender) == 0 else gender
	spend_filter = spend_type_list if len(spend_type) == 0 else spend_type
	token_name_filter = token_list if len(token_name) == 0 else token_name
	tx_type_filter = transfer_subtypes if len(tx_type) == 0 else tx_type

	return(gender_filter, spend_filter, token_name_filter, tx_type_filter)

""" CACHE
function to get and return cache data
"""

def get_cache_values(key, query):
	cache_key = key
	cache_key.update({"Query":query})
	result = cache.get(cache_key)
	return(cache_key, result)
	
""" DATE FILTER
The function below helps to set the date ranges for the selected time period requests received from the front end.
"""
# takes in from data and to date passed from request and converts it to relevant time information
def create_date_range(from_date, to_date):
	# convert string into date information
	if from_date == to_date: # single month selection
		_from_date = datetime.strptime("{}-01".format(from_date), '%Y-%m-%d')
		start_period_first = _from_date
		start_period_last = _from_date + timedelta(1)

		today = date.today()
		if today.year == _from_date.year and today.month == _from_date.month: # check if selection is current month selection
			end_period_first = datetime.combine(today, datetime.min.time())
			end_period_last = end_period_first + timedelta(1)
		else:
			_to_date = datetime.strptime("{}-01".format(to_date), '%Y-%m-%d')
			end_period_first = _to_date + timedelta(calendar.monthrange(_to_date.year, _to_date.month)[1] - 1)
			end_period_last = end_period_first + timedelta(1)	

	else:
		_from_date = datetime.strptime("{}-01".format(from_date), '%Y-%m-%d')
		_to_date = datetime.strptime("{}-01".format(to_date), '%Y-%m-%d')

		start_period_first = _from_date
		end_period_first = _to_date
		start_period_last = start_period_first + timedelta(calendar.monthrange(start_period_first.year, start_period_first.month)[1])
		end_period_last = end_period_first + timedelta(calendar.monthrange(end_period_first.year, end_period_first.month)[1])

	return (start_period_first, start_period_last, end_period_first, end_period_last)

""" CATEGORY BY FILTER
Handles cases where categories are not retunred by the query, by adding in the categories and making thier value 0.
This is crucial for the charts to work properly in the frontend.
"""

def category_by_filter(data, duration_list, time_name, time_type, time_format, category, filter_list):
	filter_list = sorted(filter_list)
	result =[]

	for time_item in duration_list: # duration list, is the list of periods e.g. list of days
		temp_dict = {time_name:time_item}

		# check if values exist for given time e.g a single day and add to list
		filtered_results = [result for result in data if result[time_type].strftime(time_format) == time_item]
		for item in filter_list: 
			# if category exists in time frame, add it, else make category 0
			x = [temp_dict.update({e[category]:e['value']}) for e in filtered_results if e[category] == item]
			if len(x) == 0: temp_dict.update({item:0})
		result.append(temp_dict)
	
	return(result)