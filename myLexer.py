# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
# -----------------------------------------------------------------------------

import sys
import math
import re
import ply.yacc as yacc
sys.path.insert(0, "../..")
# Build the lexer
reserved = {
        'cierto' : 'BOOL',
        'falso' : 'BOOL',
        'entero' : 'TYPE',
        'real': 'TYPE',
        'finmientras': 'FINMIENTRAS',
        'not': 'NOT',
        'devolver': 'DEVOLVER',
        'booleano': 'TYPE',
        'vector': 'VECTOR',
        'long': 'LONG',
        'mientras': 'MIENTRAS',
        'si': 'SI',
        'registro': 'REGISTRO',
        'caracter': 'TYPE',
        'entonces': 'ENTONCES',
        'sino': 'SINO',
        'finsi': 'FINSI',
        'and': 'AND',
        'or': 'OR',
        'funcion': 'FUNCION'

    }



if sys.version_info[0] >= 3:
    raw_input = input


# Tokens

tokens = [
    'NAME', 'OCTAL', 'BINARIO', 'HEXADECIMAL', 'REAL', 'NUMBER', 'NEWLINE', 'COMPARACION', 'CHAR', 'BOOL', 'TYPE', 'FINMIENTRAS', 'NOT', 'DEVOLVER', 'VECTOR', 'LONG', 'MIENTRAS',
    'SI', 'REGISTRO', 'ENTONCES', 'SINO', 'FINSI', 'AND', 'OR', 'FUNCION'
]
literals = ['=', '+', '-', '*', '/', '(', ')', '&', '|', '[', ']', '{', '}', ',', '.', ';', '!']

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'COMPARACION'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS', 'UPLUS', 'NOT')
)


def t_CHAR(t):
    r'\'[a-zA-Z]\''
    return t

def t_COMPARACION(t):
    r'(==|<=|>=|<|>)'
    return t


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(),'NAME')    # Check for reserved words
    return t


def t_AND(t):
    r'(and|AND|&)'
    return t

def t_OR(t):
    r'(or|OR|\|)'
    return t

def t_NOT(t):
    r'(not|!)'
    return t
#Función que lee un valor en octal y lo pasa a decimal para hacer las operaciones correspondientes
def t_OCTAL(t):
    r'0[0-7]+'
    t.value = int(t.value, 8)
    return t

#Función que lee un valor en binario y lo pasa a decimal para hacer las operaciones correspondientes

def t_BINARIO(t):
    r'0[bB][01]+'
    t.value = int(t.value, 2)
    return t    

#Función que lee un valor en hexadecimal y lo pasa a decimal para hacer las operaciones correspondientes

def t_HEXADECIMAL(t):
    r'0[xX][0-9a-fA-F]+'
    t.value = int(t.value, 16)
    return t


#Función que lee un valor en real (con o sin notación científica) y lo pasa a decimal para hacer las operaciones correspondientes
def t_REAL(t):
    r'\d+.\d+|\d+e-*\d+'
    t.value = float(t.value)
    return t

# Función que lee un valor en decimal, debe ser declarada antes que los reales
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t




#Función que lee un salto de linea y suma la linea nueva al contador de lineas
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t
#Expresión regular para ignorar las sangrías
t_ignore = " \t"
#Expresión regular para ignorar los comentarios
t_ignore_comment = "%.*\n\r"
    
# Función utilizada para saltar a la siguente linea en caso de dar error en una de ellas
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)



import ply.lex as lex
lexer = lex.lex()


