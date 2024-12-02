import math

def cargar_instancia(file):
    try:
        with open(file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]  # Remove blank lines
    except FileNotFoundError:
        print(f"Error: The file {file} was not found.")
        return None
    except IOError:
        print(f"Error: An I/O error occurred while reading the file {file}.")
        return None

    try:
        # Parse the number of customers and depots
        num_customers = int(lines[0])
        num_depots = int(lines[1])

        # Parse the coordinates for depots
        depot_coords = []
        for i in range(num_depots):
            parts = lines[2 + i].split()
            if len(parts) != 2:
                raise ValueError(f"Expected 2 values for depot coordinates, got {len(parts)}")
            x, y = map(float, parts)
            depot_coords.append((x, y))

        # Parse the coordinates for customers
        customer_coords = []
        for i in range(num_customers):
            parts = lines[2 + num_depots + i].split()
            if len(parts) != 2:
                raise ValueError(f"Expected 2 values for customer coordinates, got {len(parts)}")
            x, y = map(float, parts)
            customer_coords.append((x, y))

        # Parse the vehicle capacity
        vehicle_capacity = int(lines[2 + num_depots + num_customers])

        # Parse the depot capacities (skipping this as per your description)
        depot_capacities = []
        for i in range(num_depots):
            depot_capacities.append(int(lines[3 + num_depots + num_customers + i]))

        # Parse the customer demands
        customer_demands = []
        for i in range(num_customers):
            customer_demands.append(int(lines[3 + 2 * num_depots + num_customers + i]))

        # Parse the cost type (0 or 1)
        cost_type = int(lines[4 + 3 * num_depots + 2 * num_customers])

        # Calculate the distance matrix
        all_coords = depot_coords + customer_coords
        n = len(all_coords)
        costs = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                xA, yA = all_coords[i]
                xB, yB = all_coords[j]
                distance = math.sqrt((xA - xB) ** 2 + (yA - yB) ** 2)
                if cost_type == 0:
                    costs[i][j] = int(distance * 100)
                else:
                    costs[i][j] = distance

        return costs, num_depots, num_customers, vehicle_capacity, customer_demands
    except (ValueError, IndexError) as e:
        print(f"Error: An error occurred while parsing the file {file}. Details: {e}")
        return None