""" SCHEMA SCRIPT
This script control how the API returns data after an API call.
The various query sub-types are defined here e.g. Summary, monthlySummary.
GenericScaler types have been used in order to return the data in a format that is usable for the front end
REMINDER - remove all unused pivots, libraries and variables after development is complete.
"""

from .types import *
from .. functions import *

cic_users = models.CicUsers
reporting_table = models.CicReportingTable

""" QUERY CLASS 
The Query class below holds the resolver functions.
these functions perfrom the neccessary data manipulations
and returns the data as defined by the respective classes above
"""

class Query(graphene.ObjectType):

	categorySummary = graphene.List(category_summary,
		from_date = graphene.String(required=True), 
		to_date = graphene.String(required=True),
		token_name= graphene.List(graphene.String,required=True),
		spend_type =graphene.List(graphene.String,required=True),
		gender =graphene.List(graphene.String,required=True), 
		tx_type =graphene.List(graphene.String,required=True),
		request = graphene.String(required=True))


	def resolve_categorySummary(self, info, **kwargs):

		cache_key = kwargs
		cache_key.update({"Query":"categorySummary"})
		response = cache.get(cache_key)

		if response is not None:
			return(response)

		from_date, to_date, token_name, spend_type, gender, tx_type, request = kwargs['from_date'], kwargs['to_date'], kwargs['token_name'], kwargs['spend_type'], kwargs['gender'], kwargs['tx_type'], kwargs['request']
		start_period_first, start_period_last, end_period_first, end_period_last = create_date_range(from_date, to_date)
		
		reporting_data = reporting_table.objects.all()
		gender_filter = gender_list if len(gender) == 0 else gender
		tx_type_filter = transfer_subtypes if len(tx_type) == 0 else tx_type
		spend_filter = spend_type_list if len(spend_type) == 0 else spend_type
		token_name_filter = token_list if len(token_name) == 0 else token_name

		summary_data = reporting_data\
		.filter(
			timestamp__gte = start_period_first,
			timestamp__lt = end_period_last, 
			tokenname__in = token_name_filter,
			t_business_type__in = spend_filter,
			s_gender__in = gender_filter,
			transfer_subtype__in = tx_type_filter)

		request = request.lower()

		if request == 'tradevolumes-category-spendtype':
			data =summary_data.annotate(label = F('t_business_type')).values("label").annotate(value=Sum("weight"))
			response = [category_summary(label=i['label'], value =i['value']) for i in data]
			cache.set(cache_key,response, CACHE_TTL)
			return(response)

		if request == 'tradevolumes-category-gender':
			data =summary_data.annotate(label = F('s_gender')).values("label").annotate(value=Sum("weight"))
			response = [category_summary(label=i['label'], value =i['value']) for i in data]
			cache.set(cache_key,response, CACHE_TTL)
			return(response)

	summaryDataTopTraders = graphene.List(time_summary,
		from_date = graphene.String(required=True), 
		to_date = graphene.String(required=True),
		token_name = graphene.List(graphene.String,required=True),
		business_type = graphene.List(graphene.String,required=True),
		gender = graphene.List(graphene.String,required=True))

	def resolve_summaryDataTopTraders(self, info, **kwargs):
		cache_key = kwargs
		cache_key.update({"Query":"summaryDataTopTraders"})
		response = cache.get(cache_key)

		if response is not None:
			return(response)

		from_date, to_date, token_name, business_type, gender = kwargs['from_date'], kwargs['to_date'], kwargs['token_name'], kwargs['business_type'], kwargs['gender']
		start_period_first, start_period_last, end_period_first, end_period_last = create_date_range(from_date, to_date)

		reporting_data = reporting_table.objects.all()
		gender_filter = gender_list if len(gender) == 0 else gender
		business_filter = spend_type_list if len(business_type) == 0 else business_type
		token_name_filter = token_list if len(token_name) == 0 else token_name

		summary_data = reporting_data.annotate(_month=TruncMonth('timestamp'))\
		.filter(
			timestamp__gte = start_period_first,
			timestamp__lt = end_period_last, 
			tokenname__in = token_name_filter, 
			s_business_type__in = business_filter, 
			s_gender__in = gender_filter,
			transfer_subtype = 'STANDARD'
			).order_by("_month")

		top_ten_traders = summary_data.values('source', 's_gender', 's_business_type')\
		.annotate(volume = Coalesce(Sum("weight"),0), count = Coalesce(Count("id"),0),).order_by('-volume')[:10]

		response = [time_summary(value=top_ten_traders)]
		cache.set(cache_key,response, CACHE_TTL)

		return(response)

