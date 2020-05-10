from django.db import models

class Category(models.Model):
	class Meta:
		ordering = ['name']

	category_id = models.IntegerField(default=0, primary_key=True)
	name = models.CharField(max_length=50)

class Tracker(models.Model):
	class Meta:
		ordering = ['title']
	
	tracker_id = models.CharField(max_length=50, primary_key=True)
	title = models.CharField(max_length=50)

class SearchEvent(models.Model):
	created_on = models.DateTimeField(auto_now_add=True)
	request = models.CharField(max_length=800)

	def set_request(self, x):
		self.request = json.dumps(x)

	def get_request(self):
		return json.loads(self.request)

class SearchRecord(models.Model):
	id = models.IntegerField(default=0, primary_key=True)
	age = models.DurationField(null=True)
	tracker_info = models.ForeignKey(Tracker, on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=200)
	size = models.BigIntegerField(default=0)
	category_info = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
	seeds = models.IntegerField(default=0)
	leechers = models.IntegerField(default=0)
	magnet = models.CharField(max_length=800)
	desc_url = models.CharField(max_length=800)
	search_event = models.ForeignKey(SearchEvent, db_column='search_event', on_delete=models.CASCADE, null=True)
