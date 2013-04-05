
import prediction.Prediction

class NoPrediction(prediction.Prediction):
	
	def __init__(self):
		prediction.Prediction.__init__()

	def calculate_prediction_for_new_task(task):
		self.calculate_prediction(task)

	def calculate_prediction(task):
		task.CPU_usage = task.CPU_usage_real
		task.mem_usage = task.mem_usage_real
