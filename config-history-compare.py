#!/usr/bin/env python

############################################################################
#
# This is a python script to compare configurations history
# by comparing the  configs stored in Ambari Database.
#
# This tool can be run from Windows, Mac or Linux machines installed with
# python 2.x and one of the python modules : 'pycurl' or 'requests'
# The machine should have access to both Ambari Server nodes on each clusters
#
# Type 'python cluster-compare.py' and press enter for running instruction
#
# For any questions or suggestions please contact : ayusuf@hortonworks.com
############################################################################

import sys
import json
import cStringIO
import difflib
import random
import time
import datetime
import getpass
import collections
import getopt
import codecs

# Increment the version when you make modifications
scriptVersion = '1.0'

# Change the default values for the below parameters
# ==================================================
usernameA = 'admin'
usernameB = 'admin'
ambariPortA = '8080'
ambariPortB = '8080'

# Please add the name of the property you would like to mask below array
propertiesToBeMasked = [
'oozie.service.JPAService.jdbc.password',
'javax.jdo.option.ConnectionPassword'
]
# ==================================================

#------Some good colors-----
shadowcolor = '#666'
headergreen = '#4CAF50'
verylightred = '#f89e90'
bgExist = '#f89e90'
bgExist = '#f9a562'
bgDummy = '#90cc92'
verylightred = '#f89e90'
bgExist = '#f89e90'
niceblue = '#4184F3'
nicegreen = '#3D9400'
bgAlternate = '#f2f2f2'
whitesmoke = '#f5f5f5'
selectionblue = '#7dd4f6'

# ========= Some good Fonts ======================================
georrgia = 'Georgia, Georgia, serif;'
palatino = "'Palatino Linotype', 'Book Antiqua', Palatino, serif;"
lucida = "'Lucida Console', Monaco, monospace"
# ================================================================

hFont = georrgia
pFont = georrgia
aFont = georrgia
thFont = palatino
tdFont = palatino

bgHighlight = verylightred
bgHeader = headergreen
highlightTextColor = 'yellow'

blankSpace = '&nbsp;'
classTemplate = 'class="%s"'

outputFile = sys.stdout
clusterAHeading = ''
clusterBHeading = ''
bgNone = ''
strMissingConfiguration = '*** Not Configured ***'
diffData = list()

def printLine(line):
	outputFile.write(line + '\n')

def printStyleSheet():
	printLine('<style>')
	printLine('div {')
	printLine('    padding: 0px 20px 20px 20px;')
	#printLine('    border: 1px solid #ddd;')
	printLine('}')
	printLine('h1,h2,h3,h4,h5,h6 {')
	printLine('    font-family: %s;' % hFont)
	printLine('}')
	#printLine('h1 {')
	#printLine('    padding-top: 20px;')
	#printLine('}')
	#printLine('h2 {')
	#printLine('    padding-top: 15px;')
	#printLine('}')
	#printLine('h3 {')
	#printLine('    padding-top: 10px;')
	#printLine('}')
	printLine('a {')
	printLine('    font-family: %s;' % aFont)
	printLine('}')
	printLine('p {')
	printLine('    font-family: %s;' % pFont)
	printLine('}')
	printLine('th {')
	printLine('    font-family: %s;' % thFont)
	printLine('    text-align: left;')
	printLine('    color: %s;' % 'white')
	printLine('    background-color: %s;' % bgHeader)
	printLine('    border-bottom: 1px solid #ddd;')
	printLine('    padding: 5px;')
	printLine('}')
	printLine('th.sub {')
	printLine('    text-align: left;')
	#printLine('    background-color: %s;' % darkgray)
	printLine('}')
	printLine('th.subright {')
	printLine('    text-align: right;')
	#printLine('    background-color: %s;' % darkgray)
	printLine('}')
	printLine('tr {')
	printLine('    border-bottom: 1px solid #ddd;')
	printLine('}')
	printLine('tr.alternate {')
	printLine('    border-bottom: 0px solid #ddd;')
	printLine('}')
	printLine('td {')
	printLine('    font-family: %s;' % tdFont)
	printLine('    padding-left: 5px;')
	printLine('    padding-right: 5px;')
	printLine('    vertical-align: top;')
	printLine('    word-wrap: break-word;')
	#printLine('    border-bottom: 1px solid #ddd;')
	printLine('}')
	printLine('td.highlight {')
	printLine('    background-color: %s;' % bgHighlight)
	printLine('    border-bottom: 1px solid #ddd;')
	printLine('}')
	printLine('td.exists {')
	printLine('    background-color: %s;' % bgExist)
	printLine('    border-bottom: 1px solid #ddd;')
	printLine('}')
	printLine('td.dummy {')
	printLine('    background-color: %s;' % bgDummy)
	printLine('    border-bottom: 1px solid #ddd;')
	printLine('}')
	printLine('td.different {')
	printLine('    background-color: %s;' % bgHighlight)
	printLine('    border-bottom: 1px solid #ddd;')
	printLine('}')
	printLine('td.extproperty {') 
	printLine('    border-bottom: 1px solid #ddd;')
	printLine('}')
	printLine('td.separator {')
	printLine('    background-color: %s;' % bgHeader)
	printLine('    padding: 1px;')
	printLine('}')
	printLine('table {')
	printLine('    table-layout: fixed;')
	printLine('    border-collapse: collapse;')
	printLine('    border: 1px solid #ddd;')
	printLine('    width: 100%;')
	printLine('    -moz-box-shadow: 0 0 15px %s' % shadowcolor)
	printLine('    -webkit-box-shadow: 0 0 15px %s;' % shadowcolor)
	printLine('    box-shadow: 0 0 15px %s' % shadowcolor)
	printLine('}')

	printLine('span.texthighlight {')
	printLine('    background-color: %s;' % highlightTextColor)
	printLine('}')
	printLine('span.textul {')
	printLine('    text-decoration: underline;')
	printLine('}')
	printLine('span.textulhl {')
	printLine('    color: %s;' % niceblue)
	#printLine('    text-decoration: underline;')
	printLine('}')

	printLine('tr:nth-child(even) {')
	printLine('    background-color: %s' % bgAlternate)
	printLine('}')
	printLine('tr.alternate:nth-child(even) {')
	printLine('    background-color: %s' % whitesmoke)
	printLine('}')
	printLine('</style>')

