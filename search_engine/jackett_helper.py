import json
import os
import sys
import xml.etree.ElementTree
from urllib.parse import urlencode, unquote
from urllib import request as urllib_request
from http.cookiejar import CookieJar
import pytz
from datetime import datetime, timedelta
from . import models

CONFIG_FILE = 'jackett.json'
CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), CONFIG_FILE)
__CONFIG_DATA = {
	'api_key': 'YOUR_API_KEY_HERE',  # jackett api
	'url': 'http://127.0.0.1:9117',  # jackett url
}
CONFIG_DATA = {}

def _get_response(query):
	response = None
	try:
		# we can't use helpers.retrieve_url because of redirects
		# we need the cookie processor to handle redirects
		opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(CookieJar()))
		response = opener.open(query).read().decode('utf-8')
	except urllib_request.HTTPError as e:
		# if the page returns a magnet redirect, used in download_torrent
		if e.code == 302:
			response = e.url
	except Exception:
		pass
	return response

def load_configuration():
	global CONFIG_PATH, __CONFIG_DATA, CONFIG_DATA

	if CONFIG_DATA:
		return

	try:
		# try to load user data from file
		with open(CONFIG_PATH) as f:
			CONFIG_DATA = json.load(f)
	except ValueError:
		# if file exists but it's malformed we load add a flag
		__CONFIG_DATA['malformed'] = True
	except Exception:
        # if file doesn't exist, we create it
		with open(CONFIG_PATH, 'w') as f:
			f.write(json.dumps(__CONFIG_DATA, indent=4, sort_keys=True))
	else:
		CONFIG_DATA['url'] = CONFIG_DATA['url'].rstrip('/')

	# do some checks
	if not set(['api_key', 'url']).issubset(set(CONFIG_DATA.keys())) or CONFIG_DATA['api_key'] == "YOUR_API_KEY_HERE":
		CONFIG_DATA['malformed'] = True

def get_configuration():
	load_configuration()
	return CONFIG_DATA

def validate_config():
	load_configuration()
	if 'malformed' in CONFIG_DATA:
		return False
	
	return True
	
def get_categories(tracker='all'):
	if not validate_config():
		return {}
		
	params = {'apikey': CONFIG_DATA['api_key'], 't': 'caps'}
	jackett_url = f"{CONFIG_DATA['url']}/api/v2.0/indexers/{tracker}/results/torznab/api?{urlencode(params)}"
	response = _get_response(jackett_url)
	
	if not response:
		return {}
	
	response_xml = xml.etree.ElementTree.fromstring(response)

	cats = {} # {0: 'All'}
	cats.update({cat.get('id'): cat.get('name') for cat in response_xml.iter('category')})
	
	return cats
	
def get_trackers(configured=True):
	if not validate_config():
		return []
		
	params = {'apikey': CONFIG_DATA['api_key'], 't': 'indexers', 'configured': configured}
	jackett_url = f"{CONFIG_DATA['url']}/api/v2.0/indexers/all/results/torznab/api?{urlencode(params)}"
	response = _get_response(jackett_url)

	if not response:
		return []
	
	response_xml = xml.etree.ElementTree.fromstring(response)
	
	# traks = {'all': 'All'}
	# traks.update({trak.get('id'):trak.find('title').text for trak in response_xml.iter('indexer')})

	return {trak.get('id'):trak.find('title').text for trak in response_xml.iter('indexer')}
	
def search(request):
	if not validate_config():
		return

	q =  request.GET['q']
	tracker = request.GET['tracker']
	cat = request.GET.getlist('cat')
	limit = request.GET['limit']

	request = dict(request.GET)
	if request.get('cached'):
		del request['cached']
	se = models.SearchEvent(request=request)

	params = {'apikey': CONFIG_DATA['api_key'], 'q': q, 'limit': limit}
	if cat and 'all' not in cat:
		params['cat'] = ','.join(cat)

	jackett_url = f"{CONFIG_DATA['url']}/api/v2.0/indexers/{tracker}/results/torznab/api?{urlencode(params)}"
	response = _get_response(jackett_url)

	if not response:
		return []

	results = []
	response_xml = xml.etree.ElementTree.fromstring(response)
	_xpath_tornzab_attr = './{{http://torznab.com/schemas/2015/feed}}attr[@name="{}"]'
	
	for id, result in enumerate(response_xml.find('channel').findall('item')):
		# Age
		pub_date = result.find('pubDate')
		if pub_date is not None:
			_age = (datetime.utcnow().replace(tzinfo=pytz.utc)
					 - datetime.strptime(pub_date.text, "%a, %d %b %Y %H:%M:%S %z"))
			_age = _age if _age > timedelta(seconds=0) else None
		else:
			_age = None		

		# Tracker
		tracker = result.find('jackettindexer')
		if tracker is not None:
			_tracker_info = models.Tracker.objects.get(pk=tracker.get('id'))
		else:
			_tracker_info = None

		# Name
		title = result.find('title')
		if title is not None:
			_name = title.text
		else:
			continue
  		
		# Size
		size = result.find('size')
		if size is not None:
			_size = int(size.text)
		else:
			continue

		# Category
		category = result.find('category')
		if category is not None:
			_category_info = models.Category.objects.get(pk=int(category.text))
		else:
			_category_info = None

		# Seeds
		seeds = result.find(_xpath_tornzab_attr.format('seeders'))
		_seeds = int(seeds.get('value')) if seeds is not None else -1

		# Leechers
		peers = result.find(_xpath_tornzab_attr.format('peers'))
		_leechers = int(peers.get('value')) - _seeds if peers is not None and _seeds != -1 else -1

		# Magnet
		link = result.find('link')
		if link is not None:
			_magnet = link.text
		else:
			continue

		# Description Page URL
		comments = result.find('comments')
		guid = result.find('guid')
		if comments is not None:
			_desc_url = comments.text
		elif guid is not None:
			_desc_url = guid.text
		else:
			_desc_url = '#'

		results += [{'id': id, 'age': _age, 'tracker_info': _tracker_info, 'name': _name,
			'size': _size, 'category_info': _category_info, 'seeds': _seeds,
			'leechers': _leechers, 'magnet': _magnet, 'desc_url': _desc_url, 'search_event': se}]

	return (results, se)