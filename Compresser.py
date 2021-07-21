import os
import re

from OldAlfaM import OldImage

def decode(s):
	bits = "".join(list(map(lambda x : x.bits, s)))
	return bits



def main():
	# path to project
	path = "img"
	#path = "E:/work/save/PngToAlfaMask/x64/Release/"
	#list of *.c files
	files = []
	# r=root, d=directories, f = files
	for r, d, f in os.walk(path):
		#find all *.c
		for file in f:
			if '.c' in file and not ".o" in file:
				files.append(os.path.join(r, file))

	old_size = 0
	new_size = 0

	#read all files
	for file in files:	
		read = open(file,"r")
		alfafile = "".join(read.readlines())
		read.close()
		#try find alfa
		regular = r"(const struct \{\n\t(unsigned \w+ : \d+;\n\t)+u8 payload\[\d+\];\n\}\s*[_\w\d]+ [_\w\d\"\(\)\s]*= \{\n\t(\.\w+ = [b\d]+,\n\t)+\.payload = \{[\w\s,\n\t]+\},\n\};)"
		masks = re.findall(regular, alfafile)
		masks = list(map(lambda x: x[0],masks))
		if(len(masks) > 0):
			path = file[file.rfind('\\'):]
			f = open("result/" + path, "w")
			f.write("#include \"arch.h\"\n\n\n")
			print(len(masks))
			#all finded mask convert to new alfa and write to new file
			for i,s in enumerate(masks):
				alfa = OldImage(s)
				old_len,new_len,correct = alfa.correct()


				old_size += old_len
				new_size += new_len
				
				f.write(alfa.PrintCommpres())
	
			f.close()

	print(f"old_size = {old_size}, new_size = {new_size}, diff = {old_size - new_size}")


if __name__ == "__main__":
	main()


