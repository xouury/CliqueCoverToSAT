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

    args = parser.parse_args()

    vertex_count, edges = read_graph(args.input)
    cnf = encode(vertex_count, edges, args.k)

    with open(args.output, 'w') as f:
        f.write(cnf)
    print(f"CNF formula written to {args.output}")

if __name__ == "__main__":
   main()

