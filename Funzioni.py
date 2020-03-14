from networkx import *
from numpy import *
import matplotlib.pyplot as plt
from math import *
import sys


# funzione che importa il dataset
def ApriDataset(casi):
    file = open('Asia.txt')
    text = file.read().split('\n')
    text = array(text)

    stringa = str(text[0])
    if stringa.count(',') > 1:
        text = array([l.split(',') for l in text])
    else:
        text = array([l.split('\t') for l in text])
    file.close()

    if casi != 'default':
        text = split(text, [0, casi + 1])
        text = text[1]

    return text


# funzione che restituisce l'indice del nodo nel dataset Asia
def datasetIndice(nodo, dataset):
    indice = 0
    while (dataset[0][indice] != nodo):
        indice += 1
    return indice


# funzione che restituisce il numero di stati del nodo nel dataset = 2
def Ri(nodo, dataset):
    temp = set()
    indice = datasetIndice(nodo, dataset)

    for i in range(1, dataset.shape[0]):
        temp.add(dataset[i][indice])

    return len(temp)


# creo una classe che è utile per il calcolo della formula
class Oggetto():
    configurazione = ''  # combinazione nel dataset
    num_istanze = 1  # occorrenza di tale combinazione nel dataset


# funzione che esegue la formula di Cooper & Herskovits
def Formula(G, nodo, dataset, Ri, ArrayIndex):
    # creo un newDataset con solo Nodo + padri
    newdataset = dataset[:, [ArrayIndex[nodo]]]  # aggiungo la colonna relativa al nodo
    for n in G.predecessors(nodo):
        newdataset = column_stack([newdataset, dataset[:, ArrayIndex[n]]])

    '''
    Adesso creo due insiemi
        1) Per la prima sommatoria:
           padri[] = vettore di oggetti che hanno per nome una configurazione dei padri del nodo 
                sottoforma di stringa e il numero di istanze di tale configurazione

        2) Per la seconda sommatoria:
           padri_e_figlio[] = vettore di oggetti che hanno per nome una configurazione di padri+figlio
                         sottoforma di stringa e il numero di istanze di tale configurazione
    '''
    padri = []
    padri_e_figlio = []

    for i in range(1, newdataset.shape[0]):
        configurazione = ''
        for j in range(1, newdataset.shape[1]):
            configurazione = configurazione + newdataset[i][j]  # concateno le righe dei padri

        found = 0
        for ogg in padri:
            if ogg.configurazione == configurazione:
                found = 1
                ogg.num_istanze += 1
                break

        if (found == 0):
            ogg = Oggetto()
            ogg.configurazione = configurazione
            padri.append(ogg)

        configurazione = configurazione + newdataset[i][0]  # aggiungo la configurazione del figlio

        found = 0
        for ogg in padri_e_figlio:
            if ogg.configurazione == configurazione:
                found = 1
                ogg.num_istanze = ogg.num_istanze + 1
                break
        if found == 0:
            ogg = Oggetto()
            ogg.configurazione = configurazione
            padri_e_figlio.append(ogg)

    # fine for

    # Calcolo della Prima Sommatoria
    fattore = len(padri) * log(factorial(Ri - 1))

    # Calcolo della seconda sommatoria
    for obj in padri:
        fattore = fattore - log(factorial(obj.num_istanze + Ri - 1))

    # Calcolo della terza sommatoria
    for obj in padri_e_figlio:
        fattore = fattore + log(factorial(obj.num_istanze))

    return -fattore


