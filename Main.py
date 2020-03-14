from Funzioni import *

# Importiamo il Dataset
dataset = ApriDataset(15000)
num_var = dataset.shape[1]

# Creo il grafo
G = DiGraph()
for i in range(0, num_var):
    G.add_node(dataset[0][i])

# Effettuo la ricerca locale (Greedy)
print("numero variabili: ", num_var)
HillClimbing(G, dataset)