from parse import *
def main():
	x="x = x+5"
	c=parse("{}={}", x)
	print c
	#c[1]=2
	y={'1':2, 'a':2}
	print y
	y['1']=3
	y["v"]=1
	print y
	print c[0],c[1]

if __name__ == '__main__':
	main()