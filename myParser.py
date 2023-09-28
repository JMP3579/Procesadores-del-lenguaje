import sys
import math
import re
import ply.yacc as yacc
sys.path.insert(0, "../..")

import ply.lex as lex
from myLexer import lexer, tokens, precedence

if sys.version_info[0] >= 3:
    raw_input = input
# Tabla de variables
names = {}
# Tabla de registros
registros = {}
# Diccionario para transformar booleanos en su sintaxis de python
transformador_bool = {
    'cierto' : True,
    'falso': False,
}
# Diccionario para transformar los tipos de variable a su sintaxis correspondiente en python
valid_types = {
    'entero': int,
    'real': float,
    'booleano': bool,
    'caracter': str,
}

hayerrores = False
hayflujo = False
#Reglas de producción

def p_axioma(p):
    "axioma : statements"
    archivo_salida = open("output.txt", "w")
    if hayerrores == False:
        archivo_salida.write("Variables:\n")
        for clave, valor in names.items():
            if hayflujo == False:
                if valor[0] != 'registro' and valor[0] != 'vector':
                    archivo_salida.write(f'Nombre: {clave}, Tipo: {valor[0]}, Valor: {valor[1]}\n')
                elif valor[0] == 'vector':
                    archivo_salida.write(f'Vector: Nombre: {clave}, Tipo: {valor[1]}, Valores: {valor[2]}\n')
                elif valor[0] == 'registro':
                    archivo_salida.write(f'Registro: Nombre: {clave}\n')
                    for clave2, atributo in valor[1].items():
                        if atributo[0] != "vector":
                            archivo_salida.write(f'Nombre del atributo: {clave2}, Tipo del atributo: {atributo[0]}, valor: {atributo[1]}\n')
                        else:
                            archivo_salida.write(f'Nombre del atributo: {clave2}, Vector, Tipo del atributo: {atributo[1]}, valores: {atributo[2]}\n')
                        
            else:
                 if valor[0] != 'registro' and valor[0] != 'vector':
                    archivo_salida.write(f'Nombre: {clave}, Tipo: {valor[0]}\n')
                 elif valor[0] == 'vector':
                    archivo_salida.write(f'Vector: Nombre: {clave}, Tipo: {valor[1]}\n')
                 elif valor[0] == 'registro':
                    archivo_salida.write(f'Registro: Nombre: {clave}\n')
                    for clave2, atributo in valor[1].items():
                        if atributo[0] != "vector":
                            archivo_salida.write(f'Nombre del atributo: {clave2}, Tipo del atributo: {atributo[0]}\n')
                        else:
                            archivo_salida.write(f'Nombre del atributo: {clave2}, Vector, Tipo del atributo: {atributo[1]}\n')
                        
        for clave, valor in registros.items():
            archivo_salida.write(f'Registro: {clave}, Atributos : {valor}\n')

#Primera regla de producción, que contiene todas las operaciones. Además, contempla que pueda haber dos comentarios seguidos y hace que no pueda haber dos operaciones en la misma linea.
def p_statements(p):
    '''statements : statements NEWLINE statement 
                  | statement
                  | statements NEWLINE
                  | NEWLINE
                  '''
    pass
