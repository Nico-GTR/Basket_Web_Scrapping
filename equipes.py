# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 13:31:53 2024

@author: gautnico
"""

import basketball_reference_scapper
import pandas


liste_equipes = [
    "CLE", "BOS", "ORL", "NYK", "MIL", "ATL", "MIA", "CHI", "BRK", "IND", 
    "DET", "TOR", "CHO", "PHI", "WAS", "OKC", "HOU", "DAL", "MEM", "LAC", 
    "PHO", "GSW", "DEN", "LAL", "SAS", "MIN", "SAC", "POR", "UTA", "NOP"
]

# Création d'un df pour la liste des joueurs
for equipe in liste_equipes:
    df = get_roster(equipe, 2025)
    df.drop(columns=["Birth"])
    df.to_csv(f"roster_{equipe}")
    
    
# Création d'un df pour les statistiques par match et par joueur de l'équipe
for equipe in liste_equipes:
    df = get_team_stats(equipe, 2025, 'PER_GAME')
    df = df[["G", "3P", "3P%", "2P", "2P%", "FT", "FT%", "TRB", "AST", "PTS"]]  # Colonne à garder
    df.to_csv(f"stats_{equipe}")


# Création d'un df pour la conférence, la division et le classement
for equipe in liste_equipes:
    df = get_team_ratings(2025, equipe)
    df = df[["RK", "CONF", "DIV"]]
    df.to_csv(f"infos_base_{equipe}")
    
    
# Création d'un df pour le stade de l'équipe
for equipe in liste_equipes:
    df = get_team_misc(equipe, 2025)
    df = df[["Arena"]]
    df.to_csv(f"stade_{equipe}")
    
    
# TODO: record, next game, last game, coach, salaries, Assistant Coaches and Staff :::::> à coder car pas dans l'API
