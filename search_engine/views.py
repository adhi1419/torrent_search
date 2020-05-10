from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe

import xml.etree.ElementTree
from . import jackett_helper
from . import models
import json
import math
from datetime import datetime, timedelta
import pytz


# Helper Functions
def __hyperlink(link, text):
	return f'<a href="{link}">{text}</a>'

def __magnet(link):
	return f'<a href="{link}"><span class="fas fa-magnet"></span></a>'

def __search_record_result(sr):
	return [sr.id, sr.age.days if sr.age else 'Unknown', sr.tracker_info.title,
			 __hyperlink(sr.desc_url, sr.name), sr.size,
			sr.category_info.name, sr.seeds, sr.leechers, __magnet(sr.magnet)]

# View Functions
# /
def index(request):
	context = {'trackers': models.Tracker.objects.all(), 
				'cats': models.Category.objects.all()}
	
	return render(request, 'search_engine/index.html', context)

# /results/
def results(request):
	field_labels = ['ID', 'Age', 'Tracker', 'Title', 'Size', 
					'Category', 'Seeds', 'Leechers', 'Magnet']
	context = {'field_labels': field_labels, 
			'request': mark_safe(json.dumps(request.GET)),
			'query': request.GET['q']}

	return render(request, 'search_engine/results.html', context)

# /fetch_results/
def fetch_results(request):
	# Show Cached?
	_cached = request.GET.get('cached') == 'on'
	_request = dict(request.GET)
	if request.GET.get('cached'):
		del _request['cached']

	# Delete all old search events
	models.SearchEvent.objects.filter(created_on__lte=datetime.utcnow().replace(tzinfo=pytz.utc)
		- timedelta(days=1)).delete()
	
	_se = models.SearchEvent.objects.filter(request=_request).order_by('-created_on').first()
	if _se and _cached:
		context = {'results': [__search_record_result(x) for x in _se.searchrecord_set.all()]}
		return JsonResponse(context)

	search_results, se = jackett_helper.search(request)

	se.save()
	# models.SearchRecord.objects.all().delete()
	for _res in search_results:
		_sr = models.SearchRecord(**_res)
		# _sr.full_clean()
		_sr.save()

	context = {'results': [__search_record_result(x) for x in  se.searchrecord_set.all()]}

	return JsonResponse(context)

# /refresh/
@csrf_exempt
def refresh(request):
	# Clear existing trackers and re-populate
	models.Tracker.objects.all().delete()
	trackers = jackett_helper.get_trackers()
	for tracker_id, title in trackers.items():
		models.Tracker(tracker_id=tracker_id, title=title).save()

	# Clear existing Categories and re-populate
	models.Category.objects.all().delete()
	cats = jackett_helper.get_categories()
	for category_id, name in cats.items():
		models.Category(category_id=category_id, name=name).save()

	return HttpResponse('')