# Regla de producción para declarar y asignar valor a variables
def p_statement_assign(p):
    '''statement : NAME "=" expression
                 | TYPE NAME "=" expression
                 | TYPE names'''
    global hayerrores
    if len(p) == 4:
        # Guarda el nombre y el valor de la variable que se quiere almacenar
        variable_name = p[1]
        value = p[3]
        # Si la variable está declarada comprueba si es un vector o no
        if variable_name in names:
            # Si no es un vector se actualiza la variable según su tipo
            if names[variable_name][0] != "vector":
                variable_type = type(names[variable_name][1])
                # Si el tipo asignado coincide con el tipo de la variable o puede ser transformado actualiza el valor, en caso contrario salta un error
                if variable_type == type(value) or variable_type == bool:
                    names[variable_name][1] = value
                elif variable_type == float and type(value) == int:
                    names[variable_name][1] = float(value)
                elif variable_type == int and type(value) == str:
                    names[variable_name][1] = ord(value)
                elif variable_type == float and type(value) == str:
                    names[variable_name][1] = float(ord(value))
                
                else:
                    print(f"Error: Valor no compatible con el tipo de la variable '{variable_name}'")
                    hayerrores = True
            else:
                print("Error: Se está intentando acceder a un vector sin utilizar un índice")
                hayerrores = True
        else:
              print(f"Error: Variable '{variable_name}' no definida")
              hayerrores = True

    elif len(p) == 5:
        # Guarda el nombre, el tipo y el valor de la variable que se quiere almacenar
        variable_type = p[1].lower()
        variable_name = p[2]
        value = p[4]
        # Si la variable no está declarada comprueba que el tipo asignado coincide con el tipo de la variable o puede ser transformado actualiza el valor, en caso contrario salta un error
        if variable_name not in names:
            if type(value) == valid_types[variable_type] or variable_type == bool:
                names[variable_name] = [variable_type, value]
            elif valid_types[variable_type] == float and type(value) == int:
                names[variable_name] = [variable_type, float(value)]
            elif valid_types[variable_type] == int and type(value) == str:
                names[variable_name] = [variable_type, ord(value)]
            elif valid_types[variable_type] == float and type(value) == str:
                    names[variable_name] = [variable_type, float(ord(value))]
            else:
                print(f"Error: Valor no compatible con el tipo de la variable '{variable_name}'")
                hayerrores = True
        else:
            print(f"Error: Variable '{variable_name}' ya declarada")
            hayerrores = True
        
    elif len(p) == 3:
        # Guarda el tipo de la variable
        variable_type = p[1].lower()
        for name in p[2]:
            # Si la variable no está declarada, la añade con un valor por defecto
            if name not in names:
                names[name] = [variable_type, 0]
                if variable_type == 'real':
                    names[name][1] = 0.0
                elif variable_type == 'entero':
                    names[name][1] = 0
                elif variable_type == 'booleano':
                    names[name][1] = False
                else:
                    names[name][1] = ""
            # Si ya está declarada salta un error.
            else:
                print(f"Error: Variable '{name}' ya declarada")
                hayerrores = True

# Regla que sirve para declarar variables como registros
def p_statement_registro_new(p):
    '''statement : NAME NAME'''
    # Se almacenan el nombre del registro y de la variable
    registro = p[1]
    variable_name = p[2]
    # Si el registro ha sido declarado intenta añadir la variable
    if registro in registros:
        # Si la variable no ha sido declarada crea una variable de tipo registro con ese nombre
        if variable_name not in names:
            names[variable_name] = ["registro", {}]
            # Añade todos los atributos con un valor por defecto a la nueva variable, dependiendo de si es un vector o no
            for clave, valor in registros[registro].items():
                # Si no es un vector añade el valor como un número, un booleano o un string vacío
                if valor[0].lower() != 'vector':
                    tipo = valor[0].lower()
                    if tipo == 'entero':
                        names[variable_name][1][clave] = [tipo, 0]
                    elif tipo == 'real':
                        names[variable_name][1][clave] = [tipo, 0.0]
                    elif tipo == 'booleano':
                        names[variable_name][1][clave] = [tipo, False]
                    else:
                        names[variable_name][1][clave] = [tipo, ""]
                # Si es un vector crea un vector del tamaño establecido en el registro con valores por defecto
                else:
                    names[variable_name][1][clave] = ['vector', valor[1].lower(), []]
                    for n in range(valor[2]):
                        if valor[1].lower() == 'entero':
                            names[variable_name][1][clave][2].append(0)
                        elif valor[1].lower() == 'real':
                            names[variable_name][1][clave][2].append(0.0)
                        elif valor[1].lower() == 'booleano':
                            names[variable_name][1][clave][2].append(False)
                        else:
                            names[variable_name][1][clave][2].append("")

                    