def runUsingPyCurl(url, username, password):
	c = pycurl.Curl()
	c.setopt(pycurl.URL, url)
	s = cStringIO.StringIO()
	c.setopt(c.WRITEFUNCTION, s.write)
	c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
	c.setopt(pycurl.USERPWD, (username + ':' + password))
	c.perform()
	response = c.getinfo(pycurl.HTTP_CODE)
	if response != 200:
		errorString = "Error executing the URL: '%s' for the username: '%s'\n" % (url, username)
		sys.stderr.write(errorString)
		sys.exit(2)
	return s.getvalue()

def runUsingRequests(url, username, password):
	try:
		from requests.packages.urllib3.exceptions import InsecureRequestWarning
	except:
		pass
	else:
		requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

	try:
		from requests.packages.urllib3.exceptions import InsecurePlatformWarning
	except:
		pass
	else:
		requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

	r = requests.get(url, auth=(username, password), verify=False)
	if r.status_code != 200:
		errorString = "Error executing the URL: '%s' for the username: '%s'\n" % (url, username)
		sys.stderr.write(errorString)
		sys.exit(2)
	return r.text

def getURLData(url, username, password):
	print ">>> " + url   # Ajmal
	if module == 'pycurl':
		return runUsingPyCurl(url, username, password)
	elif module == 'requests':
		return runUsingRequests(url, username, password)
		
def printHeader():
	docMainHeading = 'Cluster Name: ' + clusterA + ' (Ambari Server: ' + ambariServerA + ')'
	docTitle = 'Config history comparison: %s and %s' % (clusterAHeading, clusterBHeading)
	docSubHeading = 'Comparison between:</br><span class="textulhl">%s</span> and <span class="textulhl">%s</span>' % (clusterAHeading, clusterBHeading)

	printLine('<!DOCTYPE html>')
	printLine('<html>')

	printLine('<head>')
	printLine('<title>%s</title>' % docTitle)
	printStyleSheet()
	printLine('</head>')

	printLine('<body>')
	printLine('<div class=pagePadding>')
	printLine('<h1></br>%s</h1>' % docMainHeading)
	printLine('<h2></br>%s</h2>' % docSubHeading)
	printLine('<p>Generated on : %s</p>' % time.strftime("%a, %d %b %Y %I:%M %p %Z"))

def highlightDiffLine(line, diffChars):
	started = False
	newLine = ''
	remaining = ''
	for x in range(0, len(line)):
		if x >= len(diffChars) or diffChars[x] == '\n':
			remaining = line[x:]
			break

		if diffChars[x] != ' ':
			if not started:
				newLine += '<span class="texthighlight">'
				started = True
		else:
			if started:
				newLine += '</span>'
				started = False

		if started and line[x] == ' ':
			newLine += '&nbsp;'
		else:
			newLine += line[x]

	if started:
		newLine += '</span>'
	newLine += remaining
	return newLine

