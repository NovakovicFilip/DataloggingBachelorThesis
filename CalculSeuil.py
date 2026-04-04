import pandas as pd
import matplotlib.pyplot as plt

#Variable modifiable qui indique à quel seuil un générateur est considéré allumé ou non [kW]
bruit = 2

#Fonction qui additionne tout les fichiers d'un côté du bateau ensemble
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

#On commence par lire et additionner les data
df_port = combiner_csv(fichiers_port)
df_stbd = combiner_csv(fichiers_stbd)


#df_m est le nom de notre dataframe qui est le mélange des deux dataframes ci-dessus
#On mélange sur la rangée du temps qui est commun aux deux
df_m = pd.merge(df_port,df_stbd,on="Date & Time")


#On assigne au merged dataframe les variables qui nous intéressent avec
#des noms plus facilement traitables
#On prends leur valeures absolues et on les multiplies par 3 pour refléter
#la réalité des capteurs

df_m = df_m.assign(GenPort = abs(df_port["S1_Port_Power_Generator [kW]"]) * 3)
df_m = df_m.assign(GenStbd = abs(df_stbd["S2_STBD_Power_Generator [kW]"]) * 3)
df_m = df_m.assign(Prise = abs(df_stbd["S1_STBD_Power_Shore_supply [kW]"])* 3)


#La boucle "for" principale pour calculer le nombre d'activations et à partir de quelle puissance
#On regarde si un générateur est allumée pendant que l'autre est éteint, si c'est le cas
#on vérifie si l'autre s'allume dans la minute qui suit(Durant l'ittération suivante)
#si c'est le cas on enregistre la valeur dans les seuils

#Un paragraphe de code pour chaque générateur

seuils_port = []
seuils_stbd = []
for i in range(1, len(df_m) - 1):
    if df_m["GenPort"].iloc[i] > bruit and df_m["GenStbd"].iloc[i] < bruit: 
        if df_m["GenStbd"].iloc[i+1] > bruit:
            seuils_stbd.append(df_m["GenPort"].iloc[i])
    
    elif df_m["GenStbd"].iloc[i] > bruit and df_m["GenPort"].iloc[i] < bruit:  
        if df_m["GenPort"].iloc[i+1] > bruit:
            seuils_port.append(df_m["GenStbd"].iloc[i])


#cumsum().iloc[-1] permettent de compter le nombre de fois où
#la condition est remplie
#Vu qu'on a une résolution en minute, on divise par 60 pour avoir un résultat en heures
NbHeuresPort = (df_m["GenPort"] > bruit).cumsum().iloc[-1] * (1 / 60)  
NbHeuresStbd = (df_m["GenStbd"] > bruit).cumsum().iloc[-1] * (1 / 60)

print(f"Heures de fonctionnement du groupe PORT : {NbHeuresPort:.2f} heures")
print(f"Heures de fonctionnement du groupe STBD : {NbHeuresStbd:.2f} heures")


#Pour la moyenne, somme divisée par quantitée totale de données
#On peut avoir l'écart type grâce à la fonction panda ci-dessous
#Partie port
moyenne_seuils_port = sum(seuils_port) / len(seuils_port)
ecart_type_seuils_port = pd.Series(seuils_port).std()
print(f"Moyenne des seuils Port : {moyenne_seuils_port:.2f} kW")
print(f"Ecart-type des seuils Port: {ecart_type_seuils_port:.2f} kW")
#Partie stbd
moyenne_seuils_stbd = sum(seuils_stbd) / len(seuils_stbd)
ecart_type_seuils_stbd = pd.Series(seuils_stbd).std()
print(f"Moyenne des seuils Stbd : {moyenne_seuils_stbd:.2f} kW")
print(f"Ecart-type des seuils Stbd: {ecart_type_seuils_stbd:.2f} kW")



