#!/usr/bin/env python

############################################################################
#
# This is a python script to compare configurations of 2 clusters
# by comparing the latest active configs stored in Ambari Database.
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
import time
import getpass
import collections
import codecs
import argparse
#import pprint

# Increment the version when you make modifications
scriptVersion = '3.0'

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
whitesmoke = '#f5f5f5'
nicered = '#DC9696'
nicegreen = '#8CCBA3'
niceblue = '#137eb8'
bestblue = '#15a7dc'
headergreen = '#4CAF50'
shadowcolor = '#666' # '#888888'
yellow = 'yellow'

darkgray = '#666'
bluegreen = '#11c1d2'
verylightred = '#f89e90'
lightred = '#d47577'
littlemorered = '#eb5f5d'
anotherred = '#ff8081'
lightgreen = '#8ecd8f'
lightblue = '#90bbff'
verylightblue = '#74c9e2'
textblue = '#1f9dd5'
lightyellow = '#efcc08'
lightorange = '#f8b25d'
verylightorange = '#f8c990'
darkred = '#bd383d'

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

#blue grey
comb1 = '#5a7ba6'
comb2 = '#9caac7'
# pink green
comb1 = '#ffccca'
comb2 = '#d7e4bb'
# another ok one
comb1 = bluegreen
comb2 = lightorange

#bgDummy =  '#edf2df' # '#dae5bf' # '#70cab9' # '#9cb794' # '#d1c4ab'  #'#a9dca8'
#bgDummy = '#7abd9b'
bgDummy = nicegreen # '#379b7c' # nicegreen
#bgDummy = '#a0c3ab'
bgExist = comb1 # '#94c2f3' # '#ffd2d1' # '#f3a824' # '#dd9a92' #'#2ea4cb'  # '#30a2c8'
bgDifferent = '#30a2c8'
#bgExist = '#f9c0b9'
bgDummy = nicegreen
bgExist = verylightred
bgExist = '#f57a5f'
bgDummy = '#90ce93'
bgExist = '#f67b62'
bgDummy = '#90cc92'
bgExist = '#f89e90'
bgDummy = '#acdab6'
bgExist = '#f9c2ac'
bgDummy = lightgreen # '#c5e5dd'
bgExist = '#f9a562'
bgDummy = '#90cc92' # lightgreen 
bgDummy = '#DCDCDC' # Selection Grey  
selectionblue = '#7dd4f6'

bgHighlight = verylightred
bgHeader = headergreen
bgAlternate = whitesmoke

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
	printLine('tr.topborder {')
	printLine('    border-top: 1px solid #ddd;')
	printLine('    border-bottom: 0px solid #ddd;')
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
	#printLine('    border-bottom: 1px solid #ddd;')
	printLine('}')
	printLine('td.dummy {')
	printLine('    background-color: %s;' % bgDummy)
	#printLine('    border-bottom: 1px solid #ddd;')
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
	printLine('    background-color: %s;' % yellow)
	printLine('}')

	printLine('tr:nth-child(even) {')
	printLine('    background-color: %s' % bgAlternate)
	printLine('}')
	printLine('tr.alternate:nth-child(even) {')
	printLine('    background-color: %s' % bgAlternate)
	printLine('}')
	printLine('tr.topborder:nth-child(even) {')
	printLine('    background-color: %s' % bgAlternate)
	printLine('}')
	printLine('</style>')
 
def runUsingPyCurl(url, username, password, suppressError):
	c = pycurl.Curl()
	c.setopt(pycurl.URL, url)
	s = cStringIO.StringIO()
	c.setopt(c.WRITEFUNCTION, s.write)
	c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
	c.setopt(pycurl.USERPWD, (username + ':' + password))
	c.perform()
	if not suppressError and c.getinfo(pycurl.HTTP_CODE) != 200:
		errorString = "Error executing the URL: '%s' for the username: '%s'\n" % (url, username)
		sys.stderr.write(errorString)
		sys.exit(2)
	return s.getvalue()

def runUsingRequests(url, username, password, suppressError):
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
	if not suppressError and r.status_code != 200:
		errorString = "Error executing the URL: '%s' for the username: '%s'\n" % (url, username)
		sys.stderr.write(errorString)
		sys.exit(2)
	return r.text

