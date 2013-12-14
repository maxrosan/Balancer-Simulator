
import commands

dirMovies = "/run/media/max/386D-A05B/DCIM/101MSDCF/"
dirDst =  "tmp/"

files = [
("MOV01488.AVI", "mem_0"),
("MOV01489.AVI", "mem_32M"),
("MOV01490.AVI", "mem_64M"),
("MOV01491.AVI", "mem_128M"),
("MOV01492.AVI", "mem_256M"),
("MOV01493.AVI", "mem_512M"),
("MOV01494.AVI", "mem_1G"),
("MOV01495.AVI", "mem_2G"),
("MOV01496.AVI", "mem_4G"),
("MOV01498.AVI", "mem_6G")
]

#

for f in files:
	fn = dirMovies + f[0]
	fnDst = dirDst + f[1] + "/video%d.jpg"
	cmd = "ffmpeg -i " + fn + " -r 4 -f image2 " + fnDst
	if commands.getstatusoutput(cmd)[0] != 0:
		print cmd, "failed!"
	else:
		print cmd, "worked!"


