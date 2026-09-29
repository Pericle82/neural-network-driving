"""Tappa 5 — La neuroevoluzione.

Obiettivo: una popolazione di genomi che migliora di generazione in generazione.
Teoria: indice didattico, Parte 3.
"""

from __future__ import annotations

import numpy as np


def next_generation(
    genomes: np.ndarray,
    fitness: np.ndarray,
    rng: np.random.Generator,
    elite: int = 4,
    mutation_rate: float = 0.1,
    mutation_sigma: float = 0.3,
) -> np.ndarray:
    """Dalla generazione corrente (P, G) e dalle fitness (P,) alla successiva (P, G).

    TODO(step-05):
      1. Elitismo: copia i migliori `elite` genomi senza modifiche.
      2. Selezione a torneo per scegliere due genitori.
      3. Crossover uniforme: ogni peso da uno dei due genitori, a caso.
      4. Mutazione: con probabilità `mutation_rate` aggiungi N(0, mutation_sigma).
    Usa SOLO `rng` per il caso: con lo stesso seed, stessi risultati.
    """
    raise NotImplementedError("tappa 5: next_generation")