# Regla que sirve para encadenar nombres de variable para declararlas
def p_names(p):
    '''names : NAME "," names
             | NAME'''
    global hayerrores
    # Si hay varios nombres los encadena
    if len(p) == 4:
        p[3].append(p[1])  
        p[0] = p[3] 
    else:
        p[0] = [p[1]]  

# Regla para declarar registros
def p_statement_registro(p):
    '''statement : REGISTRO NAME "{" declaracion "}" '''
    global hayerrores
    # Almacena el nombre del registro
    registro_name = p[2]
    # Si el nombre no se usa para ningún registro almacena el registro en la tabla
    if registro_name not in registros:
        registros[registro_name] = {}
        # Comprueba si cada atributo es un vector, si lo es lo almacena como tal
        for a, nombres in p[4]:
            if type(a) != list:
                tipo = a
                # Si no es un vector para cada nombre de un mismo tipo crea un atributo
                for nombre in nombres:
                    # Si el atributo no se repite lo crea, si no lo omite
                    if nombre not in registros[registro_name]:
                        registros[registro_name][nombre] = [tipo]
                    else:
                        print(f'Error: 2 atributos no pueden tener el mismo nombre')
                        hayerrores = True
            # Si es un vector lo añade, con su tipo y longitud
            else:
                tipo = a[1]
                longitud = a[2]
                nombre = nombres
                registros[registro_name][nombre] = ['vector', tipo, longitud]

    # Si ya está declarado salta un error
    else:
        print(f'Error: registro "{registro_name}" ya declarado')
        hayerrores = True

# Reglas para cambiar el valor de los atributos de los registro
def p_statement_registro_name(p):
    '''statement : NAME "." NAME "=" expression
                 | NAME "." NAME "[" NUMBER "]" "=" expression'''
    global hayerrores
    if len(p) == 6:
        # Almacena los nombres del registro y el atributo y el valor que se le quiere dar
        registro = p[1]
        atributo = p[3]
        value = p[5]
        # Comprueba si el registro está declarado, en caso contrario salta un error
        if registro in names:
            # Comprueba si se está intentando acceder a un registro o a otro tipo de variable
            if names[registro][0] == "registro":
                # Comprueba si se está accediendo a un atributo existente
                if atributo in names[registro][1]:
                    # Almacena el tipo del atributo
                    tipo = names[registro][1][atributo][0].lower()
                    # Si el atributo es válido asigna el nuevo valor al atributo
                    if type(value) == valid_types[tipo]:
                        names[registro][1][atributo][1] = value
                    # Si el tipo no coincide salta un error
                    else:
                        print(f"Error: Valor no compatible con el tipo del atributo '{atributo}'")
                        hayerrores = True
                # Si el atributo no está declarado en el registro salta un error
                else:
                    print(f'Error: Atributo "{atributo}" del registro "{registro}" no declarado')
                    hayerrores = True
            # Si se accede a una variable que no es un registro salta un error
            else:
                print(f'Error: La variable "{registro}" no es un registro')
                hayerrores = True
        # Si el registro no está declarado salta un error
        else:
            print(f'Error: Registro "{registro}" no declarado')
            hayerrores = True

    elif len(p) == 9:
        # Almacena los nombres del registro, el atributo, el valor que se le quiere dar y el índice del vector
        registro = p[1]
        atributo = p[3]
        index = p[5]
        value = p[8]
        # Comprueba si el registro está declarado, en caso contrario salta un error
        if registro in names:
            # Comprueba si se está intentando acceder a un registro o a otro tipo de variable
            if names[registro][0] == "registro":
                # Comprueba si se está accediendo a un atributo existente
                if atributo in names[registro][1]:
                    # Comprueba si se está accediendo a un vector
                    if names[registro][1][atributo][0] == 'vector':
                        # Almacena el tipo del vector
                        tipo = names[registro][1][atributo][1].lower()
                        # Comprueba si el tipo que se quiere asignar es válido
                        if type(value) == valid_types[tipo]:
                            # Comprueba si se está accediendo a una posición válida dentro del vector
                            if (len(names[registro][1][atributo][2]) - 1) >= index:
                                # Asigna el valor a la posición indicada del vector
                                names[registro][1][atributo][2][index] = value
                            # Si se intenta acceder a una posición no válida salta un error
                            else:
                                print(f'Error: Vector "{atributo}" fuera de rango')
                                hayerrores = True
                        # Si el tipo no coincide salta un error
                        else:
                            print(f"Error: Valor no compatible con el tipo del atributo '{atributo}'")
                            hayerrores = True
                    # Si el atributo no es un vector salta un error
                    else:
                        print(f"Error: La variable '{atributo}' no es un vector")
                        hayerrores = True
                # Si el atributo no está declarado en el registro salta un error
                else:
                    print(f'Error: Atributo "{atributo}" del registro "{registro}" no declarado')
                    hayerrores = True
            # Si se accede a una variable que no es un registro salta un error
            else:
                print(f'Error: La variable "{registro}" no es un registro')
                hayerrores = True
        # Si el registro no está declarado salta un error
        else:
            print(f'Error: Registro "{registro}" no declarado')
            hayerrores = True





