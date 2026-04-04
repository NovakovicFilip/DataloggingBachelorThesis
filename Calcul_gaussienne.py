import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


seuil = 0.3
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

#Nom des colonnes dans les fichiers excels qu'on va analyser, séparé par fichier
sous_panneaux_port = {
    1: ('S1_Port_Power_Generator [kW]', 'S1_Port_Apparent_Power_Generat* [kVA]'),
    2: ('S2_Port_Power_Anchor_Windlasse2 [kW]', 'S2_Port_Apparent_Power_Anchor* [kVA]'),
    3: ('S3_Port_Power_PS Engine room Fa [kW]', 'S3_Port_Apparent_Power_PS Engin* [kVA]'),
    4: ('S4_Port_Power_Stabilizer [kW]', 'S4_Port_Apparent_Power_Stabiliz* [kVA]'),
    5: ('S5_Port_Power_Hyde_Unit_Aft [kW]', 'S5_Port_Apparent_Power_Hyde_Uni* [kVA]'),
    6: ('S6_Port_Power_Boiller_AM_2 [kW]', 'S6_Port_Apparent_Power_Boiller* [kVA]'),
    7: ('S7_Port_Power_Water_Maker_Idrom [kW]', 'S7_Port_Apparent_Power_Water_Ma* [kVA]'),
    8: ('S8_Port_Power_Fridge_Plant [kW]', 'S8_Port_Apparent_Power_Fridge_P* [kVA]'),
    9: ('S9_Port_Power_AC7_Condaria_ECP1 [kW]', 'S9_Port_Apparent_Power_AC7_Cond* [kVA]'),
    10: ('S10_Port_Power_Q4_Sub_Gallery [kW]', 'S10_Port_Apparent_Power_Q4_Gall* [kVA]'),
    11: ('S11_Port_Power_Q3_Sub_Maindeck [kW]', 'S11_Port_Apparent_Power_Q3_Sub_* [kVA]'),
    12: ('S12_Port_Power_Subpanel_Wellhou [kW]', 'S12_Port_Apparent_Power_Wellhou* [kVA]'),
    13: ('S13_Port_Power_Crew_Dinette [kW]', 'S13_Port_Apparent_Power_Crew_Di* [kVA]'),
    14: ('S14_Port_Power_Q9_Foyer_subpan [kW]', 'S14_Port_Apparent_Power_Q9_Foye* [kVA]'),
    15: ('S15_Port_Power_Q5_Owner_Subpane [kW]', 'S15_Port_Apparent_Power_Q5_Owne* [kVA]')
}

# Configuration des sous-panneaux pour le côté "stbd"
sous_panneaux_stbd = {
    1: ('S1_STBD_Power_Shore_supply [kW]', 'S1_STBD_Apparent_Power_Shore_su* [kVA]'),
    2: ('S2_STBD_Power_Generator [kW]', 'S2_STBD_Apparent_Power_Generato* [kVA]'),
    3: ('S3_STBD_Power_PS_Engine_room_Fa [kW]', 'S3_STBD_Apparent_Power_PS_Engin* [kVA]'),
    4: ('S4_STBD_Power_Steering_pump_1 [kW]', 'S4_STBD_Apparent_Power_Steering* [kVA]'),
    5: ('S5_STBD_Power_Anchor_Windlasses [kW]', 'S5_STBD_Apparent_Power_Anchor_W* [kVA]'),
    6: ('S6_STBD_Power_Vacuum_Jets_Plant [kW]', 'S6_STBD_Apparent_Power_Vacuum_* [kVA]'),
    7: ('S7_STBD_Power_Water_maker_Idrom [kW]', 'S7_STBD_Apparent_Power_Water_ma* [kVA]'),
    8: ('S8_STBD_Power_Boiler_FWD [kW]', 'S8_STBD_Apparent_Power_Boiler_F* [kVA]'),
    9: ('S9_STBD_Power_Boiler_AM1 [kW]', 'S9_STBD_Apparent_Power_Boiler_A* [kVA]'),
    10: ('S10_STBD_Power_Bow_Thruster [kW]', 'S10_STBD_Apparent_Power_Bow_Thr* [kVA]'),
    11: ('S11_STBD_Power_Q8_Laundry_AREA [kW]', 'S11_STBD_Apparent_Power_Q8 Laun* [kVA]'),
    12: ('S12_STBD_Power_Q10_Gymnasium [kW]', 'S12_STBD_Apparent_Power_Q10_Gym* [kVA]'),
    13: ('S13_STBD_Power_Q2_Upper_Deck_Ar [kW]', 'S13_STBD_Apparent_Power_Upper_D* [kVA]'),
    14: ('S14_STBD_Power_Q6_Guest_Area [kW]', 'S14_STBD_Apparent_Power_Q6_Gues* [kVA]'),
    15: ('S15_STBD_Power_Q1_Wellhouse [kW]', 'S15_STBD_Apparent_Power_Q1_Well* [kVA]')
}


