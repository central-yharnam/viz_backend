from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import random
import string
from datetime import date 
import itertools
import requests
import json
import random

#this long xpath is for a div that is obscuring an actual checkbox, all of them have corresponding divs with different xpaths 
# but since they all load at the same time, it doesnt matter which one is targetted. 

blocking_div = '/html/body/div[1]/div/div/div[2]/div[1]/div/div/div[1]/div[2]/form/div/div[3]/div/div/div[5]/label'

# the different graphs that are selectable dont have easy xpath names like the rest of the things, they can be accessed by index, so we need a map to
# translate user input
graph_name_indices = {'-rq': 1, '-pollution': 2, '-reuse': 3, '-histogram': 4, '-hit rate': 5, 
						'-miss rate': 6, '-lecar lru': 7, '-arc p': 8, '-dlirs stack':9, '-cacheus lru': 10, '-cacheus learning rate': 12,
						'-cacheus q': 13}

BACKEND_URL = 'http:/localhost:5000'


class inquisition:

	def initialize(self, website):
		driver = webdriver.Firefox()
		wait = WebDriverWait(driver, 5)
		driver.get(website)
		return driver, wait

	def user_input(self, driver, wait, input_dictionary):
		
		submit = {}

		if input_dictionary.get('heat map') != None:
			heatmap_submit = '//*[@id="map-submit"]'
			submit['heat map'] = heatmap_submit
			input_dictionary.pop('heat map')

		if input_dictionary.get('overlay') != None:
			overlay_submit = '//*[@id="overlay-submit"]'
			submit['overlay'] = overlay_submit
			input_dictionary.pop('overlay')

		# the graph option elements have different xpaths so they have to be selected separately and then popped from the dictionary to make 
		# the rest of the loop behave properly

		for opts in input_dictionary['graph options']:
			print(opts, "graph options")
			current_xpath = '/html/body/div[1]/div/div/div[2]/div[1]/div/div/div[2]/div/label[' + str(graph_name_indices[opts]) + ' ]/input'
			wait.until(ec.visibility_of_element_located( ( By.XPATH, blocking_div ) ))
			element = driver.find_element_by_xpath(current_xpath)
			driver.execute_script("arguments[0].click();", element)

		input_dictionary.pop('graph options')

		for keys in input_dictionary:
			for items in input_dictionary[keys]:

				current_xpath = '//*[@id="_dbcprivate_checklist_' + keys + '_input_' + str(items) + '"]'
				wait.until(ec.visibility_of_element_located( ( By.XPATH, blocking_div ) ))
				#wait.until(ec.invisibility_of_element_located((By.XPATH, current_xpath)))
				print(current_xpath)
				wait.until(ec.presence_of_element_located((By.XPATH, current_xpath)))


				# instead of using the native selenium click element a javascript command must be used instead. 
				# this is because the checkbox is obscured by the aforementioned div and selenium's native click function has problems with it. 
				# javascript does not for some reason.

				element = driver.find_element_by_xpath(current_xpath)
				driver.execute_script("arguments[0].click();", element)

		#click on all the alternate submit buttons if specified
		for options in submit:
			element = driver.find_element_by_xpath(submit[options])
			driver.execute_script("arguments[0].click();", element)

		#submit user input for graphing
		current_xpath = '//*[@id="submit"]'
		element = driver.find_element_by_xpath(current_xpath)
		driver.execute_script("arguments[0].click();", element)


		'''else:
			heatmap_submit = '//*[@id="map-submit"]'
			wait.until(ec.visibility_of_element_located( ( By.XPATH, blocking_div ) ))

			element = driver.find_element_by_xpath(heatmap_submit)
			driver.execute_script("arguments[0].click();", element)'''

# get N random traces from a given dataset
def random_n(dataset, n):

	pld = {"dataset": dataset}

	traces = requests.post(BACKEND_URL + '/get_trace_options', json=pld)

	filtered_opts = traces.json()
	print(filtered_opts)
	#trace_opts.extend(filtered_opts)

	#print([ {'label':trace, 'value':trace} for trace in trace_opts]) 
	indices = {}
	for i in range (0, n):
		ind = random.randint(0,len(filtered_opts)-1)
		while indices.get(ind) != None:
			ind = random.randint(0,len(filtered_opts)-1)
		indices[ind] = True

	random_values = []

	for el in indices:
		random_values.append(filtered_opts[el])

	return random_values

def process_input(file):
	config = json.loads(file.read())
	adaptive = ['-lecar lru', '-arc p', '-dlirs stack', '-cacheus lru', '-cacheus learning rate', '-cacheus q']
	
	

	options = requests.get(BACKEND_URL + '/get_conf_options').json()

	user_inputs = {}
	#validate graph inputs
	

	print(options)

	#given an empty list, return all elements in field
	for params in config:
		if len(config[params]) == 0 and params != 'trace-file':
			print("empty")
			user_inputs[params] = options[params]
		else:
			user_inputs[params] = config[params]

	if len(config['trace-file']) == 0:
		for datasets in user_inputs['dataset']:
			random_trace = random_n(datasets, 1)
			user_inputs['trace-file'].append(random_trace[0])
	elif 'Random' in config['trace-file']:
		for datasets in user_inputs['dataset']:
			num = config['trace-file'].split()
			random_traces = random_n(datasets, num)
			for traces in random_traces:
				user_inputs['trace-file'].append(traces)



	for opts in user_inputs['graph options']:
		if opts in adaptive:
			print(opts)
			curr = opts.split('-')[1].split()[0]
			print(curr)
			if curr not in config['algorithm']:
				print('the graph option you chose:', opts, ' is not valid because it is dependent on an algorithm (', curr, ') not selected')
				user_inputs = False
				return user_inputs



	return user_inputs

	
#BACKEND_URL = 'http://127.0.0.1:5000'

# //*[@id="_dbcprivate_checklist_trace-file_input_moodle-2012-11-26-1"]
# //*[@id="_dbcprivate_checklist_algorithm_input_arc"]
# //*[@id="_dbcprivate_checklist_trace-file_input_webserver-2012-11-22-1"]
# //*[@id="_dbcprivate_checklist_cache_size_input_0.0005"]
# /html/body/div[1]/div/div/div[2]/div[1]/div/div/div[2]/div/label[1]/input
# /html/body/div[1]/div/div/div[2]/div[1]/div/div/div[2]/div/label[2]/input
# 12 inputs
# //*[@id="submit"]
# //*[@id="map-submit"]
# //*[@id="overlay-submit"]

#options = requests.get(BACKEND_URL + '/get_conf_options').json()
#print(options)

inquisitor = inquisition()
driver, wait = inquisitor.initialize("http://localhost:8055/")


#inquisitor.user_input(driver, wait, options, heat_map=True)

inputfile = input ("Enter filename :") 

f = open(inputfile, 'r')
print(f)

inp = process_input(f)

inquisitor.user_input(driver, wait, inp)

#random_n('FIU', 2)