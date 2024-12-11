# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 15:07:34 2024

@author: Manoubi
"""

import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

from lookup import lookup
from players import get_player_suffix,get_game_logs,get_player_splits,get_player_headshot

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd


def get_player_splits_clean(nom_joueur):
    
    df = get_player_splits(nom_joueur, 2024)
    # Renommer les colonnes
    df.columns = ["Catégories", "Valeur", "Minutes jouées", "Points", "Rebonds totaux", "Passes décisives"]
    return df


ok = get_player_splits_clean("Lebron James")
ok.to_csv("final.csv", index = False)
