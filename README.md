# CliqueCoverToSAT

## **Problem Description**
A **clique** is a subset of vertices of an undirected graph such that every two distinct vertices in the clique are adjacent. My script solves a **Clique Cover** problem by encoding it as a SAT problem in CNF (Conjunctive Normal Form) and solving it using a SAT solver.
### **Problem Parameters**
- A graph G = (V, E), where V is the set of vertices and E is the set of edges.
- Number of cliques (k), where the goal is to partition V into k disjoint cliques such that each vertex belongs to exactly one clique, and non-adjacent vertices do not belong to the same clique.
### **Constraints**
1. Each vertex must belong to exactly one clique.
2. Non-adjacent vertices cannot belong to the same clique.

## **CNF Encoding**
### **Propositional Variables**
We define a propositional variable x_{i, j} where **i** is the vertex index (i = 1, 2, ..., |V|) and **j** is the clique index (j = 1, 2, ..., k). 
A variable x_{i, j} = 1 if and only if vertex **i** belongs to clique **j**. 
### **Clauses**
1. Each vertex must belong to at least one clique: x_{i, 1} OR x_{i, 2} OR ... OR x_{i, k}
2. Each vertex belongs to at most one clique: NOT x_{i,j1} OR NOT x_{i,j2} where j1 != j2
3. Non-adjacent vertices cannot belong to the same clique: NOT x_{i1,j} OR NOT x_{i2,j} for all non-adjacent i1, i2

## **User Documentation**
### **Input Format**
The input is a text file that specifies the graph. Comments can be added using `#`.
#### Example Input (`graph.in`):
```
# Graph example
3
1 2
2 3
3 1
```

1. The first line (`3`) specifies the number of vertices.
2. Each subsequent line (`1 2`, `2 3`, `3 1`) specifies an edge between two vertices.
### **Output Format**
1. A DIMACS CNF file (by default `formula.cnf`) is generated, which encodes the problem as a SAT instance.
2. The script runs the SAT solver and outputs:
   - **SATISFIABLE**: Prints the clique cover solution (e.g., vertices in each clique).
   - **UNSATISFIABLE**: Indicates that the graph cannot be partitioned into \( k \) cliques.

## **How to Use**
Run the script using the following arguments:
- `-i / --input`: Input graph file (required).
- `-o / --output`: Output CNF file name (default: `formula.cnf`).
- `-k`: Number of cliques (required).
- `-s / --solver`: Path to the SAT solver executable (default: `./glucose`).
- `-v / --verbose`: Show full solver statistics and output (optional).
  
One example of a possible command can be:

`python main.py -i graph.in -o formula.cnf -k 2 -s ./glucose -v`

## **Attached Instances Description**
1. 'small_instance_SAT.in' provides an example of a small humanly readable instance, which is **satisfiable** for any k more than 2.
2. 'small_instance_UNSAT.in' provides an example of a small humanly readable instance, which is **unsatisfiable** for k = 1.
3. 'nontrivial_instance_SAT.in' provides a large input graph, which is **satisfiable** for k = 170. Since input is large, a wall-clock time (time waited to see results) is **16.82 s**

### **Further Experiments**
After doing more tests, my overall observation is that when large input file is given, it takes singnificantly long time for the script to determine that instance is unsatisfiable. Moreover, in most cases large instances are unsatisfiable for a small clique numbers. Therefore, if a small clique number is given with a large input, and instance is unsatisfiable, it will take more than 30-40 minutes for the script to run.

Based on these results, it is more efficient to provide larger clique numbers as input, and decrease it with each test to find minimum clique number. 