def calcDiffData(left, right):
	#leftList = [ln.strip() for ln in str(left).splitlines()]
	#rightList = [ln.strip() for ln in str(right).splitlines()]
	leftList = [ln.strip() for ln in left.splitlines()]
	rightList = [ln.strip() for ln in right.splitlines()]

	d = difflib.Differ()
	diffResult = list(d.compare(leftList, rightList))
	
	indx = 1
	diffList = list()
	prevOperator = ''
	nextOperator = ''
	for line in diffResult:
		operator = line[0]
		line = line[2:]

		if indx < len(diffResult):
			nextOperator = diffResult[indx][0]
			if nextOperator == '?':
				diffChars = diffResult[indx][2:]
				line = highlightDiffLine(line, diffChars)
		else:
			nextOperator = ''
		
		if operator == '-':
			diffList.append((line, 'exists', '', 'dummy'))
		elif operator == '+':
			if prevOperator == '?' or nextOperator == '?':
				l,lh,r,rh = diffList[-1]
				lh,r,rh = 'different',line,'different'
				diffList[-1] = (l,lh,r,rh)
			else:
				diffList.append(('', 'dummy', line, 'exists'))
		elif operator == '?':
			pass
		else:
			diffList.append((line, '', line, ''))
		prevOperator = operator
		indx += 1
	return diffList

def compareAndDumpHTML(service, type, dataA, dataB):
	mergedProps = sorted(set(dataA.keys() + dataB.keys()))
	if mergedProps is None:
		return

	printLine('<table>')
	printLine('<tr>')
	printLine('<th %s>%s : %s</th>' % ('width="24%"', service, type))
	printLine('<th %s>%s</th>' % ('width="38%"', clusterAHeading))
	printLine('<th %s>%s</th>' % ('width="38%"', clusterBHeading))
	printLine('</tr>')

	atleastOneProp = False
	extendedDiffList = list()
	for prop in mergedProps:
		valueA = valueB = strMissingConfiguration
		if prop in dataA:
			valueA = dataA[prop].strip()
		if prop in dataB:
			valueB = dataB[prop].strip()

		if prop == 'content':
			propName = type + ' template'
		else:
			propName = prop

		classTag = ''
		if valueA != valueB:
			classTag = classTemplate % 'highlight'

		if '\n' in valueA or '\n' in valueB:
			extendedDiffList.append((propName, calcDiffData(valueA, valueB)))
		else:
			diffLines = calcDiffData(valueA, valueB)
			if len(diffLines) == 1:
				valueA, dummy1, valueB, dummy2 = diffLines[0]
			elif len(diffLines) == 2:
				valueA, dummy1, dummy2, dummy3 = diffLines[0]
				dummy1, dummy2, valueB, dummy3 = diffLines[1]

			atleastOneProp = True
			printLine('<tr>')
			printLine('<td %s %s>%s</td>' % (classTag, 'width="500"', propName.strip()))
			printLine('<td %s>%s</td>' % (classTag, valueA))
			printLine('<td %s>%s</td>' % (classTag, valueB))
			printLine('</tr>')

	for prop, data in extendedDiffList:
		if atleastOneProp:
			printLine('<tr>')
			printLine('<td %s %s></th>' % ('colspan="3"', classTemplate % 'separator'))
			printLine('</tr>')
		printExtendedComparison(prop, data)
	printLine('</table>')

def printExtendedComparison(propName, diffList):
	noRows = len(diffList)

	firstRow = True
	for l, hl, r, hr in diffList:
		if not l:
			l = blankSpace
		if not r:
			r = blankSpace
		printLine('<tr class="%s">' % 'alternate')
		if firstRow:
			printLine('<td class="%s" %s>%s</td>' % ('extproperty', ('rowspan="%s"' % noRows), propName))
			firstRow = False
		printLine('<td class="%s">%s</td>' % (hl, l))
		printLine('<td class="%s">%s</td>' % (hr, r))
		printLine('</tr>')

def getClusterNameAsJSON(base_url, username, password):
	url = '%s/clusters/' % (base_url)
	return json.loads(getURLData(url, username, password))['items'][0]['Clusters']['cluster_name']

def getMaskedPropertyValues(listProperties):
	for prop in listProperties:
		if str(prop).strip() in propertiesToBeMasked:
			listProperties[prop] = '[*** Masked ***]'
	return listProperties