# Reglas de producción que contemplan las declaraciones de atributos dentro de los registros
def p_declaracion(p):
    '''declaracion : TYPE names ";" NEWLINE declaracion
                   | TYPE names ";" declaracion
                   | TYPE names ";"
                   | NAME NAME ";" NEWLINE declaracion
                   | NAME NAME ";" declaracion
                   | NAME NAME ";"
                   | VECTOR TYPE NAME "[" NUMBER "]" ";" NEWLINE declaracion
                   | VECTOR TYPE NAME "[" NUMBER "]" ";" declaracion
                   | VECTOR TYPE NAME "[" NUMBER "]" ";"'''
    global hayerrores
    if len(p) == 10:
         # Si es un vector añade su tipo, tamaño y nombre a la declaración total
         p[9].append([['vector', p[2].lower(), p[5]], p[3]])
         p[0] = p[9]
    elif len(p) == 9:
        # Si es un vector añade su tipo, tamaño y nombre a la declaración total
        p[8].append([['vector', p[2].lower(), p[5]], p[3]])
        p[0] = p[8]
    elif len(p) == 8:
        # Si es un vector añade su tipo, tamaño y nombre
        p[0] = [[['vector', p[2].lower(), p[5]], p[3]]]
        
    elif len(p) == 6:
            # Añade el nombre y el tipo a la declaración total
            p[5].append([p[1].lower(), p[2]])
            p[0] = p[5]
        

    elif len(p) == 5:
            # Añade el nombre y el tipo a la declaración total
            p[4].append([p[1].lower(), p[2]])
            p[0] = p[4]

    elif len(p) == 4:
        # Añade el nombre y el tipo
        p[0] = [[p[1].lower(), p[2]]]


# Regla de producción para la declaración de vectores
def p_vector_assignment(p):
    '''statement : VECTOR TYPE NAME "[" NUMBER "]"'''
    global hayerrores
    # Guarda el tipo, nombre y longitud del vector
    variable_type = p[2].lower()
    variable_name = p[3]
    length = p[5]
    # Comprueba que el nombre no esté siendo utilizado por otra variable
    if variable_name not in names:
        # Comprueba que el tipo es válido
        if variable_type in valid_types:
            # Crea un vector en names y lo rellena según el tipo del vector
            names[variable_name] = ["vector", variable_type, []]
            if variable_type == 'entero':
                variable_añadir = 0
            elif variable_type == 'real':
                variable_añadir = 0.0
            
            elif variable_type == 'caracter':
                variable_añadir = ""

            elif variable_type == 'booleano':
                variable_añadir = False
            for n in range(length):
                names[variable_name][2].append(0)
        # Si el tipo no es válido salta un error  
        else:
            print(f"Error: Tipo no válido para la variable '{variable_name}'")
            hayerrores = True
    # Si la variable ya está declarada salta un error
    else:
        print(f"Error: Variable '{variable_name}' ya declarada")
        hayerrores = True

