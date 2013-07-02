
import prediction.Prediction
import numpypy as numpy

class AveragePrediction(prediction.Prediction.Prediction):
	
	def __init__(self, lst_len):
		prediction.Prediction.Prediction.__init__(self)

		self.lst_len = lst_len

	def calculate_prediction_for_new_task(self, task):
		#self.calculate_prediction(task)

		task.avg_pred = []
		task.age_pred = 0
		task.last_max = (0, 0)

		task.CPU_usage = task.CPU_usage_real
		task.mem_usage = task.mem_usage_real

	def calculate_prediction(self, task, new_task):

		pred = task.avg_pred
		task.age_pred = task.age_pred + 1

#		cpuv = 1.
#		memv = 1. 

#		if len(pred) > 0:
			
#			cpuv = new_task.CPU_usage / (task.CPU_usage if task.CPU_usage > 0. else 1.)
#			memv = new_task.mem_usage / (task.mem_usage if task.mem_usage > 0. else 1.)

		cpuv = new_task.CPU_usage_real
		memv = new_task.mem_usage_real

		pred.append((cpuv, memv))
	
		if len(pred) > self.lst_len:
			pred.pop(0)

		if (task.age_pred % self.lst_len) == 0:
			cpua = max([cpu for (cpu, _) in pred])
			mema = max([mem for (_, mem) in pred])

			self.last_max = (cpua, mema)

			new_task.CPU_usage = cpua
			new_task.mem_usage = mema
		elif task.age_pred > self.lst_len:
			(new_task.CPU_usage, new_task.mem_usage) = task.last_max
		else:
			new_task.CPU_usage = new_task.CPU_usage_real
			new_task.mem_usage = new_task.mem_usage_real
