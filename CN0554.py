import adi
#Librarie spécifique au pilotage de différentes électronique dont le cn0554
import time
#Principalement pour "time.sleep(secondes)" pour faire des délais
import pandas as pd
#Pour le traitement des données dans le csv
import numpy as np
#Pour des fonctions mathématique

#----------------------------------------------------------------------------
#Lecture des fichiers csv


#Fonction qui va combiner tout les fichiers d'un des côtés du bateau
def combiner_csv(fichiers_csv):
    dataframes = [pd.read_csv(fichier, sep=",") for fichier in fichiers_csv]
    return pd.concat(dataframes, ignore_index=True)

#Noms des data qu'on va utiliser, séparé par côté
#Il faut que les fichiers se trouvent dans le même environnement que le fichier python
#(Les mettres dans le même dossier que le code si ne sait pas comment faire)

fichiers_port = [
    "data_97403_08_18_08_31.csv",
    "data_97403_09_01_09_14.csv",
    "data_97403_09_15_09_30.csv",
    "data_97403_10_01_10_15.csv"
]


fichiers_stbd = [
    "data_97404_08_18_08_31.csv",
    "data_97404_09_01_09_14.csv",
    "data_97404_09_15_09_30.csv",
    "data_97404_10_01_10_15.csv"
]

print("Lecture des csv...")

#On va créer des dataframes qui contiennent tout les fichiers par côté
df_port = combiner_csv(fichiers_port)
df_stbd = combiner_csv(fichiers_stbd)


#df_m est le nom de notre dataframe qui est le mélange des deux dataframes ci-dessus
#On mélange sur la rangée du temps qui est commun aux deux
df_m = pd.merge(df_port["Date & Time"],df_stbd["Date & Time"],on="Date & Time")

#.assign est une fonction qui va créer une colonne avec un nom spécfique,
#c'est pour avoir une colonne séparée qui ne va pas affecter les données de base.

#Les valeurs choisies sont arbitraires et utilisé à des fins de test

#On prends les valeurs absolues et on les multiplies par 3 pour refléter
#les valeurs de la réalité
df_m = df_m.assign(Prise = abs(df_stbd["S1_STBD_Power_Shore_supply [kW]"])* 3)

print("Fichiers csv chargés!")


#--------------------------------------------------------------------------------
#Setup du cn0554

#Dans le code j'utilise une structure "try:  except:" qui est une manière d'afficher
#les éventuels erreurs dans la console sans bloquer le code


try:
    print("Mise en route de l'appareil...")
    #uri est l'adresse ip de l'appareil avec le quel on souhaite se connecter
    uri = "ip:192.168.1.242"  
    #adi.cn0554 nous permet de créer un objet "cn0554" en lui spécifiant l'adrese
    #Ceci nous permettera d'accéder à ses différentes informations avec la librarie
    #pyadi-iio
    my_cn0554 = adi.cn0554(uri=uri)

    #On va activer les entrées de l'ADC pour qu'on puisse lire des données
    #Sur le cn0554, il y a 8 entrées
    my_cn0554.rx_enabled_channels = [0, 1, 2, 3, 4, 5, 6, 7]

    #Impression de différentes informations dont la confirmation si tout marche
    print("Appareil mis en route!")
    print(f"Sorties du DAC: {my_cn0554.dac_out_channels}")
    print(f"Entrées de l'ADC': {my_cn0554.adc_in_channels}")
    
    #Il faut laisser un petit moment pour que le système se mette en route
    time.sleep(0.5)
    
except Exception as e:
    #En cas de problème dans le setup, on l'imprime dans la console
    print(f"Problème de mise en route: {e}")

#--------------------------------------------------------------------------------
#Fonction pour fixer les valeurs de sorties

def set_mvolt(milivolts):
    try:    
        print("Modification de la valeur de sortie...")
        #On va répéter la boucle pour chaque sortie du DAC
        for i, dac_channel in enumerate(my_cn0554.dac_out_channels):
            #On va pouvoir modifier les valeurs de sortie en utilisant
            #l'objet dac.
            #la variable "dac_channel" va varier entre 0 et 15 pour chaque sortie
            dac_obj = getattr(my_cn0554.dac, dac_channel)
            #Pour modifier la valeur de sortie:
            dac_obj.volt = milivolts
            print(f"Valeur de sortie {dac_channel}: {milivolts}mV")
        print("Modification terminée")
    except Exception as e:
        #En cas de problème dans la fonction, on l'imprime dans la console
        print(f"Problème dans set_mvolt: {e}")


#--------------------------------------------------------------------------------
#Fonction pour lire les valeurs de sortie

def lecture_adc():
    try:
        print("Lecture des valeurs d'entrées...")
        
        #On peut récupérer les données en utilisant notre objet cn0554
        raw_data = my_cn0554.rx()
        
        #On va faire une boucle pour récupérer les valeurs de chaque
        #entrée du DAC
        #Pour chaque entré du DAC, on va récupérer les valeurs "bruts" et les
        #imprimer avec le nom de l'entrée
        for idx, ch in enumerate(my_cn0554.adc_in_channels):
            if idx < len(raw_data) and raw_data[idx].size > 0:
                voltage = raw_data[idx][0]  # Convert raw data to voltage
                print(f"Channel {ch}: Tension = {voltage:.6f} Volts")
            else:
                print(f"Channel {ch}: Problème avec les valeurs mesurés")
                
    except Exception as e:
        print(f"Erreur dans la lecture des données: {e}")
   

#--------------------------------------------------------------------------------
#Boucles principales

#La stable, on fixe une tension et on la mesure en boucle
def main_stable():
    set_mvolt(5000)
    while True:
            lecture_adc()  # Read ADC data
            time.sleep(10)  # Wait 10 seconds before the next loop
            
#Celle qui sera utilisé dans le projet final, hélas quand on fait tourner cette
#boucle on a une erreur: "Errno 32: Broken Pipe" au bout de la seconde
#ittération
def main_test():
    j = 0
    while True:
            #Valeurs de tension du dataframe, l'idée serait de passer par toute
            #les données, on arrondi par facilitée
            V = int(np.round(df_m["Prise"].iloc[j], 1))
            print(V)
            set_mvolt(V)
            #Un délai entre la modification des sorties et de la lecture assure
            #un bon fonctionnement (malgré le bug)
            time.sleep(5)
            lecture_adc()
            time.sleep(10)
            
            
main_stable()


