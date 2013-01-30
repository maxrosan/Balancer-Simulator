

class UsageClass:

	def __init__(self, cpu_limit, mem_limit):
		self.free_cpu_usage = cpu_limit
		self.free_mem_usage = mem_limit
		self.capacity_CPU   = cpu_limit
		self.capacity_mem   = mem_limit

	def inc(self, cpu, mem):
		if self.verify(cpu, mem):
			self.free_cpu_usage = self.free_cpu_usage - cpu
			self.free_mem_usage = self.free_mem_usage - mem
			return True
		return False

	def verify(self, cpu, mem):
		return (self.free_cpu_usage - cpu > 0) and (self.free_mem_usage - mem > 0)

