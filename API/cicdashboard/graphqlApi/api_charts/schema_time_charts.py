""" SCHEMA SCRIPT
This script is responsible for handling time based chart requests.
it makes use of functions defined in the functions script (located in parent folder > graphqlAPI)
where possible repetitive steps have been transformed into a function for simplicity.
"""

from .types import *
from .. functions import *

FQ_TRADER_THRESHOLD = 4
cic_users = models.CicUsers
reporting_table = models.CicReportingTable

class Query(graphene.ObjectType):
	
	monthlySummaryData = graphene.List(time_summary,
		from_date = graphene.String(required=True), 
		to_date = graphene.String(required=True),
		token_name= graphene.List(graphene.String,required=True),
		spend_type =graphene.List(graphene.String,required=True),
		gender =graphene.List(graphene.String,required=True), 
		tx_type =graphene.List(graphene.String,required=True),
		request = graphene.String(required=True))

	def resolve_monthlySummaryData(self, info, **kwargs):
		
		if CACHE_ENABLED:
			cache_key = kwargs
			cache_key.update({"Query":"monthlySummaryData"})
			response = cache.get(cache_key)

			if response is not None:
				return(response)

		# get filter criteria passed from front-end / user request
		from_date, to_date, token_name, spend_type, gender, tx_type, request = kwargs['from_date'], kwargs['to_date'], kwargs['token_name'], kwargs['spend_type'], kwargs['gender'], kwargs['tx_type'], kwargs['request']

		# get relevant start and end points for date selection
		start_period_first, start_period_last, end_period_first, end_period_last, flag = create_date_range(from_date, to_date)
		print(start_period_first, start_period_last, end_period_first, end_period_last, flag)

		# check if filters have been passed through, if not use all values
		gender_filter, spend_filter, token_name_filter, tx_type_filter = create_filter_items(gender, spend_type, token_name, tx_type)

		# request type for specific chart
		request = request.lower()

		#if from_date == to_date: # daily selection
		if flag == 'd':
			print("daily view selecetd")
			summary_data = reporting_table.objects.annotate(_day =TruncDay('timestamp'))\
			.filter(timestamp__gte = start_period_first, timestamp__lt = end_period_last, tokenname__in = token_name_filter, t_business_type__in = spend_filter, s_gender__in = gender_filter,transfer_subtype__in = tx_type_filter)\
			.order_by("_day")

			duration_type = '_day'
			duration_format = '%Y-%m-%d'
			duration_name = 'dayMonth'

		else: # monthly selection
			print("monthly view selecetd")
			summary_data = reporting_table.objects.annotate(_month=TruncMonth('timestamp'))\
			.filter(timestamp__gte = start_period_first, timestamp__lt = end_period_last, tokenname__in = token_name_filter, t_business_type__in = spend_filter, s_gender__in = gender_filter,transfer_subtype__in = tx_type_filter)\
			.order_by("_month")
			
			duration_type = '_month'
			duration_format = '%Y-%m'
			duration_name = 'yearMonth'


		if request == 'tradevolumes-time-spendtype':
			response = get_common_response_data(time_summary, summary_data, duration_type, 't_business_type',Sum('weight'), duration_format, duration_name, spend_filter, start_period_first, end_period_last)

		if request == 'transactioncount-time-spendtype':
			response = get_common_response_data(time_summary, summary_data, duration_type, 't_business_type',Count("id"), duration_format, duration_name, spend_filter, start_period_first, end_period_last)

		if request == 'tradevolumes-time-gender':
			response = get_common_response_data(time_summary, summary_data, duration_type, 's_gender',Sum("weight"), duration_format, duration_name, gender_filter, start_period_first, end_period_last)

		if request == 'transactioncount-time-gender':
			response = get_common_response_data(time_summary, summary_data, duration_type, 's_gender',Count("id"), duration_format, duration_name, gender_filter, start_period_first, end_period_last)

		if request == 'tradevolumes-time-txsubtype':
			response = get_common_response_data(time_summary, summary_data, duration_type, 'transfer_subtype',Sum("weight"), duration_format, duration_name, tx_type_filter, start_period_first, end_period_last)

		if request == 'transactioncount-time-txsubtype':
			response = get_common_response_data(time_summary, summary_data, duration_type, 'transfer_subtype',Count("id"), duration_format, duration_name, tx_type_filter, start_period_first, end_period_last)

		if request == 'users-time-totalvsfrequent' or request == 'registeredusers-cumulative':
			response = []

			# calculate traders
			traders_dict = {}
			traders = summary_data.values(duration_type).annotate(trader_count = Count('source', distinct=True)).order_by(duration_type)
			trader_update = [traders_dict.update({x[duration_type].strftime(duration_format):x["trader_count"]}) for x in traders]

			if duration_name == 'yearMonth':
				month_list = summary_data.values_list("_month", flat=True).distinct()

				# calculate frequent traders
				## get the list of frequent traders by month and source
				fq_dict = {}
				fq_traders = summary_data.values('_month','source').annotate(value = Count("id", distinct=True)).filter(value__gte = FQ_TRADER_THRESHOLD).order_by("-value").order_by("_month")
				
				for fq in fq_traders:
					month = fq['_month'].strftime("%Y-%m")
					if month in fq_dict.keys():
						update_count = fq_dict[month] + 1
						fq_dict.update({fq['_month'].strftime("%Y-%m"):update_count})
					else:
						fq_dict.update({fq['_month'].strftime("%Y-%m"):1})

				for month in month_list:
					temp_dict = {}
					month = month.strftime("%Y-%m")
					tr_count = traders_dict[month] if month in traders_dict.keys() else 0
					fq_count = fq_dict[month] if month in fq_dict.keys() else 0
					temp_dict.update({"yearMonth":month,"Total":tr_count, "Frequent":fq_count})
					response.append(temp_dict)

			else:

				for m in list(traders_dict.keys()):
					au_day_dict = {}
					tr_count = traders_dict[m]
					au_day_dict.update({"dayMonth":m,"Total":tr_count, "Frequent":0})
					response.append(au_day_dict)

				response = fill_missing_categories(response, "dayMonth",start_period_first,end_period_last, ['Total', 'Frequent'])
			

			if request == 'registeredusers-cumulative':
				print("registered-cumulative count")
				print(start_period_first, start_period_last)
				print(end_period_first, end_period_last)

				data = cic_users.objects.values('current_blockchain_address', 'created','gender')
				value = Coalesce(Count("current_blockchain_address", distinct=True),0)

				regusers_initial_period = data.filter(created__lt = start_period_first, gender__in = gender_filter).aggregate(value = Count('current_blockchain_address'))['value']
				print(regusers_initial_period)
				
				if duration_type == '_day':
					total = data.annotate(_day =TruncDay('created'))\
					.filter(created__gte = start_period_first, created__lt = end_period_last, gender__in = gender_filter)\
					.values(duration_type).annotate(value = value).order_by(duration_type)
				else:
					total = data.annotate(_month=TruncMonth('created'))\
					.filter(created__gte = start_period_first, created__lt = end_period_last, gender__in = gender_filter)\
					.values(duration_type).annotate(value = value).order_by(duration_type)

				initial_response = []
				populate_response = [initial_response.append({duration_name:period[duration_type].strftime(duration_format), "value":period['value']}) for period in total]
				fill_out_response = fill_missing_categories(initial_response, duration_name, start_period_first, end_period_last, ['value'])

				csum_response = {}
				
				cumsum = regusers_initial_period
				for period in fill_out_response:
					cumsum += period['value']
					csum_response.update({period[duration_name]:cumsum})

				response = []
				for month in csum_response.keys():
					temp_dict = {}
					ru_count = csum_response[month]
					tr_count = traders_dict[month] if month in traders_dict.keys() else 0
					fq_count = 0 if duration_type == '_day' else fq_dict[month] if month in fq_dict.keys() else 0
					#temp_dict.update({duration_name:month,'Registered':ru_count,"Total":tr_count, "Frequent":fq_count})
					temp_dict.update({duration_name:month,'Registered':ru_count})
					response.append(temp_dict)
			
			response = [time_summary(value=response)]

		if CACHE_ENABLED:
			cache.set(cache_key,response, CACHE_TTL)
		
		return(response)