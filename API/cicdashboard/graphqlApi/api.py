import graphene
from .api_filters import schema as filters
from .api_charts import schema_categories as categories
from .api_charts import schema_tiles as tiles
from .api_charts import schema_time_charts as time_charts

class Query(filters.Query, categories.Query, tiles.Query, time_charts.Query, graphene.ObjectType):
	pass

schema = graphene.Schema(query=Query)