#!/usr/bin/env python
# coding: utf-8

# # Compte rendu mini projet n°3

# Tout ce qui est en **gras** dans une formule représente un vecteur.

# ### Introduction
# Ce mini projet a comme objectif le calcule numérique des forces appliquées à une digue de forme arbitraire.
# On va répendre aux quéstions au fur et à mesure.

# ### Hypothèses et modélisation
# Pour simplifier, on se placera en deux dimensions et on ne considérera que les forces de pressions dues à la hauteur d’eau (la pression de l’air étant négligée).
# ##### a. Bilan des forces appliquées à la digue : 
# - Le poids ***P** = -M.g.**e<sub>y</sub>***
# - La friction  ***f** = µ.P.**e<sub>x</sub>***  , *µ* étant le coefficient de friction statique béton-roche
# - La pression hydrostatique de l'eau  ***P<sub>eau</sub>***.
# - La force qui permet à la digue de ne pas glisser sur le sol rocheux est la friction ***f***
# ##### b. L’expression de la pression hydrostatique dans l’eau :
# Cette pression ne dépend que de la hauteur par rapport au sol ***x*** et est égale à :
# *P<sub>eau</sub> = ρ<sub>eau</sub>.V.g.h*   , *ρ<sub>eau</sub>* étant la masse volumique de l'eau.
# ##### c. L'équation d’équilibre statique de la digue :
# Pour que la digue soit en équilibre on doit avoir l'égalité entre ***P<sub>eau</sub>*** et ***f***.

# On décrira les bords de la digue avec un couple de fonction *( f<sub>eau</sub> , f<sub>air</sub> )* , chacune  représentant l’interface eau-béton (rsp. air-béton).

# ### Digue en pentes droites
# Dans un premier temps, on va considérer que les bords suivent des fonctions affines, qu'on va représenter :
# ##### * L'expression de la fonction côté air dans le cas d’une fonction affine :
# Si *f<sub>eau</sub> = x<sub>e</sub>.(y - H)/H* alors *f<sub>air</sub> = x<sub>a</sub>.(y - H)/H*.

# In[1]:


# Ce code permet d'afficher les courbes représentant la digue

import numpy as np
import matplotlib.pyplot as plt

H = 10
xa = -5
xe = +5

# On définit les fonctions côté eau et côté air, ici les courbes concaves
def fair(y):
    return -(y - H) * xa / H

def feau(y):
    return -fair(y)

# On crée un tableau de y
y = np.linspace(0, H, 1000)

# On trace
plt.plot(fair(y), y,'deeppink', '-b') 
plt.plot(feau(y), y,'deeppink', '-b') 
 
plt.plot([xe, xa], [0, 0], '-b') # Bas de la digue
plt.xlabel('x (m)') 
plt.ylabel('y (m)')
plt.text(xe, 8, 'eau')
plt.text(xa, 8, 'air')
plt.axis('equal') # Permet d'avoir un plot isométrique
plt.axhline(0, color = "black")
plt.axvline(0, color = "black")
plt.xlim(-8, 8)
plt.show()


# * **a. Calcule du volume de la digue :**
# d'apres la question, on suppose que la digue est un prisme droit de base 
# triangulaire et de largeur = 1, donc pour calculer son volume :

# In[25]:


# avec une integration
xa = -5
xe = 5

     # Calcul du pas d'intégration 
n = 5500000 # Nombre de pas
pas = (xe - xa) / n

    # Initialisation de la somme à zéro
volume = 0 

    # Ajoute de chaque terme de la somme
for i in range(n):
    f_xi = feau(a+i * pas)    # Valeur de la fonction en (a + i * pas)
    aire = f_xi * pas         # Aire approximative sous la courbe entre (a + i * pas) et (a + (i + 1) * pas)
    volume = volume + aire
volume=volume/2

# calcul analytique
volume_ana=5*feau(0)

print("le calcule de l'integration donne :",round(volume,2))
print("le calcule de analytique donne :",round(volume_ana,2))


