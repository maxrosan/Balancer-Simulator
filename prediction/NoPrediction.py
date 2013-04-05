
import prediction.Prediction

class NoPrediction(prediction.Prediction.Prediction):
	
	def __init__(self):
		prediction.Prediction.Prediction.__init__(self)

	def calculate_prediction_for_new_task(task):
		self.calculate_prediction(task)

	def calculate_prediction(task):
		task.CPU_usage = task.CPU_usage_real
		task.mem_usage = task.mem_usage_real