def getAllConfigs(base_url, username, password, cluster, type):
	url = '%s/clusters/%s' % (base_url, cluster)
	if type == 'Latest':
		config_versions_url = url + '/configurations/service_config_versions?is_current=true'
	elif type == 'First':
		config_versions_url = url + '/configurations/service_config_versions?service_config_version=1'
	else:
		config_versions_url = url + '/configurations/service_config_versions'

	typeItems = json.loads(getURLData(config_versions_url, username, password))['items']
	service_group_version_dict = {}

	for item in typeItems:
		service = str(item['service_name'])
		if service not in service_group_version_dict.keys():
			service_group_version_dict[str(service)] = {}

		if item['group_id'] == -1:
			group_name = 'Default'
		else:
			group_name = str(item['group_name'])
		service_group_version_dict[service][group_name] = item['service_config_version']
	return service_group_version_dict
	

def getServiceConfigVerionMap(base_url, username, password, cluster, configDate):
	if configDate == 'Current':
		return 'Latest', getAllConfigs(baseUrlA, usernameA, passwordA, clusterA, 'Latest')

	cDate = datetime.datetime.strptime(configDate, '%Y-%m-%d@%H:%M')
	inputDate = int(time.mktime(cDate.timetuple()))
	
	url = '%s/clusters/%s' % (base_url, cluster)
	config_versions_url = url + '/configurations/service_config_versions'
	typeItems = json.loads(getURLData(config_versions_url, username, password))['items']

	service_group_version_dict = {}
	temp_service_group_date = {}

	for y in typeItems:
		service_name = str(y['service_name'])
		if y['group_id'] == -1:
			group_name = 'Default'
		else:
			group_name = str(y['group_name'])
		config_version = y['service_config_version']
		mod_time = int(y['createtime']/1000/60)*60

		if service_name not in temp_service_group_date:
			temp_service_group_date[service_name] = {}
		if group_name not in temp_service_group_date[service_name]:
			temp_service_group_date[service_name][group_name] = (0, 0)

		curr_time, curr_version = temp_service_group_date[service_name][group_name]
		if mod_time <= inputDate and mod_time >= curr_time:
			if curr_time == mod_time and config_version < curr_version:
					continue
			temp_service_group_date[service_name][group_name] = (mod_time, config_version)
			if service_name not in service_group_version_dict.keys():
				service_group_version_dict[service_name] = {}
			service_group_version_dict[service_name][group_name] = config_version

	if len(service_group_version_dict) == 0:
		return 'First', getAllConfigs(baseUrlA, usernameA, passwordA, clusterA, 'First')

	return 'Good', service_group_version_dict

def getAllHistoricalConfigs(base_url, username, password, cluster, serviceVerMap):
	url = '%s/clusters/%s' % (base_url, cluster)
	config_versions_url = url + '/configurations/service_config_versions?service_name.in(%s)&service_config_version.in(%s)'

	dictServices = {}
	for service in serviceVerMap.keys():
		versionsString = str(serviceVerMap[service]['Default'])
		for group in serviceVerMap[service]:
			if group != 'Default':
				versionsString += ',' + str(serviceVerMap[service][group])
		typeItems = json.loads(getURLData(config_versions_url % (service, versionsString), username, password))['items']
		dictGroups = {}
		for y in typeItems:
			listTypes = {}
			if y['group_id'] == -1:
				group_name = 'Default'
			else:
				group_name = y['group_name']
			for z in y['configurations']:
				listTypes[z['type']] = getMaskedPropertyValues(z['properties'])
			dictGroups[group_name] = listTypes
		dictServices[service] = dictGroups
	return dictServices

def getAllHistoricalConfigs111(base_url, username, password, cluster, serviceVerMap, configDate):
	#inputDate = int((datetime.datetime(2016,12,15,15,44) - datetime.datetime(1970,1,1)).total_seconds())

	cDate = datetime.datetime.strptime(configDate, '%Y-%m-%d@%H:%M')
	inputDate = time.mktime(cDate.timetuple())

	url = '%s/clusters/%s' % (base_url, cluster)
	config_versions_url = url + '/configurations/service_config_versions?service_name.in(%s)'

	dictServices = {}
	for service in serviceVerMap.keys():
		typeItems = json.loads(getURLData(config_versions_url % (service), username, password))['items']
		
		version_date = 0
		outstr = 'Blank'
		group_version_date = {}
		group_version_number = {}
		group_valid_items = {}

		for y in typeItems:
			mod_time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(y['createtime'])/1000))
			mod_time = int(y['createtime']/1000/60)*60

			if y['group_id'] not in group_version_date.keys():
				group_version_date[y['group_id']] = 0
				group_version_number[y['group_id']] = 0

			if mod_time <= inputDate  and mod_time >= group_version_date[y['group_id']]:
				if group_version_date[y['group_id']] == mod_time and y['service_config_version'] < group_version_number[y['group_id']]:
					continue
				group_version_date[y['group_id']] = mod_time
				group_version_number[y['group_id']] = y['service_config_version']
				group_valid_items[y['group_id']] = y

		dictGroups = {}
		for y in group_valid_items.values():
			listTypes = {}
			if y['group_id'] == -1:
				group_name = 'Default'
			else:
				group_name = y['group_name']
			#print '=>=>=>=>', service, group_name, y['service_config_version']
			for z in y['configurations']:
				listTypes[z['type']] = getMaskedPropertyValues(z['properties'])
			dictGroups[group_name] = listTypes

		if len(dictGroups) > 0:
			dictServices[service] = dictGroups

	return dictServices

