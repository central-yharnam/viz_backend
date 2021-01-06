from colorama import  init, Fore, Back, Style 

# Python program to print 
# colored text and background 

init(convert=True)


def failure(string):
	print("\u001b[31m{}\u001b[0m".format(string))
def success(string):
	print("\u001b[32m{}\u001b[0m".format(string))
def utility(string):
	print("\u001b[33m{}\u001b[0m".format(string))
def contact(string):
	print("\u001b[36m{}\u001b[0m".format(string))
def response(string):
	print("\u001b[35m{}\u001b[0m".format(string))
if __name__ == '__main__':
	utility("hello")
	success("hello")
	failure("hello")

