"""Tappa 3 — La rete neurale minima 8 → 6 → 4.

Obiettivo: una funzione che trasforma 8 letture in 4 comandi, con i pesi in un unico vettore.
Teoria: indice didattico, Parte 2.
"""

from __future__ import annotations

import numpy as np

LAYERS = (8, 6, 4)   # input: 7 raggi + velocità; output: sterzo, gas, freno, freno a mano


def genome_size(layers: tuple[int, ...] = LAYERS) -> int:
    """Numero totale di pesi + bias. Per (8, 6, 4) deve valere 82.

    TODO(step-03): somma di (n_in * n_out + n_out) per ogni coppia di strati.
    """
    raise NotImplementedError("tappa 3: genome_size")


class Network:
    def __init__(self, genome: np.ndarray, layers: tuple[int, ...] = LAYERS):
        """Ricava matrici W e vettori b dal vettore piatto `genome`.

        TODO(step-03): scorri il genome e fai reshape in W1 (6, 8), b1 (6,), W2 (4, 6), b2 (4,).
        """
        raise NotImplementedError("tappa 3: Network.__init__")

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
        """Propagazione in avanti.

        Restituisce l'output (4,) e le attivazioni di ogni strato (per la UI).
        TODO(step-03): h = tanh(W1 @ x + b1), y = tanh(W2 @ h + b2).
        Verifica: make test STEP=3
        """
        raise NotImplementedError("tappa 3: Network.forward")