#On va charger les données dans le fichier csv mentioné
def charger_donnees(fichiers):
    for fichier in fichiers:
        #On commence par lire le fichier csv, on lui spécifie le format de la première rangé
        df = pd.read_csv(fichier, date_format="%Y-%m-%d %H:%M:%S") 
        #Pour chaque colonne qui n'est pas la rangée date et heure, on va
        #prendre la valeur absolue et la multiplier par 3 pour refléter
        #la réalité
        colonnes = [col for col in df.columns if col != 'Date & Time']
        df[colonnes] = df[colonnes].abs() * 3
        df = df.set_index('Date & Time')
        df.sort_index(inplace=True)
    return df

#Fonction qui va imprimer les graphiques dans la console
#Pour ce code, j'utilise l'environnement spyder et la fonctionnalité
#intéressante est de pouvoir passer d'un graphique à l'autre avec les flèches
#Sous préférence, Console IPython, fenêtre "Graphique", il y a une option
#"Sortie graphique", choisir Tkinter pour avoir la fenêtre interactive qui 
#apparait.
def afficher_histo_gauss(puissance, titre, colour):
    
    #Un check qui nous sors de la fonction si il n'y a pas assez de données.
    if len(puissance) < 1:
        print("Pas assez de données pour tracer l'histogramme et la densité.")
        return
    
    #On graphe l'histogramme de la puissance mentionné
    plt.hist(puissance, bins=50, alpha=0.6, color=colour, density=True, label='Puissance (kW)')

    #The "Gaussian Kernel Density Estimation" (KDE), est une méthode statistique
    #Pour estimer la probabilité par densité là où il va apparaitre dans le graph
    #La fonction existe dans la library "spicy.stats" et on utilise les données
    #actuelle pour les calculer.
    kde = gaussian_kde(puissance)
    puissances_kde = np.linspace(min(puissance), max(puissance), 1000)
    densite_kde = kde(puissances_kde)
    
    #On va tracer la gaussienne au dessus de l'histogramme
    plt.plot(puissances_kde, densite_kde, color='red', label='Densité de probabilité (KDE)')

    #On va églament calculer et imprimer l'intégrale de la gaussienne pour s'assurer
    #qu'elle est égale à 1 vu qu'on normalise.
    integrale = np.trapz(densite_kde, puissances_kde)
    print(f"Intégrale de la Gaussienne KDE : {integrale:.4f} (devrait être proche de 1)")

    #Mise en forme du graph
    plt.title(titre)
    plt.xlabel('Puissance (kW)')
    plt.ylabel('Densité')
    plt.legend()
    plt.grid(True)
    
