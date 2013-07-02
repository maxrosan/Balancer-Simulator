
import numpypy as numpy

class AveragePrediction(prediction.Prediction.Prediction):
	
	def __init__(self, lst_len):
		prediction.Prediction.Prediction.__init__(self)

		self.lst_len = lst_len

	def calculate_prediction_for_new_task(self, task):
		self.calculate_prediction(task)

		task.avg_pred = []
		task.age_pred = 0

	def calculate_prediction(self, task):

		pred = task.avg_pred
		task.age_pred = task.age_pred + 1

		if len(pred) > 0:
			
			cpuv = task.CPU_usage / (pred[-1][0] if pred[-1][0] > 0 else 1.)
			memv = task.mem_usage / (pred[-1][1] if pred[-1][1] > 0 else 1.)

			pred.append((cpuv, memv))

		if len(pred) > self.lst_len:
			pred.pop(0)

		cpua = numpy.mean([cpu for (cpu, _) in pred])
		mema = numpy.mean([mem for (_, mem) in pred])

		if (task.age_pred % self.lst_len) == 0:
			task.CPU_usage = task.CPU_usage_real * cpua
			task.mem_usage = task.mem_usage_real * mema
		else:
			task.CPU_usage = task.CPU_usage_real
			task.mem_usage = task.mem_usage_real