def printFooter():
	printLine('</div>')
	printLine('<body>')
	printLine('<html>')

def getStackDisplayVersion(base_url, username, password, cluster):
	stack_versions_items = json.loads(getURLData('%s/clusters/%s/stack_versions' % (base_url, cluster), username, password))['items']
	#stack = stack_version = repo_version = ''
	for sv_item in stack_versions_items:
		stack = str(sv_item['ClusterStackVersions']['stack'])
		stack_version = str(sv_item['ClusterStackVersions']['version'])
		repo_version = str(sv_item['ClusterStackVersions']['repository_version'])
		rv_state = json.loads(getURLData('%s/clusters/%s/stack_versions/%s' % (base_url, cluster, repo_version), username, password))['ClusterStackVersions']['state']
		if str(rv_state) == 'CURRENT':
			break
		else:
			stack = stack_version = repo_version = ''

	hdp_version = json.loads(getURLData('%s/stacks/%s/versions/%s/repository_versions/%s' % (base_url, stack, stack_version, repo_version), username, password))['RepositoryVersions']['repository_version']

	return stack, stack_version, hdp_version

def getGroupsIDandLabel(serviceVerMapA, service):
	grps = {}
	if service in serviceVerMapA:
		grps = sorted(serviceVerMapA[service].keys())

	groupLink = 'Default ( V' + str(serviceVerMapA[service]['Default']) + ' )'
	
	for grp in grps:
		if grp != 'Default':
			groupString = grp +' ( V' + str(serviceVerMapA[service][grp]) + ' )'
			groupLink += ',  <a href=#%s>%s</a>' % ('CustomConfigGroups', groupString)
			
	return groupLink

def printServiceComparisonTableAsHTML(serviceVerMapA, serviceVerMapB):
	printLine('<h1></br>Installed Services</h1>')
	printLine('<table>')
	printLine('<tr>')
	printLine('<th %s %s>%s</th>' % ('width="14%"', 'rowspan="2"', 'Service'))
	printLine('<th %s %s>%s</th>' % ('width="43%"', 'colspan="2"', clusterAHeading))
	printLine('<th %s %s>%s</th>' % ('width="43%"', 'colspan="2"', clusterBHeading))
	printLine('</tr>')
	printLine('<tr>')
	printLine('<th %s>%s</th>' % ('width="10%"', 'Installed?'))
	printLine('<th %s>%s</th>' % ('width="20%"', 'Config Groups (Version)'))
	printLine('<th %s>%s</th>' % ('width="10%"', 'Installed?'))
	printLine('<th %s>%s</th>' % ('width="20%"', 'Config Groups (Version)'))
	printLine('</tr>')

	serviceMergedList = sorted(set(serviceVerMapA.keys() + serviceVerMapB.keys()))
	for service in serviceMergedList:
		classTag = ''
		colA1 = colB1 = grpLinkA = grpLinkB = '-'
		colA3 = colB3 = 'Default'
		if service in serviceVerMapA.keys():
			colA1 = 'Yes'
			grpLinkA = getGroupsIDandLabel(serviceVerMapA, service)
		if service in serviceVerMapB.keys():
			colB1 = 'Yes'
			grpLinkB = getGroupsIDandLabel(serviceVerMapB, service)
		if grpLinkA != grpLinkB:  # Check this - Ajmal
			classTag = classTemplate % 'highlight'

		printLine('<tr>')
		printLine('<td %s><a %s>%s</a></td>' % (classTag, 'href="#%s"' % service, service))

		printLine('<td %s>%s</td>' % (classTag, colA1))
		printLine('<td %s>%s</td>' % (classTag, grpLinkA))

		printLine('<td %s>%s</td>' % (classTag, colB1))
		printLine('<td %s>%s</td>' % (classTag, grpLinkB))
		printLine('</tr>')
	printLine('</table>')

	return serviceMergedList

