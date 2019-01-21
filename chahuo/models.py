from django.db import models
import datetime
import django.utils.timezone as timezone
# Create your models here.

class StockQueryRecord(models.Model):
	"""docstring for StockQueryRecord"""
	hash_id = models.CharField(unique = True, max_length = 32)
	company = models.CharField(max_length = 100)
	item = models.CharField(max_length = 45)
	spec = models.CharField(max_length = 200, null = True, blank = True)
	q_quantity = models.PositiveSmallIntegerField()
	s_quantity = models.PositiveSmallIntegerField(blank = True, null = True)
	result_status = models.PositiveSmallIntegerField(blank = True, null = True)
	q_time = models.DateTimeField(default = timezone.now)
	r_time = models.DateTimeField(auto_now = True,blank = True, null = True)

	def __str__(self):
		return ','.join([self.hash_id, self.company, self.item, str(self.q_quantity), str(self.q_time), str(self.r_time)])
		