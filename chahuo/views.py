from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import JsonResponse
from .models import StockQueryRecord
import logging, json, datetime, hashlib, time

logger = logging.getLogger(__name__)
DEFAULT_NUM = 30
TIME_STEP = 0.3
MAX_ROUND = 10
DROP_CHARS = "*%~!@'#&?"
COMPANY_SNS = {'dongnam':'dongnam',}
model = StockQueryRecord

def chahuo(request):
	keyword = request.GET.get('q', '').upper()
	keyword = ''.join(filter(lambda c: c not in DROP_CHARS, keyword))
	company = request.GET.get('c', None)
	# print('company=', company, 'keyword = ', keyword)
	if not company or keyword == '': 
		return redirect('index')
	n = request.GET.get('n', '0')
	num = parseInt(n)
	hash_str = '_'.join([company, keyword, str(datetime.datetime.now())])
	hash_id = hashlib.md5(bytes(hash_str, encoding = 'utf8')).hexdigest()
	# print('hash_id:',hash_id,' company=', company, ' keyword = ', keyword, ' n = ', num)
	record = StockQueryRecord(company = company, item = keyword, q_quantity = num, hash_id = hash_id)
	# print('record in chahuo: ', str(record))
	try:
		record.save()
	except:
		print('some error raised with saveing to db in chahuo function')
		return HttpResponse('some error raised in getting or saving with db', content_type='text/plain')
	n = 0
	while n < MAX_ROUND:
		time.sleep(TIME_STEP)
		result = model.objects.get(hash_id = record.hash_id)
		# print('result: ', result)
		if result:
			status = result.result_status
			print('item:{} q_quantity:{} status:{}'.format(result.item, result.q_quantity, result.result_status))
			if status == 0:
				return HttpResponse('<span class="label label-default">无货或无此货号，请检查输入货号</span>', content_type="text/plain")
			elif status == 1:
				return HttpResponse('<span class="label label-warning">缺货，{} 库存小于 {} 卷</span>'.format(keyword, num), content_type="text/plain")
			elif status >= 2:
				return HttpResponse('<span class="label label-success">有货，{} 库存大于 {} 卷</span>'.format(keyword, num), content_type="text/plain")
		n += 1
	return HttpResponse('<span class="label label-default">查询超时或出错，请电话联系东南墙纸</span>', content_type="text/plain")

def index(request):
	if len(request.GET) == 0:
		return render(request, 'index.html')
	else:
		return chahuo(request)

def parseInt(nstr):
	try:
		num = filter(lambda c:'0'<= c <= '9', nstr)
		num = ''.join(num)
		print(num)
		num = int(num)
		if num == 0: num = DEFAULT_NUM
	except:
		num = DEFAULT_NUM
	# print('parseInt = ', num)
	return num

@csrf_exempt
def chahuo_list(request):
	company = request.POST.get('c', None)
	if company is None: 
		return redirect('index')
	com_sn = request.POST.get('sn', None)
	if com_sn is None  or com_sn != COMPANY_SNS.get(company, ''):
		return redirect('index')

	qset = model.objects.filter(company__iexact = company, result_status__iexact = None)
	# print('qset:', qset)
	data = serializers.serialize("json", qset)
	# return HttpResponse(json.dumps(data))
	return HttpResponse(data, content_type="application/json")

@csrf_exempt
def chahuo_result(request):
	result = request.POST
	hash_id = result.get('hash_id', None)
	status = result.get('result_status', None)
	if hash_id is None or status is None:
		return redirect('index')
	try:
		record = model.objects.get(hash_id = hash_id)
		# print('record:',record)
		if record is None:
			return JsonResponse({'status': False, 'message':'db has no record like it.'}, content_type="text/plain")

		record.result_status = status
		record.save()
		print('hash_id:{} item:{} record has been got and been saved.'.format(record.hash_id, record.item))
		return JsonResponse({'status': True, 'message':'reslut has been got and saved to db'}, content_type="text/plain")
	except:
		print('some error raised in db')
		return JsonResponse({'status': False, 'message':'some error raised in getting result or saving to db'}, content_type="text/plain")