def printConfigTypeComparisonTablesAsHTML(serviceMergedList, configDataA, configDataB):
	service_count = 1
	for service in serviceMergedList:
		printLine('<h2 %s></br>%d. %s Service Configurations</h2>' % ('id=%s' % service, service_count, service))

		if service in configDataA.keys():
			listTypesA = configDataA[service]['Default']
		else:
			listTypesA = {}
		if service in configDataB.keys():
			listTypesB = configDataB[service]['Default']
		else:
			listTypesB = {}

		configTypeMergedList = sorted(set(listTypesA.keys() + listTypesB.keys()))
		type_count = 1
		for type in configTypeMergedList:
			printLine('<h3></br>%d.%d. %s : %s</h3>' % (service_count, type_count, service, type))

			if type in listTypesA.keys():
				propsA = listTypesA[type]
			else:
				propsA = {}
			if type in listTypesB.keys():
				propsB = listTypesB[type]
			else:
				propsB = {}

			compareAndDumpHTML(service, type, propsA, propsB)
			type_count += 1

		service_count += 1

def splitConfigGroups(configData):
	defaultCGData = {}
	otherCGsData = {}
	for service in configData:
		defaultGP = {}
		otherGP = {}
		for group in configData[service]:
			if group == 'Default':
				defaultGP[group] = configData[service][group]
			else:
				otherGP[group] = configData[service][group]
		defaultCGData[service] = defaultGP
		if len(otherGP) > 0:
			otherCGsData[service] = otherGP
	return defaultCGData, otherCGsData

def printOtherConfigGroupsTablesAsHTML(newList):
	if len(newList) > 0:
		printLine('<h2 %s></br>Custom Config Groups</h2>' % ('id=%s' % 'CustomConfigGroups'))
		#printLine('<p>There are no custom config groups</p>')

	service_count = 1
	for item in newList:
		printLine('<h3></br>%d. %s</h3>' % (service_count, item))
		firstRow = True
		printLine('<table>')
        	printLine('<tr>')
        	printLine('<th %s>%s</th>' % ('width="25%"', 'Cluster Name'))
        	printLine('<th %s>%s</th>' % ('width="25%"', 'Config Group'))
        	printLine('<th %s>%s</th>' % ('width="25%"', 'Property (Key)'))
        	printLine('<th %s>%s</th>' % ('width="25%"', 'Value'))
        	printLine('</tr>')
		for prop, dummyC, dummyCG, cluster, configgroup, value in newList[item]:
			tag = ''
			if dummyCG == 0:
				tag = '<b>'
				if not firstRow:
					printLine('<tr>')
					printLine('<td %s %s></th>' % ('colspan="4"', classTemplate % 'separator'))
					printLine('</tr>')
					printLine('<tr>')
					printLine('</tr>')
                	printLine('<tr>')
                	printLine('<td>%s%s%s</td>' % (tag, cluster, tag))
                	printLine('<td>%s%s%s</td>' % (tag, configgroup, tag))
                	printLine('<td>%s%s%s</td>' % (tag, prop, tag))
                	printLine('<td>%s%s%s</td>' % (tag, value, tag))
			printLine('</tr>')
			firstRow = False
        	printLine('</table>')
		service_count += 1

def getSortedConfigGroupsList(otherCGsDataA, otherCGsDataB, defaultCGDataA, defaultCGDataB):
	serviceTypeList = {}

	for service in otherCGsDataA:
		for group in otherCGsDataA[service]:
			for type in otherCGsDataA[service][group]:
				key = service + ' : ' + type
				if key not in serviceTypeList:
					serviceTypeList[key] = set()
				for prop in otherCGsDataA[service][group][type]:
					serviceTypeList[key].add((prop, 'A', 1, clusterAHeading, group, otherCGsDataA[service][group][type][prop]))
					if prop in defaultCGDataA[service]['Default'][type]:
						serviceTypeList[key].add((prop, 'A', 0, clusterAHeading, 'Default', defaultCGDataA[service]['Default'][type][prop]))
					else:
						serviceTypeList[key].add((prop, 'A', 0, clusterAHeading, 'Default', strMissingConfiguration))

	for service in otherCGsDataB:
		for group in otherCGsDataB[service]:
			for type in otherCGsDataB[service][group]:
				key = service + ' : ' + type
				if key not in serviceTypeList:
					serviceTypeList[key] = set()
				for prop in otherCGsDataB[service][group][type]:
					serviceTypeList[key].add((prop, 'B', 1, clusterBHeading, group, otherCGsDataB[service][group][type][prop]))
					if prop in defaultCGDataB[service]['Default'][type]:
						serviceTypeList[key].add((prop, 'B', 0, clusterBHeading, 'Default', defaultCGDataB[service]['Default'][type][prop]))
					else:
						serviceTypeList[key].add((prop, 'B', 0, clusterBHeading, 'Default', strMissingConfiguration))

	sortedServiceTypeList = {}
	for serviceType in serviceTypeList:
		sortedServiceTypeList[serviceType] = sorted(serviceTypeList[serviceType])

	return collections.OrderedDict(sorted(sortedServiceTypeList.items()))