def getURLData(url, username, password, suppressError = False):
	# print ">>> " + url   # Ajmal
	if module == 'requests':
		return runUsingRequests(url, username, password, suppressError)
	elif module == 'pycurl':
		return runUsingPyCurl(url, username, password, suppressError)
		
def printHeader():
	headingAndTitle = 'Cluster comparison - %s and %s' % (clusterAHeading, clusterBHeading)

	printLine('<!DOCTYPE html>')
	printLine('<html>')

	printLine('<head>')
	printLine('<meta charset="utf-8">')
	printLine('<title>%s</title>' % headingAndTitle)
	printStyleSheet()
	printLine('</head>')

	printLine('<body>')
	printLine('<div class=pagePadding>')
	printLine('<h1></br>%s</h1>' % headingAndTitle)
	printLine('<p>Generated on : %s</p>' % time.strftime("%a, %d %b %Y %I:%M %p"))

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
			newLine += blankSpace
		else:
			newLine += line[x]

	if started:
		newLine += '</span>'
	newLine += remaining
	return newLine

def calcDiffData(left, right):
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
		else:
			listProperties[prop] = listProperties[prop].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('{','&#123;').replace('}','&#125;')
	return listProperties


def getAllLatestConfigs(base_url, username, password, cluster, services):
	url = '%s/clusters/%s' % (base_url, cluster)

	active_config_group_ids = []
	active_config_groups_url = url + '/config_groups'
	active_config_groups_data = json.loads(getURLData(active_config_groups_url, username, password))['items']
	for acg in active_config_groups_data:
		active_config_group_ids.append(acg['ConfigGroup']['id'])

	dictServices = {}
	config_versions_url = url + '/configurations/service_config_versions?service_name.in(%s)&is_current=true'
	for service in services:
		typeItems = json.loads(getURLData(config_versions_url % (service), username, password))['items']
		dictGroups = {}
		for y in typeItems:
			listTypes = {}
			if y['group_id'] == -1:
				group_name = 'Default'
			elif y['group_id'] in active_config_group_ids:
				group_name = y['group_name']
			else:
				continue
			for z in y['configurations']:
				listTypes[z['type']] = getMaskedPropertyValues(z['properties'])

			groupData = {}
                        groupData['Configurations'] = listTypes
                        groupData['user'] = y['user']
                        #groupData['modified_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(int(y['createtime'])/1000))
                        groupData['modified_time'] = time.strftime('%d %b %Y %H:%M', time.localtime(int(y['createtime'])/1000))
                        groupData['config_version'] = 'V' + str(y['service_config_version'])
                        groupData['config_version_note'] = str(y['service_config_version_note'])

                        dictGroups[group_name] = groupData
		dictServices[service] = dictGroups

	return dictServices

def printFooter():
	printLine('</div>')
	printLine('<body>')
	printLine('<html>')

def getStackDisplayVersion(base_url, username, password, cluster):
	stack_name = stack_version = ''
	stack_versions_items = json.loads(getURLData('%s/clusters/%s/stack_versions' % (base_url, cluster), username, password, True))['items']
	for sv_item in stack_versions_items:
		version_id = str(sv_item['ClusterStackVersions']['id'])
		repo_version = str(sv_item['ClusterStackVersions']['repository_version'])
		rv_state = json.loads(getURLData('%s/clusters/%s/stack_versions/%s' % (base_url, cluster, version_id), username, password, True))['ClusterStackVersions']['state']
		if str(rv_state) == 'CURRENT':
			stack_url = '%s/clusters/%s/stack_versions/%s/repository_versions/%s' % (base_url, cluster, version_id, repo_version)
			current_stack = json.loads(getURLData(stack_url, username, password, True))
			stack_name = current_stack['RepositoryVersions']['stack_name']
			stack_version = current_stack['RepositoryVersions']['repository_version']
			break
	
	return stack_name, stack_version

