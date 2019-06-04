import os

def run(**args):
	print("[*] In envrionment module")
	return str(os.environ)
run()
