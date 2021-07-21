import re
from collections import namedtuple
class mem:
	def __init__(self, only, bits):
		self.only = only
		self.bits = bits

	def __str__(self):
		result = 0
		leng = len(self.bits)
		if(leng < 7):
				self.bits += "0" * (7 - leng)
				self.only = False
		if(self.only):
			result = (1 << 7) + (int(self.bits[0]) << 6) + (leng - 7) 
		else:
			result = int(self.bits,2)
		s = int_to_hex(result)
		return s + ", "


def hex_to_bin(i):
		s = bin(int(i,base = 16))[2:]
		lenght = 8 - len(s)
		s = "0" * lenght + s
		return s

def int_to_bin(i):
		s = bin(i)[2:]
		return s

def bin_to_hex(i):
		tmp = int(i,base=2)
		s = "0x"
		if(tmp < 0x10):
			s+="0"
		s+=hex(tmp)[2:]
		return s

def int_to_hex(i):
	s = "0x"
	if(i < 0x10):
		s+="0"
	s+=hex(i)[2:]
	return s

class OldAlfa:
	#			a8 a16 a24 a32
	#max for width and height
	wsizes = [0b111,	0b1111111, 0b1111111111,	0b11111111111111]
	hsizes = [0b1111,	0b1111111, 0b11111111111,	0b11111111111111]
	
	#keys in bin
	keys = ["0b1",		"0b10",	   "0b100",			"0b1000"]
	#count of bit for width and height
	wbit = [3,			7,			10,				14]
	hbit = [4,			7,			11,				14]
	keybit = [1,          2,          3,              4]
	
	@staticmethod
	def spliter(s,w,h):
		result = [mem(True, s[0])]
		leng = 0
		l = len(s)
		for i in range(1,l):
			if(result[leng].only):
				if(s[i] == s[i - 1]):
					if(len(result[leng].bits) - 7 < 0b111111):
						result[leng].bits += s[i]
					else:
						result.append(mem(True,s[i]))
						leng += 1
				else:
					if(len(result[leng].bits) <= 7):
						result[leng].only = False
					else:
						leng += 1
						result.append(mem(True,s[i]))
			if(result[leng].only == False):
				if(len(result[leng].bits) < 7):
					result[leng].bits += s[i]
				else:
					leng += 1
					result.append(mem(True,s[i]))
		return result

class OldImage(OldAlfa):
	def __init__(self, s):
		#get name of symbol
		regular = re.findall(r"\}\s+([_,\w,\d]+)[_\w\d\"\(\)\s]*= \{", s)
		self.symbol = regular[0]
		
		#get width, 0, height, 0,
		sizes = re.findall(r"[width,height] = \d+",s)
		#get width
		width = re.findall(r"\d+",(sizes[0]))[0]
		#get height
		height = re.findall(r"\d+",(sizes[1]))[0]
		self.width = int(width)
		self.height = int(height)
		#get payload without sizes
		payload = re.search(r"0x[\n\w\s\,]+\},",s)[0][:-3]
		#to 1 string
		payload = payload.replace("\t","")
		payload = payload.replace(","," ")
		self.payload = list(payload.split())
		self.size = int(re.findall(r"u8 payload\[(\d+)]",s)[0])
		

		#find type of alfa
		wtype, htype = 0, 0
		
		for i,w in enumerate(OldAlfa.wsizes):
			if(self.width < w):
				wtype = i
				break
		
		for i,h in enumerate(OldAlfa.hsizes):
			if(self.height < h):
				htype = i
				break
		
		self.type = max(wtype,htype)

		#get size of payload
		self.size = len(self.payload)


	def toNewAlfa(self):
		t = self.type
		O = OldAlfa
		#finaly struct for write
		newalfa = ["const struct {\n\t",
					f"unsigned key : {O.keybit[t]};\n\t",
					f"unsigned width : {O.wbit[t]};\n\t",
					f"unsigned height : {O.hbit[t]};\n\t",
					f"u8 payload[{self.size}];\n",
					"} ",
						self.symbol, " = {\n\t",
						".key = ",  str(O.keys[self.type]), ",\n\t",
						".width = ", str(self.width), ",\n\t",
						".height = ", str(self.height), ",\n\t",
						".payload = {", self.payload ,"},\n"
						"};\n"]

		return "".join(newalfa) + "\n\n\n"

	def CreExtern(self):
		#finaly extern struct for write
		newalfa = ["extern const amask_t " , self.symbol, ";"]
		return "".join(newalfa) + "\n\n"

	

	def draw(self):
		nums = list(map(lambda x : int(str(x).replace(", ",""),16),self.Compress()))
		
		result = ""
		word_pos = 0
		count = (self.width + 1) * (self.height + 1)
		select = 0
		for i in range(count,0,-1):
			try:
				data = nums[select]
				if(data >> 7 == 0):
					rawdata = data & 0b01111111
					result += str((rawdata >> (6-word_pos)) & 1)
					word_pos += 1
					if(word_pos == 7):
						word_pos = 0
						select+=1
				else:
					leng = (data & 0b00111111) + 7
					color = (data >> 6) & 1
					result+=str(color)
					word_pos+=1
					if(word_pos == leng):
						word_pos = 0
						select+=1
			except:
				result+="0"

		'''
		for i in nums:
			if(i>>7==1):
				result += str((i>>6)&1) * ((i&0b00111111) + 7)
			else:
				tmp = bin(i&0b01111111)[2:]
				result += ("0"*(7-len(tmp))) + tmp
		'''
		return result
		

	

	def Compress(self):
		s = "".join(list(map(lambda x : hex_to_bin(x)[::-1],self.payload)))
		split = OldAlfa.spliter(s,self.width+1,self.height+1)
		#print(s)
		#print(*list(map(lambda x : f"{str(int(x.only))} : {x.bits}",split)))
		return split

	def print(self,s):
		w = self.width + 1
		index = 0

		for i in s:
			print(i,end="")
			index+=1
			if(index % w == 0):
				print()
				index = 0

	def correct(self):
		s = "".join(list(map(lambda x : hex_to_bin(x)[::-1],self.payload)))
		split = OldAlfa.spliter(s,self.width+1,self.height+1)
		not_comp = "".join(list(map(lambda x : x.bits, split)))
		compress = self.draw()

		if(self.symbol == "__senso_main"):
			print(self.symbol)
			print(len(s),len(not_comp),len(compress),(self.width+1)*(self.height+1))
			print(compress in s)
			print("\n\n\ncorrect")
			self.print(s)
			print("\n\n\ncompress")
			self.print(compress)
			
			input()

		return [len(self.payload), len(split), s == compress]

	def PrintCommpres(self):
		compress = "".join(list(map(str,self.Compress())))
		leng = len(compress.split(", "))

		t = self.type
		O = OldAlfa
		newalfa = ["const struct {\n\t",
					f"unsigned key : {O.keybit[t]};\n\t",
					f"unsigned width : {O.wbit[t]};\n\t",
					f"unsigned height : {O.hbit[t]};\n\t",
					f"u8 payload[{leng}];\n",
					"} ",
						self.symbol, " = {\n\t",
						".key = ",  str(O.keys[self.type]), ",\n\t",
						".width = ", str(self.width), ",\n\t",
						".height = ", str(self.height), ",\n\t",
						".payload = {", compress ,"},\n"
						"};\n"]

		return "".join(newalfa) + "\n\n\n"