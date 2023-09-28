from myParser import yacc
import re

fname= "control_de_flujo.txt"
try:
    f = open(fname , 'r')
except IOError:
    print ("Archivo no encontrado:", fname)

s = f.read()
expresion_regular = re.compile(r'^%.*$')
if s == "":
    pass

elif expresion_regular.search(s):
    pass
else:
    yacc.parse(s)
