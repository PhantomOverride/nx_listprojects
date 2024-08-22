#!/bin/env python3
import requests
import xml.etree.ElementTree as ET
import json

try:
	with open('config.json', 'r') as config_file:
		config = json.load(config_file)
except FileNotFoundError:
	print("File 'config.json' does not exist. Rename config.sample and paste your config in it.")
	print("Exiting...")
	exit(1)

nx_refreshtoken = config.get("refreshToken", False)
nx_deviceid = config.get("deviceId", False)
nx_organizationid = config.get("organizationId", False)
nx_actinguserid = config.get("actingUserId", False)

if not (nx_refreshtoken and nx_deviceid and nx_organizationid and nx_actinguserid):
	print("Could not load at least one of the values, exiting...")
	exit(1)


def nx_get_session():
	nx_host_auth = "system.nexonia.com"
	nx_mobile_auth_endpoint = "/assistant/mobile/authentication"
	nx_proxies = {"https": "127.0.0.1:8080"}
	nx_headers = {
		"Content-Type": "application/json",
		"User-Agent": "Timesheets/5.4.10/iOS17.6.1/iPhone15,4/iPhone",
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "en-GB,en;q=0.9",
		"Accept": "application/json"
	}
	nx_auth_data = ('{"device":"IOS","product":"TIMESHEETS","deviceId":"' +
		nx_deviceid +
		'","productVersion":"5.4.10","osVersion":"17.6.1","organizationId":"' +
		nx_organizationid +
		'","refreshToken":"' +
		nx_refreshtoken + 
		'","actingUserId":"' +
		nx_actinguserid + 
		'","modelDescription":"iPhone15,4","distributionBuild":"true","apiVersion":"23"}')

	url = "https://" + nx_host_auth + nx_mobile_auth_endpoint
	#response = requests.post(url, data=nx_auth_data, proxies=nx_proxies, headers=nx_headers, verify=False)
	response = requests.post(url, data=nx_auth_data, headers=nx_headers)
	#obj = json.loads(response.text)
	#t = obj.get("token",None)
	t = json.loads(response.text).get("token", None)
	if t is None:
		print("Request getting session token have failed; will exit.")
		print("Raw response from server:")
		print(response.text)
		print("End of server error response. Now exiting...")
		exit(1)
	else:
		return t


def nx_get_projects():
	nx_host = "a.na2.system.nexonia.com"
	nx_mobile_endpoint = "/assistant/webapi/api"
	nx_projects_data = "requestXml=%3CapiRequest%3E%3CapiAction%20actionId%3D%22103%22%3E%3CgetTimeSetup%2F%3E%3C%2FapiAction%3E%0A%3C%2FapiRequest%3E"
	nx_proxies = {"https": "127.0.0.1:8080"}
	nx_headers = {
		"Content-Type": "application/x-www-form-urlencoded",
		"User-Agent": "Timesheets/5.4.10/iOS17.6.1/iPhone15,4/iPhone",
		"Authorization": "token " + nx_session_token,
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "en-GB,en;q=0.9",
		"Accept": "*/*"
	}

	url = "https://" + nx_host + nx_mobile_endpoint
	#response = requests.post(url, data=nx_projects_data, proxies=nx_proxies, headers=nx_headers, verify=False)
	response = requests.post(url, data=nx_projects_data, headers=nx_headers)
	if "errorMessage" in response.text or "An unexpected error has occurred" in response.text:
		print("Request getting projects have failed; will exit.")
		print("Raw response from server:")
		print(response.text)
		print("End of server error response. Now exiting...")
		exit(1)
	return response.text


def nx_print_projects(data):
	all_projects = []
	root = ET.fromstring(data)
	for customer in root.findall("apiResult/setup/customer"):
		customer_name = customer.attrib.get("name")
		for project in customer.findall("project"):
			project_name = project.attrib.get('name')
			# The following assumes that projects are named "1234 some-project-name". If not, then you need to re-write.
			project_id = project_name.split(" ")[0]
			project_actual_name = " ".join(project_name.split(" ")[1:])
			all_projects.append( (project_id, customer_name, project_actual_name) )

	sorted_data = sorted(all_projects, key=lambda x: int(x[0]), reverse=False)

	col_width_1 = max(len(item[0]) for item in sorted_data)
	col_width_2 = max(len(item[1]) for item in sorted_data)
	col_width_3 = max(len(item[2]) for item in sorted_data)

	print(f"{'ID'.ljust(col_width_1)}  {'Customer'.ljust(col_width_2)}  {'Project'.ljust(col_width_3)}")
	print("-" * (col_width_1 + col_width_2 + col_width_3 + 4))

	for item in sorted_data:
		print(f"{item[0].ljust(col_width_1)}  {item[1].ljust(col_width_2)}  {item[2].ljust(col_width_3)}")

	print("-" * (col_width_1 + col_width_2 + col_width_3 + 4))
	print(f"{'ID'.ljust(col_width_1)}  {'Customer'.ljust(col_width_2)}  {'Project'.ljust(col_width_3)}")


if __name__ == "__main__":
	nx_session_token = nx_get_session()
	nx_print_projects(nx_get_projects())

