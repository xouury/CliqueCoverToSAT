import time
import subprocess
from argparse import ArgumentParser

def read_graph(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    vertex_count = int(lines[0].strip())
    edges = [tuple(map(int, line.strip().split())) for line in lines[1:]]
    
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
            if i != j and (i, j) not in edges and (j, i) not in edges:
                for c in range(1, k + 1):
                    clauses.append([-variable(i, c), -variable(j, c)])
    
    num_clauses = len(clauses)
    cnf = f"p cnf {num_variables} {num_clauses}\n"
    cnf += "\n".join(" ".join(map(str, clause)) + " 0" for clause in clauses)

    return cnf

def call_solver(cnf_file, solver_name, verbose):
    try:
        command = f"{solver_name} {'-verb=0' if not verbose else ''} {cnf_file}"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        print("no file")
        return None
    except subprocess.CalledProcessError:
        print("problem with processing")
        return None

    return result.stdout

def decode_solution(solution, k):
    cliques = [[] for _ in range(k)]
    
    for var in solution:
        if var > 0:
            i = (var - 1) // k + 1
            c = (var - 1) % k
            cliques[c].append(i)

    return [clique for clique in cliques if clique]

def print_output(result, k):
    if "UNSAT" in result:
        print("Result: UNSATISFIABLE")
    elif "SAT" in result:
        print("Result: SATISFIABLE")

        solution = [int(x) for x in result.splitlines() if x.strip() and x[0].isdigit()][0]
        decoded_solution = decode_solution(solution, k)

        for idx, clique in enumerate(decoded_solution):
            print(f"Clique {idx + 1}: {clique}")

def main():
    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default = "input.in",
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
        action="store_true",
        help="Show full solver statistics and detailed output.",
    )

    args = parser.parse_args()

    vertex_count, edges = read_graph(args.input)
    cnf = encode(vertex_count, edges, args.k)

    with open(args.output, 'w') as f:
        f.write(cnf)
    
    result = call_solver(args.output, args.solver, args.verbose)
    print(result)

    print(f"CNF formula written to {args.output}")

if __name__ == "main":
   main()