""" SCHEMA SCRIPT
This script is responsible for handling summary tiles and balance queries.
it makes use of functions defined in the functions script (located in parent folder > graphqlAPI)
where possible repetitive steps have been transformed into a function for simplicity.
"""

from .types import *
from .. functions import *

FQ_TRADER_THRESHOLD = 4
cic_users = models.CicUsers
reporting_table = models.CicReportingTable

class Query(graphene.ObjectType):

	# define query object and the filters required
	summaryData = graphene.List(summary_tiles,
		from_date = graphene.String(required=True), 
		to_date = graphene.String(required=True),
		token_name = graphene.List(graphene.String,required=True),
		spend_type = graphene.List(graphene.String,required=True),
		gender = graphene.List(graphene.String,required=True), 
		tx_type = graphene.List(graphene.String,required=True),
		request = graphene.String(required=True))

	# resolving the query object
	def resolve_summaryData(self, info, **kwargs):

		if CACHE_ENABLED:
			cache_key, response = get_cache_values(kwargs, {"Query":"summaryData"})
			response = cache.get(cache_key)

			if response is not None:
				return(response)

		# get variable passed through query from front-end
		from_date, to_date, token_name, spend_type, gender, tx_type, request = kwargs['from_date'], kwargs['to_date'], kwargs['token_name'], kwargs['spend_type'], kwargs['gender'], kwargs['tx_type'], kwargs['request']
		start_period_first, start_period_last, end_period_first, end_period_last = create_date_range(from_date, to_date)
		gender_filter, spend_filter, token_name_filter, tx_type_filter = create_filter_items(gender, spend_type, token_name, tx_type)

		reporting_data = reporting_table.objects
		summary_data = reporting_data.annotate(_month=TruncMonth('timestamp'))\
		.filter(
			timestamp__gte = start_period_first,
			timestamp__lt = end_period_last,
			tokenname__in = token_name_filter,
			t_business_type__in = spend_filter,
			s_gender__in = gender_filter,
			transfer_subtype__in = tx_type_filter
			).order_by("_month")

		all_users = cic_users.objects.values('current_blockchain_address', 'created', 'gender') # get data for registered and new registered users tile

		print(start_period_first, start_period_last)
		print(end_period_first, end_period_last)

		request = request.lower()

		if request == 'registeredusers':
			

			registered_user_data_from_date = all_users.filter(created__lt = start_period_last, gender__in = gender_filter).aggregate(value = Count('current_blockchain_address'))['value']
			registered_user_data_to_date = all_users.filter(created__lt = end_period_last, gender__in = gender_filter).aggregate(value = Count('current_blockchain_address'))['value']
			response = [summary_tiles(
				total = registered_user_data_to_date,
				start = registered_user_data_from_date,
				end = registered_user_data_to_date
				)]

		if request == 'newregisteredusers':
			value = Coalesce(Count("current_blockchain_address", distinct=True),0)
			total = all_users.filter(created__gte = start_period_first, created__lt = end_period_last, gender__in = gender_filter).aggregate(value = value)['value']
			start = all_users.filter(created__gte = start_period_first, created__lt = start_period_last, gender__in = gender_filter).aggregate(value = value)['value']
			end = all_users.filter(created__gte = end_period_first, created__lt = end_period_last, gender__in = gender_filter).aggregate(value = value)['value']
			response = [summary_tiles(total = total,start = start,end = end)]

		if request == 'traders':
			value = Coalesce(Count("source", distinct=True),0)
			data = summary_data.values('timestamp','source')
			response = get_common_summary_response_data(summary_tiles,data, value, start_period_first, start_period_last, end_period_first, end_period_last)

		if request == 'tradevolumes':
			value = Coalesce(Sum("weight"),0)
			data = summary_data.values('timestamp','weight')
			response = get_common_summary_response_data(summary_tiles,data, value, start_period_first, start_period_last, end_period_first, end_period_last)

		if request == 'transactioncount':
			value = Coalesce(Count("id"),0)
			data = summary_data.values('timestamp','id')
			response = get_common_summary_response_data(summary_tiles,data, value, start_period_first, start_period_last, end_period_first, end_period_last)

		if request == 'frequenttraders':
			# get number of months selected, used in frequent trader calculation
			month_count = summary_data.values_list("_month", flat=True).distinct()
			FQT_total = summary_data.values('_month','source')\
			.annotate(value = Count("id", distinct=True)).filter(value__gte = (FQ_TRADER_THRESHOLD * len(month_count))).order_by("-value").order_by("_month")
			FQT_total_all = FQT_total.count()

			FQT_months = summary_data.values('_month','source').annotate(value = Count("id", distinct=True)).filter(value__gte = FQ_TRADER_THRESHOLD).order_by("-value").order_by("_month")
			FQT_first_month = FQT_months.filter(_month = start_period_first).count()
			FQT_last_month = FQT_months.filter(_month = end_period_first).count()

			response = [summary_tiles(total = FQT_total_all, start = FQT_first_month, end = FQT_last_month)]

		if CACHE_ENABLED:
			cache.set(cache_key,response, CACHE_TTL)
		
		return(response)

	summaryDataSubtype = graphene.List(subtype_summary,
		from_date = graphene.String(required=True), 
		to_date = graphene.String(required=True),
		token_name = graphene.List(graphene.String,required=True),
		spend_type = graphene.List(graphene.String,required=True),
		gender = graphene.List(graphene.String,required=True), 
		tx_type = graphene.List(graphene.String,required=True),
		request = graphene.String(required=True))

	def resolve_summaryDataSubtype(self, info, **kwargs):

		if CACHE_ENABLED:
			cache_key = kwargs
			cache_key.update({"Query":"summaryDataSubtype"})
			response = cache.get(cache_key)

			if response is not None:
				return(response)

		from_date, to_date, token_name, spend_type, gender, tx_type, request = kwargs['from_date'], kwargs['to_date'], kwargs['token_name'], kwargs['spend_type'], kwargs['gender'], kwargs['tx_type'], kwargs['request']
		start_period_first, start_period_last, end_period_first, end_period_last = create_date_range(from_date, to_date)
		gender_filter, spend_filter, token_name_filter, tx_type_filter = create_filter_items(gender, spend_type, token_name, tx_type)

		reporting_data = reporting_table.objects.values('id','timestamp','weight')
		summary_data = reporting_data.annotate(_month=TruncMonth('timestamp'))\
		.filter(
			timestamp__gte = start_period_first,
			timestamp__lt = end_period_last, 
			tokenname__in = token_name_filter, 
			t_business_type__in = spend_filter, 
			s_gender__in = gender_filter,
			transfer_subtype__in = tx_type_filter
			).order_by("_month")

		request = request.upper()

		if request in tx_type_filter:

			no_transactions_data_total = summary_data.filter(transfer_subtype = request).aggregate(value = Coalesce(Count("id"),0))['value']
			no_transactions_data_first_month = summary_data.filter(transfer_subtype = request, timestamp__gte = start_period_first, timestamp__lt = start_period_last).aggregate(value = Coalesce(Count("id"),0))['value']
			no_transactions_data_last_month = summary_data.filter(transfer_subtype = request, timestamp__gte = end_period_first, timestamp__lte = end_period_last).aggregate(value = Coalesce(Count("id"),0))['value']

			tc = summary_tiles(total = no_transactions_data_total, start = no_transactions_data_first_month,end = no_transactions_data_last_month)

			trade_volume_data_total = summary_data.filter(transfer_subtype = request).aggregate(value = Coalesce(Sum("weight"),0))['value']
			trade_volume_data_first_month = summary_data.filter(transfer_subtype = request, timestamp__gte = start_period_first, timestamp__lt = start_period_last).aggregate(value = Coalesce(Sum("weight"),0))['value']
			trade_volume_data_last_month = summary_data.filter(transfer_subtype = request, timestamp__gte = end_period_first, timestamp__lte = end_period_last).aggregate(value = Coalesce(Sum("weight"),0))['value']
			
			tv = summary_tiles(total = trade_volume_data_total, start = trade_volume_data_first_month, end = trade_volume_data_last_month)
			response = [subtype_summary(trade_volumes = tv, transaction_count = tc)]

		else:

			tv = summary_tiles(total = 0, start = 0,end = 0)
			tc = summary_tiles(total = 0, start = 0, end = 0)
			response = [subtype_summary(trade_volumes = tv, transaction_count = tc)]

		if CACHE_ENABLED:
			cache.set(cache_key,response, CACHE_TTL)
		
		return(response)


	summaryDataBalance = graphene.List(time_summary,gender = graphene.List(graphene.String,required=True))

	def resolve_summaryDataBalance(self, info, **kwargs):
		if CACHE_ENABLED:

			cache_key = kwargs
			cache_key.update({"Query":"summaryDataBalance"})
			response = cache.get(cache_key)

			if response is not None:
				return(response)

		gender = kwargs['gender']
		gender_filter = gender_list if len(gender) == 0 else gender

		all_users = cic_users.objects.values("current_blockchain_address",'gender','bal').filter(gender__in = gender_filter)
		total_balance = all_users.aggregate(value = Sum('bal'))['value']
		circulation = all_users.exclude(roles__has_key ='ADMIN').aggregate(value = Sum('bal'))['value']
		# supply = int(cic_supply)/10**18
		# reserve = int(converter_reserve_balance)/10**18
		# price = cic_price
		# balance = [{"total":total_balance, "circulation":circulation, "supply":supply, "reserve":reserve, "price":price}]
		balance = [{"total":total_balance, "circulation":circulation}]
		response = [time_summary(value=balance)]

		if CACHE_ENABLED:
			cache.set(cache_key,response, CACHE_TTL)
		
		return(response)