def GetBaseURLs(protocolA, ambariServerA, ambariPortA):
	if (protocolA == 'y'):
		baseUrlA = 'https://%s:%s/api/v1' % (ambariServerA, ambariPortA)
	else:
		baseUrlA = 'http://%s:%s/api/v1' % (ambariServerA, ambariPortA)

	return baseUrlA

def PrintUsage():
	sys.stderr.write('Version : %s\n' % scriptVersion)
	sys.stderr.write('Usage:\n')
	sys.stderr.write('python ' + sys.argv[0] + ' -h <ambariServer> -o <configDate> [-n <configDate>] [-u <username>] [-c <cluster>] [-p <port>] [-s]\n')
	sys.stderr.write('Options:\n')
	sys.stderr.write('    -h, --host <ambariServer>\n\tRequired.\n\tIP/Hostname of Ambari Server\n')
	sys.stderr.write('    -o, --olderDate <configDate>\n\tRequired.\n\tProvide the older date in \"YYYY-MM-DD HH:MI\" or YYYY-MM-DD@HH:MI\n')
	sys.stderr.write('    -n, --newerDate <configDate>\n\tOptional.\n\tProvide the newer date in \"YYYY-MM-DD HH:MI\" or YYYY-MM-DD@HH:MI\n\tDefault: Current Date & Time. Will use the current active versions/configs\n')
	sys.stderr.write('    -u, --username <username>\n\tOptional.\n\tUsername for Ambari.\n\tDefault: "%s". Will be prompted for the password\n' % usernameA)
	sys.stderr.write('    -p, --port <port>\n\tOptional.\n\tPort number for Ambari Server.\n\tDefault: "%s"\n' % ambariPortA)
	sys.stderr.write('    -c, --cluster <cluster>\n\tOptional.\n\tName of the cluster.\n\tDefault: First available cluster name configured in Ambari\n')
	sys.stderr.write('    -s, --sslEnabled\n\tOptional.\n\tFlag to indicate whether SSL is enabled for the Ambari URL.\n\tDefault: Disabled\n')
	sys.stderr.write('Note:\n')
	sys.stderr.write('\tIf the script takes too long and times out, please try\n\tusing the IP Address of Ambari Server instead of hostname.\n')


############################################
# Program start
############################################
module = 'none'
try:
	import pycurl
except:
	try:
		import requests
	except:
		errorString = "Error:\n"
		errorString += "  Could not import 'pycurl' or 'requests' module. One of them is required.\n"
		errorString += "  Try running from one of the Ambari Server hosts; it should have 'pycurl' module installed.\n"
		errorString += "  You can test by running \"python -c 'import pycurl'\" or \"python -c 'import requests'\". This should NOT throw any error.\n"
		errorString += "  You may use 'pip install' or 'easy_install' to install 'requests' or 'pycurl' module.\n"
		sys.stderr.write(errorString)
		sys.exit(2)
	else:
		module = 'requests'
else:
	module = 'pycurl'


olderConfigDate = ''
newerConfigDate = 'Current'
ambariServerA = ''
clusterA = ''
protocolA = 'n'

try:
	opts, args = getopt.getopt(sys.argv[1:],"h:o:n:u:c:p:s",["host=","olderDate=","newerDate","user=","cluster=","port=","sslEnabled="])
except getopt.GetoptError, optsError:
	sys.stderr.write('\nInvalid option : %s\n\n' % optsError)
	PrintUsage()
	sys.exit(2)

for opt, arg in opts:
	if opt in ("-o", "--olderDate"):
		olderConfigDate = arg.replace(' ','@')
	elif opt in ("-n", "--newerDate"):
		newerConfigDate = arg.replace(' ','@')
	elif opt in ("-h", "--host"):
		ambariServerA = arg
	elif opt in ("-u", "--user"):
		usernameA = arg
	elif opt in ("-c", "--cluster"):
		clusterA = arg
	elif opt in ("-p", "--port"):
		ambariPortA = arg
	elif opt in ("-s", "--sslEnabled"):
		protocolA = 'y'
	else:
		PrintUsage()
		sys.exit(2)

