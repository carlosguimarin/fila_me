from src.fila_me.database.banco import registrar_ticket


numero_ticket = 123456

foi_registrado = registrar_ticket(numero_ticket)

if foi_registrado:
    print("Ticket novo registrado.")
else:
    print("Ticket já existia no banco.")