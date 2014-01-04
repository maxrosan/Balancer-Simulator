
import prediction.Prediction

class NoPrediction(prediction.Prediction.Prediction):
	
	def __init__(self):
		prediction.Prediction.Prediction.__init__(self)

	def calculate_prediction_for_new_task(self, task):
		self.calculate_prediction(task, task)

	def calculate_prediction(self, task, new_task):
		pass
