from gurobipy import Model, GRB

def modelo_scf_gurobi(costos, num_depositos, num_clientes, capacidad, demandas):
    """
    Implementación del modelo SCF (Single Commodity Flow) en Gurobi.
    """
    n = num_depositos + num_clientes
    model = Model("SCF")

    # Variables
    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")  # Arcos binarios
    u = model.addVars(n, vtype=GRB.CONTINUOUS, name="u")  # Flujo continuo

    # Función objetivo: minimizar el costo total
    model.setObjective(
        sum(costos[i][j] * x[i, j] for i in range(n) for j in range(n)), GRB.MINIMIZE
    )

    # Restricciones
    # Cada cliente es visitado exactamente una vez
    for j in range(num_depositos, n):  # Clientes
        model.addConstr(sum(x[i, j] for i in range(n) if i != j) == 1, name=f"in_{j}")
        model.addConstr(sum(x[j, i] for i in range(n) if i != j) == 1, name=f"out_{j}")

    # Restricciones de flujo
    for i in range(num_depositos, n):
        for j in range(num_depositos, n):
            if i != j:
                model.addConstr(
                    u[i] + demandas[j - num_depositos] * x[i, j] <= u[j] + capacidad * (1 - x[i, j]),
                    name=f"flow_{i}_{j}"
                )

    # Capacidad mínima y máxima de los nodos
    for i in range(num_depositos, n):
        model.addConstr(u[i] >= demandas[i - num_depositos], name=f"min_capacity_{i}")
        model.addConstr(u[i] <= capacidad, name=f"max_capacity_{i}")

    # Flujo en los depósitos es cero
    for i in range(num_depositos):
        model.addConstr(u[i] == 0, name=f"depot_flow_{i}")

    return model

def modelo_dl_gurobi(costos, num_depositos, num_clientes, capacidad, demandas):
    """
    Implementación del modelo DL (Improved Miller-Tucker-Zemlin) en Gurobi.
    """
    n = num_depositos + num_clientes
    model = Model("DL")

    # Variables
    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")  # Arcos binarios
    u = model.addVars(n, vtype=GRB.CONTINUOUS, name="u")  # Carga acumulada

    # Función objetivo: minimizar el costo total
    model.setObjective(
        sum(costos[i][j] * x[i, j] for i in range(n) for j in range(n)), GRB.MINIMIZE
    )

    # Restricciones
    # Cada cliente es visitado exactamente una vez
    for j in range(num_depositos, n):  # Clientes
        model.addConstr(sum(x[i, j] for i in range(n) if i != j) == 1, name=f"in_{j}")
        model.addConstr(sum(x[j, i] for i in range(n) if i != j) == 1, name=f"out_{j}")

    # Salidas y entradas a depósitos
    for i in range(num_depositos):
        model.addConstr(sum(x[i, j] for j in range(num_depositos, n)) <= 1, name=f"depot_out_{i}")
        model.addConstr(sum(x[j, i] for j in range(num_depositos, n)) <= 1, name=f"depot_in_{i}")

    # Restricciones de capacidad y eliminación de subtours (MTZ)
    for i in range(num_depositos, n):  # Clientes
        model.addConstr(u[i] >= demandas[i - num_depositos], name=f"min_load_{i}")
        model.addConstr(u[i] <= capacidad, name=f"max_load_{i}")
        for j in range(num_depositos, n):  # Clientes
            if i != j:
                model.addConstr(
                    u[i] + demandas[j - num_depositos] * x[i, j] <= u[j] + capacidad * (1 - x[i, j]),
                    name=f"mtz_{i}_{j}"
                )

    # Flujo en los depósitos es cero
    for i in range(num_depositos):
        model.addConstr(u[i] == 0, name=f"depot_flow_{i}")

    return model

