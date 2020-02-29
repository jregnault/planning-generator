"""
Modèle Python pour la génération de planning de soutenances

Génération pour plusieurs soutenances rangées par formation

Auteur: Jérémie Regnault 2020
"""

import json
import argparse
from pulp import *

def satisfaction(soutenance, creneau):
    """Calcule la satisfaction des participants d'une soutenance pour un créneau donné."""
    result = 1
    for pers in soutenance:
        result *= pers[creneau]

    return result

def distance(s1, s2):
    """Calcule la distance entre deux soutenances."""
    pass

parser = argparse.ArgumentParser(description="Générateur de planning de soutenances")
parser.add_argument('FILE', help="Un fichier JSON respectant le format défini.")
parser.add_argument('-o', '--output', help="Chemin vers un fichier de sortie pour récupérer le planning.")

args = parser.parse_args()

with open(args.FILE, 'r', encoding="utf-8") as input_file:
    data = json.load(input_file)

creneaux = data['creneaux']
etudiants = data['etudiants']
professeurs = data['professeurs']
soutenances_list = data['soutenances']
soutenances = []
for (e, p) in soutenances_list:
    soutenances.append((etudiants[e], professeurs[p]))

model = LpProblem("Planning_de_soutenances",LpMaximize)

# Variables
creneaux_vars = []
for i in range(0,len(soutenances)):
    name = "Soutenance_" + str(i)
    creneau_vars = LpVariable.dicts(name,creneaux,
                                    lowBound = 0,
                                    upBound = 1,
                                    cat = LpInteger)
    creneaux_vars.append(creneau_vars)

# Objectif
model += sum([satisfaction(s,c) * creneaux_vars[i][c] for s in soutenances for c in creneaux for i in range(0,len(soutenances))])

# Contraintes
# Contraintes sur les créneaux : 1 soutenance max par créneaux
for c in creneaux:
    model += sum([creneaux_vars[i][c] for i in range(0, len(soutenances))]) <= 1

# Contraintes sur les soutenances : 1 créneau par soutenance
for i in range(0,len(soutenances)):
    model += sum([creneaux_vars[i][c] for c in creneaux]) <= 1

# Solution
model.solve()

planning = {}
i = 0
for s in soutenances:
    line = s[0]['name'] + " (" + s[1]['name'] + ")"
    for c in creneaux:
        if creneaux_vars[i][c].value() == 1.0:
            planning[c] = line
    i += 1

if args.output :
    output_filename = args.output
    with open(output_filename, "w", encoding="utf-8") as output_file:
        json.dump(planning, output_file, ensure_ascii=False)
else:
    planning_list = list(planning.keys())
    planning_list.sort()
    print("Soutenance \t Horaire")
    for c in planning_list:
        print(planning[c] + " \t " + c)