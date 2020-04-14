""" SCHEMA SCRIPT
This script is responsible for providing the range of available filter values to the dashboard application.
it makes use of functions defined in the functions script (located in parent folder > graphqlAPI)
where possible repetitive steps have been transformed into a function for simplicity.
"""

from .. functions import *
from .types import filters
from .resolvers import resolve_filters

class Query(graphene.ObjectType):

	filters = graphene.List(filters)

	def resolve_filters(self, info, **kwargs):

		if CACHE_ENABLED:
			cache_key, cache_data = get_cache_values(kwargs, "filters")
			if cache_data is not None:
				return cache_data

		data = resolve_filters(kwargs)

		if CACHE_ENABLED:
			cache.set(cache_key,data, CACHE_TTL)

		return data