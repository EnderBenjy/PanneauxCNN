import json
import random
import sys
import time
import pickle

from activation_functions import *
from cost_functions import *
from layers import *

import numpy as np


# Main class
class Network(object):

    def __init__(self, layers: list, cost=QuadraticCost2, activation_func=tanh):
        """
            layers = [Layer1, Layer2, ...],
            cost = fonction cout a utiliser,
            activation_func = fonction sortie neurone
        """
        self.layers = layers
        self.num_layers = len(layers)
        self.cost = cost
        self.activation = activation_func

    def feedforward(self, entree):
        """
        Renvoie la sortie pour un vecteur d'entree a
        """
        sortie = entree
        for layer in self.layers:
            sortie = layer.feedforward(sortie)
        return sortie

    def train(self, loader, epochs=1, eta=2,
              test_accuracy=False, train_accuracy=False,
              mini_batch_size=20):

        train, test = loader()
        monitor = ([], [])  # train, test
        start = time.time()

        if train_accuracy: monitor[0].append(self.accuracy(train, '(train)'))
        if test_accuracy: monitor[1].append(self.accuracy(test, '(test)'))

        for epoch in range(epochs):

            # train, test = loader()
            n_train = len(train)
            print(f'Epoch {epoch + 1} started...')

            random.shuffle(train)
            batches = [
                train[k:k + mini_batch_size]
                for k in range(0, n_train, mini_batch_size)]

            monitor_batch = 0 #
            for batch in batches:
                if monitor_batch % 100 == 0: #
                    print(monitor_batch) #
                self.train_batch(batch, eta)
                monitor_batch += 1 #
            print(f"\nEntrainement epoch {epoch + 1} fini")
            print(f"Only required {time.time() - start:.2f}s")

            if train_accuracy: monitor[0].append(self.accuracy(train, '(train)'))
            if test_accuracy: monitor[1].append(self.accuracy(test, '(test)'))

        return train_accuracy, test_accuracy

    def train_batch(self, batch, eta):
        batch_size = len(batch)
        for couple in batch:
            image, label = couple
            output = self.feedforward(image)
            nabla = self.cost.prime(output, label)
            for layer in reversed(self.layers):
                nabla = layer.backpropagation(eta, nabla)

        for layer in reversed(self.layers):
            layer.backpropagation_update(eta, batch_size)
            layer.reset_backpropagation()

    def accuracy(self, data, add_str=''):
        """
        renvoie (nombre juste, nombre total)
        """
        print('Evaluating accuracy...')
        results = [(np.argmax(self.feedforward(x)), np.argmax(y))
                   for (x, y) in data]
        juste, total = sum(int(x == y) for (x, y) in results), len(results)
        # print(results)
        print(f"Accuracy: {juste}/{total} ou {juste / total:.4%} {add_str}")
        return juste, total

    def save(self, nom):
        """"
        Sauvegardes sous ..\network\filename
        """
        with open('../networks/' + nom, "wb") as f:
            pickle.dump(self, f)
            f.close()
        print(f'network {nom} saved')

    def total_cost(self, data, lmbda, test_data=False):
        """
        Cout moyen sur un dataset complet, test_data to True si c'est le jeu de test
        """
        cost = 0.0
        for x, y in data:
            output = self.feedforward(x)
            if test_data:
                y = int_to_vect(y, self.output_size)
            cost += self.cost.fn(output, y) / len(data)
        # cost += 0.5*(lmbda/len(data))*sum(
        # np.linalg.norm(w)**2 for w in self.weights)
        return cost

def load(nom):
    """
    Charge un reseau
    """
    with open("../networks/" + nom, "rb") as f:
        net = pickle.load(f)
        f.close()
        print(f'Network {nom} loaded!')
        return net

####Fonctions randoms
def int_to_vect(j, size):
    """
    vecteur size*1, 1.0 si l = j, 0 sinon
    """
    e = np.zeros((size, 1))
    e[j] = 1.0
    return e