# Regla de producción que sirve para modificar el valor de un vector
def p_vector_op(p):
    '''statement : NAME "[" NUMBER "]" "=" expression'''
    global hayerrores
    # Almacena el nombre e índice del vector, además del valor que se le quiere dar
    variable_name = p[1]
    index = p[3]
    value = p[6]
    # Comprueba que el vector esté declarado
    if variable_name in names:
        # Comprueba que la variable sea un vector
        if names[variable_name][0] == "vector":
            # Comprueba si se está accediendo a una posición válida dentro del vector
            if (len(names[variable_name][2]) - 1) >= index:
                # Comprueba que el tipo que se quiere asignar sea válido
                if type(names[variable_name][2][index] == type(value)):
                    names[variable_name][2][index] = value
                # Si el tipo no coincide salta un error
                else:
                    print(f"Error: Valor no compatible con el tipo de la variable '{variable_name}'")
                    hayerrores = True
            # Si se intenta acceder a una posición no válida salta un error
            else:
                  print(f"Error: Índice del vector '{variable_name}' fuera de rango")
                  hayerrores = True
        # Si la variable no es un vector salta un error
        else:
            print(f"Error: La variable '{variable_name}' no es un vector")
            hayerrores = True
    # Si la variable no está declarada salta un error
    else:
        print(f"Error: Variable '{variable_name}' no definida")
        hayerrores = True


# Regla de producción que contempla los condicionales   
def p_si(p):
    '''statement : SI expression ENTONCES NEWLINE statements FINSI
                 | SI expression ENTONCES NEWLINE statements SINO NEWLINE statements FINSI
                 | SI expression NEWLINE ENTONCES NEWLINE statements FINSI
                 | SI expression NEWLINE ENTONCES NEWLINE statements SINO NEWLINE statements FINSI'''
    # Comprueba que la expresión sea un valor booleano
    global hayerrores
    if (type(p[2])) != bool:
        print(f'Error: La condición debe ser un valor booleano')
        hayerrores = True
    global hayflujo
    hayflujo = True
    
# Regla de producción que contempla los bucles
def p_mientras(p):
    '''statement : MIENTRAS expression NEWLINE statements FINMIENTRAS'''
    # Comprueba que la expresión sea un valor booleano
    global hayerrores
    if (type(p[2])) != bool:
        print(f'Error: La condición debe ser un valor booleano')
        hayerrores = True
    global hayflujo
    hayflujo = True
# Regla de producción que contempla las funciones
def p_funcion(p):
    '''statement : FUNCION NAME "(" parametros ")" ":" TYPE NEWLINE "{" statements NEWLINE DEVOLVER expression "}"
                 | FUNCION NAME "(" ")" ":" TYPE NEWLINE "{" statements NEWLINE DEVOLVER expression "}"'''
    global hayflujo
    hayflujo = True
# Regla de producción para los parámetros de las funciones
def p_parametros(p):
    '''parametros : TYPE NAME "," parametros
                  | TYPE NAME
                  | NAME NAME "," parametros
                  | NAME NAME'''

# Regla de producción que contempla cualquier operación
def p_statement_expr(p):
    'statement : expression'
    pass


