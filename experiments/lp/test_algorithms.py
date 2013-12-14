


def generate_VMs(num):

	VMs = []

	for i in range(0, num):
		cpu = random.random()
		mem = random.random()

		VMs.append((cpu, mem))

	return VMs


def generate_macs(num):

	macs = [(1., 1.)] * num

	return macs


def W_cpu(cpu_usage):

	if cpu_usage > 0.25:
		return 0.05

	return 0.133

def W_on(cpu_usage):
	