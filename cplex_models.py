from docplex.mp.model import Model

def modelo_scf_cplex(costos, num_depositos, num_clientes, capacidad, demandas):
    n = num_depositos + num_clientes
    model = Model(name="SCF")

    # Decision variables
    x = model.binary_var_matrix(n, n, name="x")  # Binary decision for arcs
    u = model.continuous_var_list(n, name="u")  # Continuous flow variables

    # Objective function: Minimize total travel cost
    model.minimize(model.sum(costos[i][j] * x[i, j] for i in range(n) for j in range(n)))

    # Each customer is visited exactly once
    for j in range(num_depositos, n):  # For customers only
        model.add_constraint(model.sum(x[i, j] for i in range(n) if i != j) == 1)  # Exactly one incoming arc
        model.add_constraint(model.sum(x[j, i] for i in range(n) if i != j) == 1)  # Exactly one outgoing arc

    # Flow constraints to ensure correct cumulative load
    for i in range(num_depositos, n):
        for j in range(num_depositos, n):
            if i != j:
                model.add_constraint(u[i] + demandas[j - num_depositos] * x[i, j] <= u[j] + capacidad * (1 - x[i, j]))

    # Capacity constraints
    for i in range(num_depositos, n):
        model.add_constraint(u[i] >= demandas[i - num_depositos])  # At least the customer's demand
        model.add_constraint(u[i] <= capacidad)  # At most vehicle capacity

    # Set flow at depots to 0
    for i in range(num_depositos):
        model.add_constraint(u[i] == 0)

    return model

def modelo_dl_cplex(costos, num_depositos, num_clientes, capacidad, demandas):
    n = num_depositos + num_clientes
    model = Model(name="DL")

    # Variables de decisión
    x = model.binary_var_matrix(n, n, name="x")  # 1 si se usa el arco (i, j)
    u = model.continuous_var_list(n, name="u")  # Carga acumulada en el nodo

    # Función objetivo: Minimizar costo total
    model.minimize(model.sum(costos[i][j] * x[i, j] for i in range(n) for j in range(n)))

    # Restricción: Cada cliente debe ser visitado exactamente una vez
    for j in range(num_depositos, n):  # Clientes
        model.add_constraint(model.sum(x[i, j] for i in range(n) if i != j) == 1)  # Un arco entrante
        model.add_constraint(model.sum(x[j, i] for i in range(n) if i != j) == 1)  # Un arco saliente

    # Restricción: Salida y entrada a depósitos
    for i in range(num_depositos):
        model.add_constraint(model.sum(x[i, j] for j in range(num_depositos, n)) <= 1)  # Salida máxima 1 vehículo
        model.add_constraint(model.sum(x[j, i] for j in range(num_depositos, n)) <= 1)  # Entrada máxima 1 vehículo

    # Restricción de capacidad y eliminación de subtours (Miller-Tucker-Zemlin)
    for i in range(num_depositos, n):  # Clientes
        model.add_constraint(u[i] >= demandas[i - num_depositos])  # Demanda mínima del cliente
        model.add_constraint(u[i] <= capacidad)  # No exceder capacidad
        for j in range(num_depositos, n):  # Clientes
            if i != j:
                model.add_constraint(
                    u[i] + demandas[j - num_depositos] * x[i, j] <= u[j] + capacidad * (1 - x[i, j])
                )

    # Carga en los depósitos es cero
    for i in range(num_depositos):
        model.add_constraint(u[i] == 0)

    return model