# Reglas de producción que contemplan las operaciones entre expresiones
def p_prioridad_2(p):
    '''expression : expression '*' expression
                  | expression '/' expression
                  | expression '+' expression
                  | expression '-' expression
                  | expression COMPARACION expression
                  | expression AND expression
                  | expression OR expression
                  | NOT expression
                  '''
    global hayerrores

    if len(p) == 4:
        tipo_1 = type(p[1])
        tipo_2 = type(p[3])
        if tipo_1 == str and p[1] not in valid_types:
            p[1] = ord(p[1])
        if tipo_2 == str and p[3] not in valid_types:
            p[3] = ord(p[3])
        
        p[2] = p[2].lower()
        if tipo_1 == dict or tipo_2 == dict:
            print(f'Error: Operación con variables no válidas')
        elif p[1] is None or p[3] is None:
            print(f'Error: Operación con variables no válidas')
        elif (tipo_1 == bool and tipo_2 != bool) or (tipo_2 == bool and tipo_1 != bool):
            print(f"Error: No se permiten operaciones entre un valor booleano y otro tipo de variable")
            hayerrores = True
        elif (tipo_1 == bool or tipo_2 == bool) and (p[2] != '==' and p[2] != 'and' and p[2] != '&' and p[2] != 'or' and p[2] != '|'):
            print(f"Error: Operación no permitida para valores booleanos")
            hayerrores = True
        elif p[1] in valid_types or p[3] in valid_types:
            print(f'Error: Operación con variables no válidas')
        else:
            # Realiza la operación de multiplicación
            if p[2] == '*':
                p[0] = p[1] * p[3]
            # Realiza la operación de división
            elif p[2] == '/':
                if p[3] == 0:
                    print(f"No se permite la división entre 0")
                    hayerrores = True
                else:
                    p[0] = p[1] / p[3]
            
            # Si la operación es de suma realiza la suma
            elif p[2] == '+':
                p[0] = p[1] + p[3]
            # Si la operación es de resta realiza la resta
            elif p[2] == '-':
                p[0] = p[1] - p[3]  
            # Comprueba si la operación es del tipo >=, la cual solo puede realizarse entre valores no booleanos
            elif p[2] == '>=':
                if tipo_1 == bool or tipo_2 == bool:
                     print(f"Error: No se permiten operaciones del tipo '>=' entre valores booleanos")
                     hayerrores = True
                    
                
                if p[1] >= p[3]:
                    p[0] = transformador_bool['cierto']
                else:
                    p[0] = transformador_bool['falso']
            # Comprueba si la operación es del tipo <=, la cual solo puede realizarse entre valores no booleanos
            elif p[2] == '<=':
                if tipo_1 == bool or tipo_2 == bool:
                     print(f"Error: No se permiten operaciones del tipo '<=' entre valores booleanos")
                     hayerrores = True
                    
                
                if p[1] <= p[3]:
                    p[0] = transformador_bool['cierto']
                else:
                    p[0] = transformador_bool['falso']
            # Comprueba si la operación es del tipo >, la cual solo puede realizarse entre valores no booleanos
            elif p[2] == '>':
                if tipo_1 == bool or tipo_2 == bool:
                     print(f"Error: No se permiten operaciones del tipo '>' entre valores booleanos")
                     hayerrores = True
                    
                
                if p[1] > p[3]:
                    p[0] = transformador_bool['cierto']
                else:
                    p[0] = transformador_bool['falso']
            # Comprueba si la operación es del tipo <, la cual solo puede realizarse entre valores no booleanos
            elif p[2] == '<':
                if tipo_1 == bool or tipo_2 == bool:
                     print(f"Error: No se permiten operaciones del tipo '<' entre valores booleanos")
                     hayerrores = True
                    
                
                if p[1] < p[3]:
                    p[0] = transformador_bool['cierto']
                else:
                    p[0] = transformador_bool['falso']
             # Comprueba si la operación es del tipo ==
            elif p[2] == '==':
                
                if p[1] == p[3]:
                    p[0] = transformador_bool['cierto']
                else:
                    p[0] = transformador_bool['falso']
            # Comprueba si la operación es del tipo and
            elif p[2] == 'and' or p[2] == '&':
                if tipo_1 == bool and tipo_2 == bool:
                    p[0] = p[1] and p[3]
                else:
                    print(f'Error: La operación "and" debe utilizar 2 valores booleanos')
                    hayerrores = True
            # Comprueba si la operación es del tipo or
            elif p[2] == 'or' or p[2] == "|":
                if tipo_1 == bool and tipo_2 == bool:
                    p[0] = p[1] or p[3]
                else:
                    print(f'Error: La operación "or" debe utilizar 2 valores booleanos')
                    hayerrores = True
    # Si la operación es not comprueba que el valor sea booleano
    else:
        tipo = type(p[2])
        if tipo == bool:
            p[0] = not p[2]
        else:
            print(f'La operacion "not" debe utilizar un valor booleano')
            hayerrores = True



