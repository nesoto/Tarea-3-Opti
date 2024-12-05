import os
from leerInstancias import cargar_instancia
import pandas as pd
import time

# ==== MODELOS ====
from cplex_models import modelo_scf_cplex, modelo_dl_cplex
from gurobi_models import modelo_scf_gurobi, modelo_dl_gurobi


# ==== RESOLUCIÓN ====
def resolver_modelo(modelo, tiempo_limite):
    modelo.setParam("TimeLimit", tiempo_limite)
    modelo.optimize()

    if modelo.status == GRB.OPTIMAL:
        return modelo.objVal, modelo.NumVars, modelo.NumConstrs
    else:
        return None, modelo.NumVars, modelo.NumConstrs

# ==== EJECUCIÓN PRINCIPAL ====
def resolver_modelo(modelo, tiempo_limite):
    modelo.setParam("TimeLimit", tiempo_limite)
    modelo.optimize()

    if modelo.status == GRB.OPTIMAL:
        return modelo.objVal, modelo.NumVars, modelo.NumConstrs
    else:
        return None, modelo.NumVars, modelo.NumConstrs

# ==== EJECUCIÓN PRINCIPAL ====
if __name__ == "__main__":
    DATA_FOLDERS = ["Instancias1", "Instancias2", "Instancias3"]
    TIME_LIMIT = 1800

    resultados_cplex = []
    resultados_gurobi = []

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

            # Resolviendo modelo SCF
            print("Resolviendo modelo SCF...")
            try:
                # Usando CPLEX
                start_time = time.time()
                modelo = modelo_scf_cplex(costos, num_depositos, num_clientes, capacidad, demandas)
                resultado_scf, num_vars, num_constrs = resolver_modelo(modelo, TIME_LIMIT)
                end_time = time.time()
                elapsed_time_scf = end_time - start_time
                print(f"Resultados de la instancia {idx} (SCF) en CPLEX: {resultado_scf}")
                print(f"  Variables: {num_vars}, Restricciones: {num_constrs}")
                resultados_cplex.append((archivo, "SCF", resultado_scf, elapsed_time_scf, num_vars, num_constrs))

                # Usando Gurobi
                start_time = time.time()
                modelo = modelo_scf_gurobi(costos, num_depositos, num_clientes, capacidad, demandas)
                resultado_scf, num_vars, num_constrs = resolver_modelo(modelo, TIME_LIMIT)
                end_time = time.time()
                elapsed_time_scf = end_time - start_time
                print(f"Resultados de la instancia {idx} (SCF) en Gurobi: {resultado_scf}")
                print(f"  Variables: {num_vars}, Restricciones: {num_constrs}")
                resultados_gurobi.append((archivo, "SCF", resultado_scf, elapsed_time_scf, num_vars, num_constrs))
            except Exception as e:
                print(f"Error al resolver la instancia {archivo} (SCF): {e}")

            # Resolviendo modelo DL
            print("Resolviendo modelo DL...")
            try:
                # Usando CPLEX
                start_time = time.time()
                modelo = modelo_dl_cplex(costos, num_depositos, num_clientes, capacidad, demandas)
                resultado_dl, num_vars, num_constrs = resolver_modelo(modelo, TIME_LIMIT)
                end_time = time.time()
                elapsed_time_dl = end_time - start_time
                print(f"Resultados de la instancia {idx} (DL) en CPLEX: {resultado_dl}")
                print(f"  Variables: {num_vars}, Restricciones: {num_constrs}")
                resultados_cplex.append((archivo, "DL", resultado_dl, elapsed_time_dl, num_vars, num_constrs))

                # Usando Gurobi
                start_time = time.time()
                modelo = modelo_dl_gurobi(costos, num_depositos, num_clientes, capacidad, demandas)
                resultado_dl, num_vars, num_constrs = resolver_modelo(modelo, TIME_LIMIT)
                end_time = time.time()
                elapsed_time_dl = end_time - start_time
                print(f"Resultados de la instancia {idx} (DL) en Gurobi: {resultado_dl}")
                print(f"  Variables: {num_vars}, Restricciones: {num_constrs}")
                resultados_gurobi.append((archivo, "DL", resultado_dl, elapsed_time_dl, num_vars, num_constrs))
            except Exception as e:
                print(f"Error al resolver la instancia {archivo} (DL): {e}")

    # Generar reporte en Excel
    df_cplex = pd.DataFrame(resultados_cplex, columns=["Archivo", "Modelo", "Resultado", "Tiempo (s)", "Variables", "Restricciones"])
    df_cplex.to_excel("resultados_cplex.xlsx", index=False)

    df_gurobi = pd.DataFrame(resultados_gurobi, columns=["Archivo", "Modelo", "Resultado", "Tiempo (s)", "Variables", "Restricciones"])
    df_gurobi.to_excel("resultados_gurobi.xlsx", index=False)

    print("\n--- Resultados Finales ---")
    print("Resultados de CPLEX:")
    for idx, (archivo, modelo, resultado, tiempo, vars_, constrs) in enumerate(resultados_cplex, start=1):
        print(f"Instancia {idx} ({archivo}, {modelo}): Resultado={resultado}, Tiempo={tiempo:.2f} segundos, Variables={vars_}, Restricciones={constrs}")
    print("Resultados de Gurobi:")
    for idx, (archivo, modelo, resultado, tiempo, vars_, constrs) in enumerate(resultados_gurobi, start=1):
        print(f"Instancia {idx} ({archivo}, {modelo}): Resultado={resultado}, Tiempo={tiempo:.2f} segundos, Variables={vars_}, Restricciones={constrs}"
