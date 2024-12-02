import os
from math import sqrt
from leerInstancias import cargar_instancia
import pandas as pd

# ==== MODELOS ====
from docplex.mp.model import Model

def modelo_scf(costos, num_depositos, num_clientes, capacidad, demandas):
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

def modelo_dl(costos, num_depositos, num_clientes, capacidad, demandas):
    n = num_depositos + num_clientes
    model = Model(name="DL")

    # Decision variables
    x = model.binary_var_matrix(n, n, name="x")  # Binary decision for arcs

    # Objective function: Minimize total travel cost
    model.minimize(model.sum(costos[i][j] * x[i, j] for i in range(n) for j in range(n)))

    # Each customer is visited exactly once
    for j in range(num_depositos, n):  # For customers only
        model.add_constraint(model.sum(x[i, j] for i in range(n) if i != j) == 1)  # One incoming arc
        model.add_constraint(model.sum(x[j, i] for i in range(n) if i != j) == 1)  # One outgoing arc

    # Vehicle capacity constraints
    for i in range(num_depositos):
        model.add_constraint(model.sum(demandas[j - num_depositos] * x[i, j] for j in range(num_depositos, n)) <= capacidad)

    return model



# ==== RESOLUCIÓN ====
def resolver_modelo(modelo, time_limit):
    try:
        modelo.parameters.timelimit = time_limit
        solucion = modelo.solve(log_output=False)
        return solucion.objective_value
    except Exception as e:
        print(f"Error al resolver el modelo: {e}")
        return None

# ==== EJECUCIÓN PRINCIPAL ====
if __name__ == "__main__":
    DATA_FOLDERS = ["Instancias1", "Instancias2", "Instancias3"]
    TIME_LIMIT = 3600

    resultados = []

    for folder in DATA_FOLDERS:
        archivos = [f for f in os.listdir(folder) if f.endswith(".dat")]

        for idx, archivo in enumerate(archivos, start=1):
            print(f"Procesando instancia {idx}: {archivo} en carpeta {folder}")
            file_path = os.path.join(folder, archivo)
            result = cargar_instancia(file_path)

            if result is None:
                print(f"Error al cargar la instancia {archivo}. Saltando...")
                continue

            costos, num_depositos, num_clientes, capacidad, demandas = result

            print(f"Instancia {idx}: {archivo}")
            print(f"  Número de depósitos: {num_depositos}")
            print(f"  Número de clientes: {num_clientes}")
            print(f"  Tamaño de la matriz de costos: {len(costos)}x{len(costos[0])}")

            print("Resolviendo modelo SCF...")
            try:
                modelo = modelo_scf(costos, num_depositos, num_clientes, capacidad, demandas)
                resultado_scf = resolver_modelo(modelo, TIME_LIMIT)
                print(f"Resultados de la instancia {idx} (SCF): {resultado_scf}")
                resultados.append((archivo, "SCF", resultado_scf))
            except Exception as e:
                print(f"Error al resolver la instancia {archivo} (SCF): {e}")

            print("Resolviendo modelo DL...")
            try:
                modelo = modelo_dl(costos, num_depositos, num_clientes, capacidad, demandas)
                resultado_dl = resolver_modelo(modelo, TIME_LIMIT)
                print(f"Resultados de la instancia {idx} (DL): {resultado_dl}")
                resultados.append((archivo, "DL", resultado_dl))
            except Exception as e:
                print(f"Error al resolver la instancia {archivo} (DL): {e}")

    # Generar reporte en Excel
    df = pd.DataFrame(resultados, columns=["Archivo", "Modelo", "Resultado"])
    df.to_excel("resultados.xlsx", index=False)

    print("\n--- Resultados Finales ---")
    for idx, (archivo, modelo, resultado) in enumerate(resultados, start=1):
        print(f"Instancia {idx} ({archivo}, {modelo}): {resultado}")