#La fonction pour naviguer entre les différents graphiques
def affichage_dynamique():
    
    #Il y a une partie setup, une partie définition de fonctions et la partie
    #"boucle"
    #On va initier des variables pour savoir à quel graph on est.
    #L'index nous dit à quelle colonne on se trouve dans l'excel
    index = [0]
    #Savoir si on se trouve dans les fichiers port ou stbd
    is_port = True
    #Ceci active le mode interactif et permettra d'influencer le graphique avec
    #les flèches
    plt.ion()  # Activer le mode interactif
    #Création d'une figure initiale où on va pouvoir imprimer tout les graphs
    fig, ax = plt.subplots(figsize=(12, 6))
    
    
    def affichage_graphique(index):

        #Quand on affiche un nouveau graphique, on efface le précdédent
        ax.cla()
        
        #On sélectionne les données à afficher en fonction de la valeur de 
        #l'index et de quel côté de données on se trouve
        if is_port:
            col_kw = sous_panneaux_port[index + 1][0]  # Ajuster l'index pour le dictionnaire
            df = df_port
        else:
            col_kw = sous_panneaux_stbd[index + 1][0]  # Ajuster l'index pour le dictionnaire
            df = df_stbd

        #À partir de la sélection, on va mettre à jour une variable "puissance"
        #Qu'on va affichier sur le graphique après
        puissance = df[col_kw]
        #Filtrage des données, on garde seulement les valeurs au dessus du seuil
        puissance = puissance[puissance >= seuil]
        #Le titre va également varier en fonction du graphique
        titre = f"Gaussienne KDE de - {col_kw}"
        
        #On appelle la fonction ci-dessus pour imprimer l'histogramme et la gaussienne
        afficher_histo_gauss(puissance, titre, 'blue')
        #Pour mettre à jour le graphique
        plt.pause(0.1)

    #La fonction qui nous permettra de naviguer parmis les données
    def on_key(event):
        #Nous permet de modifier la variable "is_port"
        nonlocal is_port
        
        #Les flèches du haut et du bas nous permettent de passer d'une partie 
        #À l'autre
        if event.key == 'down':
            is_port = False
        elif event.key == 'up':
            is_port = True
        
        #Les flèches de gauche à droite vont nous faire monter ou descendre
        #dans les données, on augmente ou descend la valeur d'index, et si on
        #dépasse, on refait le tour
        elif event.key == 'right':
            index[0] = (index[0] + 1) % (len(sous_panneaux_port) if is_port else len(sous_panneaux_stbd))
        elif event.key == 'left':
            index[0] = (index[0] - 1) % (len(sous_panneaux_port) if is_port else len(sous_panneaux_stbd))
        
        #On réaffiche un nouveau graphique à chaque modification
        affichage_graphique(index[0])

    #On commence par afficher le premier graphique
    affichage_graphique(index[0])
    
    #Fonction pour pourvoir lire les touches du clavier et d'
    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()
  

#On charge les données dans les dataframes
df_port = charger_donnees(fichiers_port)
df_stbd = charger_donnees(fichiers_stbd)

#Cette partie qui suit est pour calculer la gaussienne de la génération totale
#df_m est le nom de notre dataframe qui est le mélange des deux dataframes ci-dessus
#On mélange sur la rangée du temps qui est commun aux deux
df_m = pd.merge(df_port,df_stbd,on='Date & Time')
df_m = df_m.assign(GenTot =df_stbd['S2_STBD_Power_Generator [kW]']+df_port['S1_Port_Power_Generator [kW]'])
df_m = df_m[df_m['GenTot'] > seuil]

#On va également faire une colonne avec tout les consommateurs
df_m = df_m.assign(ConsTot = 0)
#Additionner tout les consommateurs dans une seule colonne
for col in range(3, len(sous_panneaux_stbd) + 1):
    df_m['ConsTot'] = df_m['ConsTot'] + df_port[sous_panneaux_port[col][0]] + df_stbd[sous_panneaux_stbd[col][0]] 

#Décommenter si vous voulez voir le graphique
afficher_histo_gauss(df_m['GenTot'], "Generation Totale",'blue')
afficher_histo_gauss(df_m['ConsTot'], "Consommation Totale",'green')

#On lance la "boucle"
affichage_dynamique()