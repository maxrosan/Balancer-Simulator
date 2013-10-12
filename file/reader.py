
import os, io, sys

class Reader:

	folder    = ""
	part      = 0
	line      = None
	fd        = None
	num_lines = 0

	def __init__(self, folder, part):
		self.folder = folder
		self.part = part - 1
	
	def name_format(self, part):
		num_str = str(part)
		fn = self.folder + "/part-" + ("0" * (5 - len(num_str))) + num_str + "-of-00500.csv"
		return fn
	
	def has_next(self):
		fn = self.name_format(self.part + 1)
		return os.path.exists(fn)		

	def open_next(self):
		self.part = self.part + 1
		self.fd = io.open(self.name_format(self.part), 'r+')

		print "Arquivo " + str(self.part) + " do task usage"

	def dect_eof(self):
		return (self.line == None)

	def read_next_line(self):
		if self.fd == None:
			self.line = None
			return

		ln = self.fd.readline()
		if len(ln) < 1 or (not ln.endswith("\n")):
			self.line = None
		else:
			self.line = ln.split(',',18)

		self.num_lines = self.num_lines + 1

	# returns true provided that other models must be read
	def verify_model(self, condition, model):
		return False

	def get_model(self):
		return None

	def read_until(self, condition, callback, arg): # callback(model, arg)

		keep_going = True

		while keep_going:

			if self.line == None:
				self.read_next_line()

			if self.dect_eof():
				if self.has_next():
					self.open_next()
				else:
					keep_going = False
			else:

				model = self.get_model()

				if self.verify_model(condition, model):
					callback(model, arg)
					self.line = None				
				else:
					keep_going = False
	
		return True