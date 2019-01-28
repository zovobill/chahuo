import unittest, asyncio

class R(object):
	def __init__(self, appname, name, **kwargs):
		self.name = name or 'R'
		self.allin_num = kwargs.get('allin_num', 0)
		self.in_num = kwargs.get('in_num', 0)
		self.in_rs = kwargs.get('in_rs', [])
		self.formula_in = kwargs.get('formula_in', 2)
		self.formula_out = kwargs.get('formula_out', 1)
		self.out_rs = kwargs.get('out_rs', [])
		self.out_num = kwargs.get('out_num', 0)
		self.allout_num = kwargs.get('allout_num', 0)
		self.appname = appname

	def _push_in(self, n, from_inr = None):
		for from_inr in self.in_rs:
			while self.in_num < n:
				from_inr.pop_out(n, self)		
				self.allin_num += n
				self.in_num += n
				print('{}, {},in_rs:{} in_num:{} allin_num:{}'\
					.format(repr(self.appname).rjust(10), self.name.rjust(10),self.in_rs, repr(self.in_num).rjust(10), repr(self.allin_num).rjust(10)))		
				print('{}, {},out_rs:{} out_num:{} allout_num:{}'\
					.format(self.appname.rjust(10), self.name.rjust(10), self.out_rs, repr(self.out_num).rjust(10), repr(self.allout_num).rjust(10)))

	def pop_out(self, n, to_outr):
		if to_outr in self.out_rs:
			while self.out_num < n:
				self.produce(n)
			self.out_num -= n
			self.allout_num += n
			print('{}, {},in_rs:{} in_num:{} allin_num:{}'\
				.format(repr(self.appname).rjust(10), self.name.rjust(10),self.in_rs, repr(self.in_num).rjust(10), repr(self.allin_num).rjust(10)))		
			print('{}, {},out_rs:{} out_num:{} allout_num:{}'\
				.format(self.appname.rjust(10), self.name.rjust(10), self.out_rs, repr(self.out_num).rjust(10), repr(self.allout_num).rjust(10)))

	def produce(self, n):
		m = self.formula_in/self.formula_out*n
		self._push_in(m)
		self.in_num -= n
		self.out_num += n

	def __str__(self):
		return self.appname+'-'+self.name

class M(object):
	"""docstring for M"""
	def __init__(self, name, ptimer):
		self.name = name
		self.ptimer = ptimer
		self.rio = 3

	async def task(self):
		i = 0
		while i < 20:
			for t in self.ptimer:
				print("M:{}".format(self.name))
				await asyncio.sleep(t)
				self.pr.produce(t*self.rio)
			i += 1
			
	def create(self):
		self.pr = R(self.name, 'produce')
		self.outr = R(self.name, 'outresource', allin_num = 0, formula_in = 1)
		self.inr = R(self.name, 'inresource', allin_num = 200, in_num = 200)
		self.inr.out_rs.append(self.pr)
		self.pr.in_rs.append(self.inr)
		self.pr.out_rs.append(self.outr)	


class TestAsyncio(unittest.TestCase):
	
	def setUp(self):
		pass

	def test_asyncio(self):
		self.apprun()
		loop = asyncio.get_event_loop()
		tasks = [self.app.task(), self.app2.task()]
		loop.run_until_complete(asyncio.wait(tasks))
		loop.close()

	def apprun(self):
		print("start")
		self.app = M('app1', [2,1,2])
		self.app.create()

		self.app2 = M('app2', [1,2,1])
		self.app2.rio = 20
		self.app2.create()
		self.app.outr.out_rs.append(self.app2.inr)
		self.app2.inr.in_rs.append(self.app.outr)

	def tearDown(self):
		pass

if __name__ == '__main__':
	unittest.main()