# Hill-Climbing
def HillClimbing(G, dataset):
    '''
       Inizzializzaizone: Creo tre insiemi tramite la funzione get_node_attribute (networkx library):
          ArrayIndex[u]=indice del nodo "u" nel dataset
          ArrayScore[u]=fattore di score riferito al nodo "u" (data la rete corrente e il dataset)
          ArrayRi[u]=numero di valori che assume il nodo "u" nel dataset
    '''

    tmp_set = DiGraph()  # creo un grafo dove ogni nodo ha tre attributi (index, score, Ri)

    for n in G.nodes():
        index_nodo = datasetIndice(n, dataset)
        tmp_set.add_node(n, index=index_nodo)

    ArrayIndex = get_node_attributes(tmp_set, 'index')

    c = 0
    for n in G.nodes():
        Ri_nodo = Ri(n, dataset)
        tmp_set.add_node(n, score=Formula(G, n, dataset, Ri_nodo, ArrayIndex))
        c = c + 1

    ArrayScore = get_node_attributes(tmp_set, 'score')

    for n in G.nodes():
        Ri_nodo = Ri(n, dataset)
        tmp_set.add_node(n, Ri=Ri_nodo)

    ArrayRi = get_node_attributes(tmp_set, 'Ri')

    # Ottengo lo Score della rete sommando tutti i valori di ArrayScore
    best_score = 0
    for n in G.nodes():
        best_score += ArrayScore[n]

    sys.stdout.write('\r')
    print("score iniziale = ", best_score)
    print("Eseguo l'Hill Climbing: ")
    num_iterazioni = 0  # tengo conto dei passi
    tipo = 'tipo di operazione elementare'

    # Ricerca locale per i grafi orientati
    while (tipo != 'not found'):
        tipo = 'not found' #quando lo score non cambia per la prima volta
        c = 0
        print(' ')
        first_score = best_score

        # ciclo in tutti gli archi
        for (u, v) in G.edges():
            c = c + 1
            G.remove_edge(u, v)  # RIMUOVE
            tmp_score = first_score - ArrayScore[v] + Formula(G, v, dataset, ArrayRi[v], ArrayIndex)

            # Controllo lo Score
            if tmp_score < best_score:
                best_score = tmp_score
                padre = u
                figlio = v
                tipo = 'rem'

            G.add_edge(v, u)  # INVERTE
            if is_directed_acyclic_graph(G) == True:
                tmp_score = tmp_score - ArrayScore[u] + Formula(G, u, dataset, ArrayRi[u], ArrayIndex)
                if tmp_score < best_score:
                    best_score = tmp_score
                    padre = u
                    figlio = v
                    tipo = 'rev'
            G.add_edge(u, v)
            G.remove_edge(v, u)
        # fine ciclo

        comp = list(complement(G).edges())
        for (u, v) in complement(G).edges():
            if (v, u) in G.edges():
                c = c + 1
                comp.remove((u, v))

        for (u, v) in comp:  # AGGIUNGE
            G.add_edge(u, v)
            c = c + 1
            if is_directed_acyclic_graph(G) == True:
                tmp_score = first_score - ArrayScore[v] + Formula(G, v, dataset, ArrayRi[v], ArrayIndex) #score della rete
                if tmp_score < best_score:
                    best_score = tmp_score
                    tipo = 'add'
                    padre = u
                    figlio = v
            G.remove_edge(u, v)

        if (tipo == 'rem'):
            G.remove_edge(padre, figlio)
            ArrayScore[figlio] = best_score - first_score + ArrayScore[figlio]

        elif (tipo == 'rev'):
            G.add_edge(figlio, padre)
            G.remove_edge(padre, figlio)
            ArrayScore[figlio] = Formula(G, figlio, dataset, ArrayRi[figlio], ArrayIndex)
            ArrayScore[padre] = Formula(G, padre, dataset, ArrayRi[padre], ArrayIndex)

        elif (tipo == 'add'):
            G.add_edge(padre, figlio)
            ArrayScore[figlio] = best_score - first_score + ArrayScore[figlio]

        if (tipo != 'not found'):
            num_iterazioni = num_iterazioni + 1
            stringa = "Passo " + str(num_iterazioni) + ': score= ' + str(best_score)
            stringa = stringa + '   ' + tipo + " (" + str(padre) + ")->(" + str(figlio) + ")"
            sys.stdout.write('\r' + stringa)
    # fine While

    draw(G, with_labels=True);
    plt.savefig("grafo.png");

    sys.stdout.write('\r' + ' ')
    print("FINAL SCORE= ", best_score)