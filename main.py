import time
import subprocess
from argparse import ArgumentParser

def read_graph(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines if not line.strip().startswith("#") and line.strip()]

    vertex_count = int(lines[0]) 
    edges = [tuple(map(int, line.split())) for line in lines[1:]] 
    
    return vertex_count, edges

def encode(vertex_count, edges, k):
    clauses = []
    num_variables = vertex_count * k

    def variable(i, j):
        return (i - 1) * k + j

    #First condition is for each vertex to belong to at least one clique
    for i in range(1, vertex_count + 1):
        clause = [variable(i, j) for j in range(1, k + 1)]
        clauses.append(clause)
    
    #Second condition is for each vertex to belong to at most one clique
    for i in range(1, vertex_count + 1):
        for j_1 in range(1, k + 1):
            for j_2 in range(j_1 + 1, k + 1):
                clauses.append([-variable(i, j_1), -variable(i, j_2)])
    
    #Third condition is that non-adjacent vertices cannot be in the same clique 
    for i in range(1, vertex_count + 1):
        for j in range(1, vertex_count + 1):
            if i !=j and (i, j) not in edges and (j, i) not in edges:
                for c in range(1, k + 1):
                    clauses.append([-variable(i, c), -variable(j, c)])
    
    num_clauses = len(clauses)
    cnf = f"p cnf {num_variables} {num_clauses}\n"
    cnf += "\n".join(" ".join(map(str, clause)) + " 0" for clause in clauses)

    return cnf

def call_solver(cnf_file, solver_name):
    try:
        command = [solver_name, '-model', cnf_file]
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout
    except FileNotFoundError:
        print("Error: SAT solver was not found.")
        return None
    except subprocess.CalledProcessError as e:
        print("Error: Solver has encountered an error.")
        print(f"Details: {e.stderr}")
        return None
    
def decode_solution(solution, k):
    solution_lines = solution.splitlines()
    model = solution_lines[len(solution_lines) - 1]

    if not model:
        print("Error: No model found in the SAT solver output")
        return None

    variables = list(map(int, model.split()[1:]))
    clique_cover = [[] for _ in range(k)]

    for var in variables:
        if var > 0:
            i = (var - 1) // k + 1
            c = (var - 1) % k
            clique_cover[c].append(i)
    
    return [clique for clique in clique_cover if clique]

def print_output(result, k, verbose):
    if "UNSAT" in result:
        if verbose:
            print(result)
            return
        print("Result: UNSATISFIABLE")
    elif "SAT" in result:
        if verbose:
            print(result)
        else:
            print("Result: SATISFIABLE")

        decoded_solution = decode_solution(result, k)

        if decoded_solution is not None:
            for idx, clique in enumerate(decoded_solution):
                print(f"Clique {idx + 1}: {clique}")
    else:
        print("Error: Unexpected SAT solver output")
        print(result)

def main():
    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help=("File containing a graph."),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=("Output file for the DIMACS format (i.e. the CNF formula)."),
    )
    parser.add_argument(
        "-k",
        type=int,
        required=True,
        help=("Number of cliques."),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="./glucose",
        help=("The SAT solver to be used."),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="Show full solver statistics and detailed output.",
    )

    args = parser.parse_args()

    vertex_count, edges = read_graph(args.input)
    cnf = encode(vertex_count, edges, args.k)

    with open(args.output, 'w') as f:
        f.write(cnf)
    print(f"CNF formula written to {args.output}")
    
    result = call_solver(args.output, args.solver)
    if result is None:
        print("Error: Solver execution failed.")
        return
    
    print_output(result, args.k, args.verbose)

if __name__ == "__main__":
   main()