if len(args) > 0:
	sys.stderr.write("\nInvalid argument(s): ")
	for arg in args:
		sys.stderr.write('%s ' % arg)
	sys.stderr.write("\nNote: Please check if '-' is the ascii hyphen. ")
	sys.stderr.write("May contain non-ASCII character(s) if copied from word applications.\n")
	sys.stderr.write("\n")
	
	PrintUsage()
	sys.exit(2)

if olderConfigDate == '' or ambariServerA == '':
	PrintUsage()
	sys.exit(2)

passwordA = getpass.getpass('Ambari password for %s [%s]: ' % (ambariServerA, usernameA))
if not passwordA:
	passwordA = 'admin'

baseUrlA = GetBaseURLs(protocolA, ambariServerA, ambariPortA)

# Wraping around str() to convert unicode to str - for using in URL
if not clusterA:
	clusterA = str(getClusterNameAsJSON(baseUrlA, usernameA, passwordA))

sys.stdout.write('\nParameters used:')
sys.stdout.write('\nAmbari Host\t\t: %s' % ambariServerA)
sys.stdout.write('\nOlder Config Date\t: %s' % olderConfigDate)
sys.stdout.write('\nNewer Config Date\t: %s' % newerConfigDate)
sys.stdout.write('\nUsername\t\t: %s' % usernameA)
sys.stdout.write('\nPort\t\t\t: %s' % ambariPortA)
sys.stdout.write('\nCluster Name\t\t: %s' % clusterA)
sys.stdout.write('\nSSLEnabled\t\t: %s' % protocolA)
sys.stdout.write('\n\n')

clusterAHeading = 'Config properties on <span class="textul">%s</span>' % datetime.datetime.strptime(olderConfigDate, '%Y-%m-%d@%H:%M').strftime('%a, %d %b %Y %I:%M %p')
if newerConfigDate == 'Current':
	currentDateTime = time.strftime('%a, %d %b %Y %I:%M %p')
	clusterBHeading = 'Current Config Properties (<span class="textul">%s</span>)' % currentDateTime
else:
	currentDateTime = datetime.datetime.strptime(newerConfigDate, '%Y-%m-%d@%H:%M').strftime('%a, %d %b %Y %I:%M %p')
	clusterBHeading = 'Config properties on <span class="textul">%s</span>' % currentDateTime

outFilename = '%s_%s_%s.html' % (clusterA, olderConfigDate.replace(':',''), newerConfigDate.replace(':', ''))
#outFilename = '%s_%s.html' % (clusterA, 'ConfigComparison') # Ajmal: Delete this line
outputFile = codecs.open(outFilename, 'w', 'utf-16') # Ajmal

statusA, serviceVerMapA = getServiceConfigVerionMap(baseUrlA, usernameA, passwordA, clusterA, olderConfigDate)
statusB, serviceVerMapB = getServiceConfigVerionMap(baseUrlA, usernameA, passwordA, clusterA, newerConfigDate)

if statusA == 'First':
	clusterAHeading += ' *'

printHeader()

serviceMergedList = printServiceComparisonTableAsHTML(serviceVerMapA, serviceVerMapB)

if statusA == 'First':
	printLine("<p>*The first config version of all the active services are used as the cluster was built after %s" % datetime.datetime.strptime(olderConfigDate, '%Y-%m-%d@%H:%M').strftime('%a, %d %b %Y %I:%M %p'))

configDataA = getAllHistoricalConfigs(baseUrlA, usernameA, passwordA, clusterA, serviceVerMapA)
configDataB = getAllHistoricalConfigs(baseUrlA, usernameA, passwordA, clusterA, serviceVerMapB)

defaultCGDataA, otherCGsDataA = splitConfigGroups(configDataA)
defaultCGDataB, otherCGsDataB = splitConfigGroups(configDataB)

printLine('<h1></br>Service: Config Type - Comparison</h1>')

printLine("<p>Note:</br>The comparison is done only for the 'Default' Config Group.")
if len(otherCGsDataA) > 0 or len(otherCGsDataB) > 0:
	printLine('</br><a href=#%s>Click here to jump to Custom Config Groups listing section</a>' % 'CustomConfigGroups')
printLine('</p>')

printConfigTypeComparisonTablesAsHTML(serviceMergedList, defaultCGDataA, defaultCGDataB)

sortedList = getSortedConfigGroupsList(otherCGsDataA, otherCGsDataB, defaultCGDataA, defaultCGDataB)

printOtherConfigGroupsTablesAsHTML(sortedList)

printFooter()

sys.stdout.write("The comparison output has been written to the file '%s'\n\n" % outFilename)