def getServiceVerMap(base_url, username, password, cluster):
	services = []
	items = json.loads(getURLData('%s/clusters/%s/services' % (base_url, cluster), username, password))['items']
	for item in items:
		services.append(str(item['ServiceInfo']['service_name']))

	service_details = json.loads(getURLData('%s/clusters/%s' % (base_url, cluster), username, password))['Clusters']['desired_service_config_versions']

	serviceVersionMap = {}
	for service in services:
		try:
			stack, stack_version = str(service_details[service][0]['stack_id']).split('-',2)
			service_url = '%s/stacks/%s/versions/%s/services/%s' % (base_url, stack, stack_version, service)
			service_version = json.loads(getURLData(service_url, username, password))['StackServices']['service_version']
		except:
			serviceVersionMap[service] = 'Unknown'
		else:
			serviceVersionMap[service] = service_version
	return serviceVersionMap

def getGroupsIDandLabel(configData, service):
	grps = []
	if service in configData:
		grps.append('Default')
		for grp in sorted(configData[service].keys()):
			if grp != 'Default':
				grps.append(grp)

	config_group_details = []
	for grp in grps:
		details = {}
		if grp != 'Default':
			details['group_name'] = '<a href=#%s>%s</a>' % ('CustomConfigGroups', str(grp))
		else:
			details['group_name'] = 'Default'
		details['modified_time'] = configData[service][grp]['modified_time']
		details['user'] = configData[service][grp]['user']
		details['config_version'] = configData[service][grp]['config_version']

		config_group_details.append(details)

	return config_group_details

def printActiveStackAndVersion(stack_nameA, stack_versionA, stack_nameB, stack_versionB):
	printLine('<h1></br>Current Stack and Versions</h1>')
	printLine('<table>')
	printLine('<tr>')
	printLine('<th %s>%s</th>' % ('width="24%"', 'Stack'))
	printLine('<th %s>%s</th>' % ('', clusterAHeading))
	printLine('<th %s>%s</th>' % ('', clusterBHeading))
	printLine('</tr>')
	printLine('<tr>')
	printLine('<td>%s</td>' % (stack_nameA))
	printLine('<td>%s</td>' % (stack_versionA))
	printLine('<td>%s</td>' % (stack_versionB))
	printLine('</tr>')
	printLine('</table>')

def printServiceComparisonTableAsHTML(clusterA, serviceVerMapA, configDataA, clusterB, serviceVerMapB, configDataB):
	serviceMergedList = sorted(set(serviceVerMapA.keys() + serviceVerMapB.keys()))
	printLine('</br>')
	printLine('<table>')
	printLine('<tr>')
	printLine('<th %s>%s</th>' % ('width="24%"', 'Service'))
	printLine('<th %s>%s</th>' % ('', clusterAHeading))
	printLine('<th %s>%s</th>' % ('', clusterBHeading))
	printLine('</tr>')
	for service in serviceMergedList:
		printLine('<tr class=alternate>')
		printLine('<td>%s</td>' % (service))
		if service in serviceVerMapA.keys():
			printLine('<td>%s</td>' % (serviceVerMapA[service]))
		else:
			printLine('<td>%s</td>' % ('Not installed'))
		if service in serviceVerMapB.keys():
			printLine('<td>%s</td>' % (serviceVerMapB[service]))
		else:
			printLine('<td>%s</td>' % ('Not installed'))
		printLine('</tr>')
	printLine('</table>')

	printLine('<h1></br>Service: Config Groups - Details</h1>')
	printLine('<table>')
	printLine('<tr>')
	printLine('<th %s %s>%s</th>' % ('width="14%"', 'rowspan="2"', 'Service'))
	printLine('<th %s %s>%s</th>' % ('', 'colspan="4"', clusterAHeading))
	printLine('<th %s %s>%s</th>' % ('', 'colspan="4"', clusterBHeading))
	printLine('</tr>')
	printLine('<tr>')
	printLine('<th %s>%s</th>' % ('', 'Config Groups'))
	printLine('<th %s>%s</th>' % ('', 'Version'))
	printLine('<th %s>%s</th>' % ('', 'Modified Time'))
	printLine('<th %s>%s</th>' % ('', 'Modified By'))
	printLine('<th %s>%s</th>' % ('', 'Config Groups'))
	printLine('<th %s>%s</th>' % ('', 'Version'))
	printLine('<th %s>%s</th>' % ('', 'Modified Time'))
	printLine('<th %s>%s</th>' % ('', 'Modified By'))
	printLine('</tr>')

	for service in serviceMergedList:
		config_group_list_A = getGroupsIDandLabel(configDataA, service)
		config_group_list_B = getGroupsIDandLabel(configDataB, service)
		number_rows = max(len(config_group_list_A), len(config_group_list_B))

		for i in range(number_rows):
			if i == 0:
				printLine('<tr class=topborder>')
				printLine('<td %s><a %s>%s</a></td>' % ('rowspan="%s"' % number_rows, 'href="#%s"' % service, service))
			else:
				printLine('<tr class=alternate>')
			if service in serviceVerMapA.keys() and i < len(config_group_list_A):
				colA1 = config_group_list_A[i]['group_name']
				colA2 = config_group_list_A[i]['config_version']
				colA3 = config_group_list_A[0]['modified_time']
				colA4 = config_group_list_A[i]['user']
			else:
				colA1 = colA2 = colA3 = colA4 = '-'
			if service in serviceVerMapB.keys() and i < len(config_group_list_B):
				colB1 = config_group_list_B[i]['group_name']
				colB2 = config_group_list_B[i]['config_version']
				colB3 = config_group_list_B[i]['modified_time']
				colB4 = config_group_list_B[i]['user']
			else:
				colB1 = colB2 = colB3 = colB4 = '-'
			
			printLine('<td>%s</td>' % (colA1))
			printLine('<td>%s</td>' % (colA2))
			printLine('<td>%s</td>' % (colA3))
			printLine('<td>%s</td>' % (colA4))

			printLine('<td>%s</td>' % (colB1))
			printLine('<td>%s</td>' % (colB2))
			printLine('<td>%s</td>' % (colB3))
			printLine('<td>%s</td>' % (colB4))
			printLine('</tr>')
	printLine('</table>')
	return serviceMergedList

