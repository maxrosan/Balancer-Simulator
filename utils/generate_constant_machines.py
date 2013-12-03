

import sys


if __name__ == "__main__":

	fileName = sys.argv[1]
	numOfMachines = int(sys.argv[2])

	fp = open(fileName, "w+")

	for i in range(1, numOfMachines + 1):
		fp.write("0,%d,0,HofLGzk1Or/8Ildj2+Lqv0UGGvY82NLoni8+J/Yy0RU=,1.0,1.0\n" % (i))

	fp.close()

