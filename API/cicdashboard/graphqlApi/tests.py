import json
from .api import schema
from django.test import TestCase
from graphene.test import Client
from .models import CicReportingTable, CicUsers
from graphene_django.utils.testing import GraphQLTestCase

filters_query = """
    query {
        filters {
            yearMonthList
            tokenNameList
            genderList
            txTypeList
            spendTypeList
        }
    }
"""

summaryData = """
query summmaryData($fromDate:String!, $toDate:String!, $tokenName:[String]!,$spendType:[String]!, $gender:[String]!, $txType:[String]!, $request:String!) {
	summaryData (fromDate:$fromDate, toDate:$toDate, tokenName:$tokenName,spendType:$spendType, gender:$gender, txType:$txType, request:$request) {
		total
	    start
	    end
	}
}
"""

monthlyData = """
query monthlySummaryData($fromDate:String!, $toDate:String!, $tokenName:[String]!,$spendType:[String]!, $gender:[String]!, $txType:[String]!, $request:String!) {
	monthlySummaryData (fromDate:$fromDate, toDate:$toDate, tokenName:$tokenName,spendType:$spendType, gender:$gender, txType:$txType, request:$request) {
		value
	}
}
"""

categoryData = """
query categorySummary ($fromDate:String!, $toDate:String!, $tokenName:[String]!,$spendType:[String]!, $gender:[String]!, $txType:[String]!, $request:String!) {
	categorySummary (fromDate:$fromDate, toDate:$toDate, tokenName:$tokenName,spendType:$spendType, gender:$gender, txType:$txType, request:$request) {
		label
		value
	}
}
"""

subtypeData = """
query summaryDataSubtype($fromDate:String!, $toDate:String!, $tokenName:[String]!,$spendType:[String]!, $gender:[String]!, $txType:[String]!, $request:String!) {
	summaryDataSubtype (fromDate:$fromDate, toDate:$toDate, tokenName:$tokenName,spendType:$spendType, gender:$gender, txType:$txType, request:$request)   {
    tradeVolumes
    {
      total
      start
      end
    }
    transactionCount
    {
      total
      start
      end
    }
  }
}
"""

balanceData = """
query summaryDataBalance($gender:[String]!) {
	summaryDataBalance (gender:$gender) {
		value
	}
}
"""

topTraders = """
query summaryDataTopTraders($fromDate:String!, $toDate:String!, $tokenName:[String]!,$businessType:[String]!, $gender:[String]!) {
	summaryDataTopTraders (fromDate:$fromDate, toDate:$toDate, tokenName:$tokenName,businessType:$businessType, gender:$gender) {
		value
	}
}
"""

summaryDataQueries = [
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"registeredusers"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"newregisteredusers"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"traders"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"frequenttraders"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"tradevolumes"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"transactioncount"}
]

balanceDataQueries = [
	{"gender":[]}
]

subtypeDataQueries = [
  	{"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"standard"},
  	{"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"disbursements"},
  	{"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"agent_out"},
  	{"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"reclamation"},
  	{"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"unknown"}
]

monthlyDataQueries = [
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"tradevolumes-time-spendtype"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"transactioncount-time-spendtype"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"tradevolumes-time-gender"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"transactioncount-time-gender"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"tradevolumes-time-txsubtype"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"transactioncount-time-txsubtype"},
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"registeredusers-cumulative"},	  
	  {"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"users-time-totalvsfrequent"}
]

categoryDataQueries = [
 	{"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"tradevolumes-category-spendtype"},
  	{"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"spendType":[], "gender":[], "txType":[], "request":"tradevolumes-category-gender"}
]


topTradersQueries = [
	{"fromDate":"2018-09", "toDate":"2020-03", "tokenName":[],"businessType":[], "gender":[]}
]

class TestAPISchema(GraphQLTestCase):
	GRAPHQL_SCHEMA = schema

	def setUp(self):
		self.client = Client(self.GRAPHQL_SCHEMA)
		CicReportingTable.objects.create(
			timestamp='2020-01-10 10:00:00',
			hash="",
			source='0x3cc06c32c88aba379c4bbd4c9ebda585d7574bbf',
			s_gender="Male",
			s_business_type="Education",
			s_location="",
			target="",
			t_gender="",
			t_business_type="Education",
			t_location="",
			weight=100,
			tokenname="Sarafu",
			updated='2020-01-10 10:00:00',
			transfer_subtype="STANDARD",
			transfer_use="",
			address="",
			row_created_date = '2020-09-10 10:00:00'
			)

		CicUsers.objects.create(
			created = '2020-01-10 10:00:00',
			gender = 'Male',
			location = '',
			roles = {},
			current_blockchain_address = '0x3cc06c32c88aba379c4bbd4c9ebda585d7574bbf',
			previous_blockchain_address = '0x3cc06c32c88aba379c4bbd4c9ebda585d7574bbf',
			business_type = 'Labour',
			bal = 4000,
			start = '2020-01-10 10:00:00',
			last_send = '2020-01-10 10:00:00',
			delete_flag = False,
			row_created_date = '2020-09-10 10:00:00'
			)


	def test_filters_query(self):
		response = self.query(filters_query, op_name = 'filters')
		content = json.loads(response.content)
		# print(response)
		# print(content)
		self.assertResponseNoErrors(response)	

	def test_summaryDataQueries(self):
		for query in summaryDataQueries:
			response = self.query(
				summaryData, 
				op_name = 'summmaryData',
				variables = query)
			content = json.loads(response.content)
			# print(response)
			# print(content)
			self.assertResponseNoErrors(response)	

	def test_monthlyDataQueries(self):
		for query in monthlyDataQueries:
			response = self.query(
				monthlyData, 
				op_name = 'monthlySummaryData',
				variables = query)
			content = json.loads(response.content)
			# print(response)
			# print(content)
			self.assertResponseNoErrors(response)	

	def test_categoryDataQueries(self):
		for query in categoryDataQueries:
			response = self.query(
				categoryData, 
				op_name = 'categorySummary',
				variables = query)
			content = json.loads(response.content)
			# print(response)
			# print(content)
			self.assertResponseNoErrors(response)
	
	def test_subtypeDataQueries(self):
		for query in subtypeDataQueries:
			response = self.query(
				subtypeData, 
				op_name = 'summaryDataSubtype',
				variables = query)
			content = json.loads(response.content)
			# print(response)
			# print(content)
			self.assertResponseNoErrors(response)	


	def test_balanceDataQueries(self):
		for query in balanceDataQueries:
			response = self.query(
				balanceData, 
				op_name = 'summaryDataBalance',
				variables = query)
			content = json.loads(response.content)
			# print(response)
			# print(content)
			self.assertResponseNoErrors(response)	


	def test_topTradersQueries(self):
		for query in topTradersQueries:
			response = self.query(
				topTraders, 
				op_name = 'summaryDataTopTraders',
				variables = query)
			content = json.loads(response.content)
			# print(response)
			# print(content)
			self.assertResponseNoErrors(response)	