def printServiceConfigVersionDetails(service, configDataA, configDataB):
	printLine('<table>')
       	printLine('<tr>')
       	printLine('<th %s>%s</th>' % ('width="24%"', 'Details'))
       	printLine('<th %s>%s</th>' % ('', clusterAHeading))
       	printLine('<th %s>%s</th>' % ('', clusterBHeading))
       	printLine('</tr>')
       	printLine('<tr>')
       	printLine('<td %s>%s</td>' % ('', 'Last modified time'))
	if service in configDataA.keys():
       		printLine('<td %s>%s</td>' % ('', configDataA[service]['Default']['modified_time']))
	else:
		printLine('<td %s>%s</td>' % ('', '-'))
	if service in configDataB.keys():
       		printLine('<td %s>%s</td>' % ('', configDataB[service]['Default']['modified_time']))
	else:
		printLine('<td %s>%s</td>' % ('', '-'))
       	printLine('</tr>')
       	printLine('<tr>')
       	printLine('<td %s>%s</td>' % ('', 'Last modified by'))
	if service in configDataA.keys():
       		printLine('<td %s>%s</td>' % ('', configDataA[service]['Default']['user']))
	else:
		printLine('<td %s>%s</td>' % ('', '-'))
	if service in configDataB.keys():
       		printLine('<td %s>%s</td>' % ('', configDataB[service]['Default']['user']))
	else:
		printLine('<td %s>%s</td>' % ('', '-'))
       	printLine('</tr>')
       	printLine('<tr>')
       	printLine('<td %s>%s</td>' % ('', 'Service config version note'))
	if service in configDataA.keys():
       		printLine('<td %s>%s</td>' % ('', configDataA[service]['Default']['config_version_note']))
	else:
		printLine('<td %s>%s</td>' % ('', '-'))
	if service in configDataB.keys():
       		printLine('<td %s>%s</td>' % ('', configDataB[service]['Default']['config_version_note']))
	else:
		printLine('<td %s>%s</td>' % ('', '-'))
       	printLine('</tr>')
	printLine('</table>')


