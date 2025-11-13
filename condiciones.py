# #? CONDIFCIONES IF

# EJERCICIO BASICO ( NUMERO POSITIVO, NEGATIVO O CERO)
# num1 = int(input("Ingrese un número para determinar si es positivo, negativo o cero: "))
# if num1 > 0: # if (condicion):
#     print("El número es positivo.") # SE EJECUTA SI LA CONDICION ES VERDADERA
# elif num1 == 0: # if (condicion):  ( = -> ASIGNACIÓN ) ( PARA CONDICIONES EXACTAS SE DEBE USAR == )
#     print("El número es cero.")
# else: # ELSE:
#     # CONDICION FALSA
#     print("El número es negativo")

# if num1 >= 0:
#     print("El número es positivo o cero")
# else:
#     print("El número es negativo")

# # < > == (<= >= !=)

# nombre = input("Ingrese su nombre: ")

# if nombre != 'Carlos':
#     print("Menos mal no es el carlos")

# if nombre == 'Carlos':
#     print("No me lo deje ingresar")
#     nombre = 'Daniel'
#     print("Su nombre ha sido cambiado a:", nombre)
# else:
#     print("Menos mal no es el carlos")

# 20 % 2 == 0

# if 20 % 2 == 0:
#     print("20 es un número par")



# lista_nombre = [] # CREAR UNA LISTA VACIA
# lista_nombre = ['Angelo','Carlos','Daniel','Elena','Fernando'] # CREAR UNA LISTA CON ELEMENTOS

# print(lista_nombre[0])
# print(lista_nombre[1])
# print(lista_nombre[2])
# print(lista_nombre[3])
# print(lista_nombre[4])


# for n in range(1, 11): # RANGE ( INICIO [0], FIN-1 )
#     print(n)



# numeros_list = [2,4,6,8,10]
# for n in numeros_list:
#     print("\n",n)


#? IMPRIMA UNA PALABRA N VECES
# 
palabra = input('Ingrese una palabra: ')

veces = int(input('Ingrese el número de veces que quiere que se repita la palabra: '))

for n in range(veces):
    print(palabra)