# Les deux calculs integrale est analytique sont bien egaux.

# Donc le poid de la digue est :

# In[6]:


p=round(3000*volume)
P=(0,-p) #en vecteur
print("P = ",P)


# * **b. La résultante des forces de pression du côté de l'eau est  :** on suppose que le mouvement est suivant l'axe (ox).

# In[8]:


#nos constantes
mu=0.5 #le coeff de friction
g=10
ρ=3000 #la masse volumique de l'eau 
θ=np.arctan(-xa)  #l'angle que fait le bord de la digue avec l'horizontiale

#les forces
P=np.array(P)
f=np.array([round(mu*p),0])  #quand le mouvement est vers les *x* negatifs
Pr=np.array([round(ρ*g*np.cos(θ)),round(ρ*g*np.sin(θ))])   #la pression dans la base cartesienne
F=tuple(P+f+Pr)

print("La resultante des forces dans la base cartesienne est  F =",F)


# La digue n'est pas en equilibre statique translationel.

# * c. Si on suppose que la digue n'est pas en translation suivant l'axe (oz), on a, d'apres le PFD **R**=(T,N)=**P**+**Pr_z** et donc :

# In[10]:


R=(0,45583) #dans la base cartesienne
r=45583
R=(r*np.sin(θ),r*np.cos(θ))
print("La force de réaction du sol dans la base {t,n} est R =",R)
rapp=round(R[0]/R[1])
print("le rapport T/N =",rapp)


# * d. On refait tout avec *xa*=-5 et *xe*=0 :

# In[26]:


xa=-5
xe=0
    # a
# calcul analytique
volume_ana=2.5*feau(0)

print("le volume est :",volume_ana,2)

p=round(3000*volume)
P=(0,-p)   #en vecteur
print("P = ",P)

   #b
#nos constantes
mu=0.5    #le coeff de friction
g=10
ρ=3000    #la masse volumique de l'eau 
θ=np.pi/2  #l'angle que fait le bord de la digue avec l'horizontiale

#les forces
P=np.array(P)
f=np.array([round(mu*p),0])  #quand le mouvement est vers les *x* negatifs
Pr=np.array([0,round(ρ*g*np.sin(θ))])   #la pression dans la base cartesienne
F=tuple(P+f+Pr)

print("La resultante des forces dans la base cartesienne est  F =",F)

    #c
R=(0,45583) #dans la base cartesienne
r=45583
R=(r*np.sin(θ),r*np.cos(θ))
print("La force de réaction du sol dans la base {t,n} est R =",R)
rapp=round(R[0]/R[1])
print("le rapport T/N =",rapp)


# * e. On refait tout avec *xa*=0 et *xe*=5 :

# In[15]:


xa=0
xe=5
    # a
# calcul analytique
volume_ana=2.5*feau(0)

print("le volume est :",volume)

p=round(3000*volume)
P=(0,-p) #en vecteur
print("P = ",P)

   #b
#nos constantes
mu=0.5    #le coeff de friction
g=10
ρ=3000    #la masse volumique de l'eau 
θ=np.arctan(-xa)  #l'angle que fait le bord de la digue avec l'horizontiale

#les forces
P=np.array(P)
f=np.array([round(mu*p),0])  #quand le mouvement est vers les *x* negatifs
Pr=np.array([0,round(ρ*g*np.sin(θ))])   #la pression dans la base cartesienne
F=tuple(P+f+Pr)

print("La resultante des forces dans la base cartesienne est  F =",F)

    #c
R=(0,45583) #dans la base cartesienne
r=45583
R=(r*np.sin(θ),r*np.cos(θ))
print("La force de réaction du sol dans la base {t,n} est R =",R)
rapp=round(R[0]/R[1])
print("le rapport T/N =",rapp)


# # Je n'ai pas eu le temps de finir avant la dead-line précisée, mais je continue à y travailler dessus.