def printConfigTypeComparisonTablesAsHTML(serviceMergedList, configDataA, configDataB):
	service_count = 1
	for service in serviceMergedList:
		printLine('<h2 %s></br>%d. %s Service Configurations</h2>' % ('id=%s' % service, service_count, service))

		# Ajmal testing
		printServiceConfigVersionDetails(service, configDataA, configDataB)

		if service in configDataA.keys():
			listTypesA = configDataA[service]['Default']['Configurations']
		else:
			listTypesA = {}
		if service in configDataB.keys():
			listTypesB = configDataB[service]['Default']['Configurations']
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
	printLine('<h2 %s></br>Custom Config Groups</h2>' % ('id=%s' % 'CustomConfigGroups'))
	service_count = 1
	for config_type in sorted(newList.keys()):
		printLine('<h3></br>%d. %s</h3>' % (service_count, config_type))
		firstRow = True
		printLine('<table>')
        	printLine('<tr>')
        	printLine('<th %s>%s</th>' % ('width="25%"', 'Cluster Name'))
        	printLine('<th %s>%s</th>' % ('width="25%"', 'Config Group'))
        	printLine('<th %s>%s</th>' % ('width="25%"', 'Property'))
        	printLine('<th %s>%s</th>' % ('width="25%"', 'Value'))
        	printLine('</tr>')
		for prop, dummyC, dummyCG, cluster, configgroup, value in newList[config_type]:
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
			for type in otherCGsDataA[service][group]['Configurations']:
				key = service + ' : ' + type
				if key not in serviceTypeList:
					serviceTypeList[key] = []
				for prop in otherCGsDataA[service][group]['Configurations'][type]:
					serviceTypeList[key].append((prop, 'A', 1, clusterAHeading, group, otherCGsDataA[service][group]['Configurations'][type][prop]))
					if prop in defaultCGDataA[service]['Default']['Configurations'][type]:
						serviceTypeList[key].append((prop, 'A', 0, clusterAHeading, 'Default', defaultCGDataA[service]['Default']['Configurations'][type][prop]))
					else:
						serviceTypeList[key].append((prop, 'A', 0, clusterAHeading, 'Default', strMissingConfiguration))

	for service in otherCGsDataB:
		for group in otherCGsDataB[service]:
			for type in otherCGsDataB[service][group]['Configurations']:
				key = service + ' : ' + type
				if key not in serviceTypeList:
					serviceTypeList[key] = []
				for prop in otherCGsDataB[service][group]['Configurations'][type]:
					serviceTypeList[key].append((prop, 'B', 1, clusterBHeading, group, otherCGsDataB[service][group]['Configurations'][type][prop]))
					if prop in defaultCGDataB[service]['Default']['Configurations'][type]:
						serviceTypeList[key].append((prop, 'B', 0, clusterBHeading, 'Default', defaultCGDataB[service]['Default']['Configurations'][type][prop]))
					else:
						serviceTypeList[key].append((prop, 'B', 0, clusterBHeading, 'Default', strMissingConfiguration))

	sortedServiceTypeList = {}
	for serviceType in serviceTypeList:
		sortedServiceTypeList[serviceType] = sorted(serviceTypeList[serviceType])

	return sortedServiceTypeList

def GetBaseURLs(protocolA, protocolB, ambariServerA, ambariServerB, ambariPortA, ambariPortB):
	if (protocolA == 'y'):
		baseUrlA = 'https://%s:%s/api/v1' % (ambariServerA, ambariPortA)
	else:
		baseUrlA = 'http://%s:%s/api/v1' % (ambariServerA, ambariPortA)

	if (protocolB == 'y'):
		baseUrlB = 'https://%s:%s/api/v1' % (ambariServerB, ambariPortB)
	else:
		baseUrlB = 'http://%s:%s/api/v1' % (ambariServerB, ambariPortB)

	return baseUrlA, baseUrlB


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

ambariServerA = ''
ambariServerB = ''
clusterA = ''
clusterB = ''
protocolA = 'n'
protocolB = 'n'

description = 'Version %s. \nScript to compare configs from 2 clusters. NOTE: If the script takes too long and times out, then try using the IP Addresses of Ambari Servers instead of hostnames.' % scriptVersion

parser = argparse.ArgumentParser(description=description)