# Regla de producción que contempla las operaciones de cambio de signo   
def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    global hayerrores
    p[0] = -p[2]


# Regla de producción que contempla las operaciones que tienen un + delante, como +5 o -(+3)
def p_expression_(p):
    "expression : '+' expression %prec UPLUS"
    global hayerrores
    p[0] = p[2]

# Regla de producción que contempla las operaciones con paréntesis
def p_expression_group(p):
    "expression : '(' expression ')'"
    global hayerrores
    p[0] = p[2]


def p_expression_numero(p):
    "expression : NUMBER"
    p[0] = p[1]

# Reglas de producción que contemplan todas las formas posibles de escribir un valor, es decir, decimal, hexadecimal, octal...
def p_expression_number(p):
    '''expression : CHAR
                  | REAL
                  | BOOL
                  | OCTAL
                  | HEXADECIMAL
                  | BINARIO'''
    global hayerrores
    if type(p[1]) == str:
        # Comprueba si el valor de la expresión es un valor booleano, y lo transforma a su sintaxis de python
        if p[1].lower() == 'cierto' or p[1].lower() == 'falso':
            p[0] = transformador_bool[p[1].lower()]
        # Si no es booleano coge el valor sin comillas
        if p[1].lower() != 'cierto' and p[1].lower() != 'falso':
            p[0] = p[1][1]
    # En cualquier otro caso utiliza el número
    else:
        p[0] = p[1]
# Reglas de producción que contemplan las expresiones como atributos de un registro
def p_expression_registro(p):
    '''expression : NAME "." NAME
                  | NAME "." NAME "[" NUMBER "]"'''
    global hayerrores
    if len(p) == 4:
        # Almacena el nombre del registro y el nombre del atributo
        registro = p[1]
        atributo = p[3]
        # Comprueba que el registro esté declarado
        if registro in names:
            # Comprueba que se esté intentando acceder a un registro
            if names[registro][0] == "registro":
                # Comprueba que el atributo exista
                if atributo in names[registro][1]:
                    if names[registro][1][atributo][0] != 'vector':
                        # Asigna a expression el valor del atributo
                        p[0] = names[registro][1][atributo][1]
                    else:
                        print(f'Error: Se está intentado acceder al atributo "{atributo}" del registro "{registro}" sin utilizar un índice')
                # Si el atributo no existe salta un error
                else:
                    print(f'Error: Atributo "{atributo}" del registro "{registro}" no declarado')
                    hayerrores = True
            # Si la variable no es un registro salta un error
            else:
                print(f'Error: La variable "{registro}" no es un registro')
                hayerrores = True
        # Si el registro no está declarado salta un error
        else:
            print(f'Error: Registro "{registro}" no declarado')
            hayerrores = True
    elif len(p) == 7:
        # Se almacenan el nombre del registro, el nombre del atributo y el índice del vector
        registro = p[1]
        atributo = p[3]
        index = p[5]
        # Comprieba que el registro esté declarado
        if registro in names:
            # Comprueba que se esté intentando acceder a un registro
            if names[registro][0] == "registro":
                # Comprueba que el atributo exista
                if atributo in names[registro][1]:
                    # Comprueba que el atributo sea un vector
                    if names[registro][1][atributo][0] == 'vector':
                        # Comprueba que se esté accediendo a una posición válida del vector
                        if (len(names[registro][1][atributo][2]) - 1) >= index:
                            # Asigna a expression el valor del índice del vector
                            p[0] = names[registro][1][atributo][2][index]
                        # Si se intenta acceder a una posición no válida salta un error
                        else:
                            print(f'Error: Vector "{atributo}" fuera de rango')
                            hayerrores = True
                    # Si la variable no es un vector salta un error
                    else:
                        print(f"Error: La variable '{atributo}' no es un vector")
                        hayerrores = True
                # Si el atributo no existe salta un error
                else:
                    print(f'Error: Atributo "{atributo}" del registro "{registro}" no declarado')
                    hayerrores = True
            # Si la variable no es un registro salta un error
            else:
                print(f'Error: La variable "{registro}" no es un registro')
                hayerrores = True
        # Si el registro no está declarado salta un error
        else:
            print(f'Error: Registro "{registro}" no declarado')
            hayerrores = True

# Regla de producción que contempla las expresiones de longitud de un vector
def p_expression_vector(p):
    '''expression : NAME "." LONG'''
    global hayerrores
    # Almacena el nombre del vector
    variable_name = p[1]
    # Comprueba si la variable está declarada
    if variable_name in names:
        # Comprueba si la variable es un vector
        if names[variable_name][0] == "vector":
            # Iguala expresion a la longitud del vector
            p[0] = len(names[variable_name][2])
        # Si la variable no es un vector salta un error
        else:
            print(f"Error: La variable '{variable_name}' no es un vector")
            hayerrores = True
    # Si la variable no existe salta un error
    else:
        print(f"Error: Variable '{variable_name}' no definida")
        hayerrores = True





# Regla de producción que contempla las expresiones como variables
def p_expression_name(p):
    "expression : NAME"
    global hayerrores
    try:
        p[0] = names[p[1]][1]
        if p[0] == 'entero' or p[0] == 'caracter' or p[0] == 'real' or p[0] == 'booleano':
            print("Error: Se está intentando acceder a un vector sin utilizar un índice")
            hayerrores = True
    except LookupError:
        print("Undefined name '%s'" % p[1])
        hayerrores = True

# Regla de producción que contempla las expresiones como valor del índice de un vector
def p_expression_name_vec(p):
    '''expression : NAME "[" NUMBER "]" '''
    global hayerrores
    # Almacena el nombre y el índice del vector
    variable_name = p[1]
    index = p[3]
    # Comprueba si la variable está declarada
    if variable_name in names:
        # Comprueba si la variable es un vector
        if names[variable_name][0] == "vector":
            # Comprueba si la posición a la que se intenta acceder es válida
            if (len(names[variable_name][2]) - 1) >= index:
                # Guarda en la expresión el valor del índice del vector
                p[0] = names[variable_name][2][index]
            # Si se intenta acceder a una posición no válida salta un error
            else:
                print(f"Error: Índice del vector '{variable_name}' fuera de rango")
                hayerrores = True
        # Si la variable no es un vector salta un error
        else:
            print(f"Error: La variable '{variable_name}' no es un vector")
            hayerrores = True
    # Si la variable no está definida salta un error
    else:
        print(f"Error: Variable '{variable_name}' no definida")
        hayerrores = True



# Regla de producción que contempla los casos de error
def p_error(p):
    global hayerrores
    hayerrores = True
    if p:
        print("Syntax error at '%s'" % p.value)
        
    else:
        print("Syntax error at EOF")



yacc.yacc()