#parser._action_groups.pop()
required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-a', '--ambari_hosts', nargs = 2, help='IPs/Hostnames of first and second Ambari Server', required=True, metavar=('AMBARI_HOST_1','AMBARI_HOST_2'))
parser.add_argument('-u', '--usernames', nargs = 2, help='Usernames for first and second Ambari UI. Default: admin', default=['admin', 'admin'], metavar=('USERNAME_1','USERNAME_2'))
parser.add_argument('-p', '--ports', nargs = 2, help='Port numbers for first and second Ambari Servers. Default: 8080', default=['8080', '8080'], metavar=('PORT_1','PORT_2'))
parser.add_argument('-c', '--clusternames', nargs = 2, help='Names of the first and second cluster. Default: First available cluster names from  each Ambari', metavar=('CLUSTER_1','CLUSTER_2'))
parser.add_argument('-s', '--ssl_flags', nargs = 2, help='Whether SSL is enabled for first and second Ambari URLs (y or n). Default: n', default=['n', 'n'], metavar=('SSL_ENABLED_FLAG_1','SSL_ENABLED_FLAG_2'))

args = parser.parse_args()

ambariServerA = args.ambari_hosts[0]
ambariServerB = args.ambari_hosts[1]
usernameA = args.usernames[0]
usernameB = args.usernames[1]
if args.clusternames:
	clusterA = args.clusternames[0]
	clusterB = args.clusternames[1]
ambariPortA = args.ports[0]
ambariPortB = args.ports[1]
protocolA = args.ssl_flags[0].lower()
protocolB = args.ssl_flags[1].lower()

passwordA = getpass.getpass('Ambari password for %s [%s]: ' % (ambariServerA, usernameA))
if not passwordA:
	passwordA = 'admin'

passwordB = getpass.getpass('Ambari password for %s [%s]: ' % (ambariServerB, usernameB))
if not passwordB:
	passwordB = 'admin'

baseUrlA, baseUrlB = GetBaseURLs(protocolA, protocolB, ambariServerA, ambariServerB, ambariPortA, ambariPortB)

# Wraping around str() to convert unicode to str - for using in URL
if not clusterA:
	clusterA = str(getClusterNameAsJSON(baseUrlA, usernameA, passwordA))
if not clusterB:
	clusterB = str(getClusterNameAsJSON(baseUrlB, usernameB, passwordB))

sys.stdout.write('\nParameters:')
sys.stdout.write('\nAmbari1 Host : %s' % ambariServerA)
sys.stdout.write('\nAmbari2 Host : %s' % ambariServerB)
sys.stdout.write('\nUsername1 : %s' % usernameA)
sys.stdout.write('\nUsername2 : %s' % usernameB)
sys.stdout.write('\nPort1  : %s' % ambariPortA)
sys.stdout.write('\nPort2  : %s' % ambariPortB)
sys.stdout.write('\nCluster1 Name  : %s' % clusterA)
sys.stdout.write('\nCluster2 Name  : %s' % clusterB)
sys.stdout.write('\nSSLEnabled1  : %s' % protocolA)
sys.stdout.write('\nSSLEnabled2  : %s' % protocolB)
sys.stdout.write('\n\n')

clusterAHeading = clusterA + ' (Ambari Server: ' + ambariServerA + ')'
clusterBHeading = clusterB + ' (Ambari Server: ' + ambariServerB + ')'

outFilename = '%s-%s.html' % (clusterA, clusterB)
outputFile = codecs.open(outFilename, 'w', 'utf-8')
#outputFile = open(outFilename, 'w')

printHeader()

stack_nameA, stack_versionA = getStackDisplayVersion(baseUrlA, usernameA, passwordA, clusterA)
stack_nameB, stack_versionB = getStackDisplayVersion(baseUrlB, usernameB, passwordB, clusterB)

printActiveStackAndVersion(stack_nameA, stack_versionA, stack_nameB, stack_versionB)

serviceVerMapA = getServiceVerMap(baseUrlA, usernameA, passwordA, clusterA)
serviceVerMapB = getServiceVerMap(baseUrlB, usernameB, passwordB, clusterB)

configDataA = getAllLatestConfigs(baseUrlA, usernameA, passwordA, clusterA, serviceVerMapA.keys())
configDataB = getAllLatestConfigs(baseUrlB, usernameB, passwordB, clusterB, serviceVerMapB.keys())

serviceMergedList = printServiceComparisonTableAsHTML(clusterA, serviceVerMapA, configDataA, clusterB, serviceVerMapB, configDataB)

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

