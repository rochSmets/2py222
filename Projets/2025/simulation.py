import random
import sys

import numpy as np
from typing import Optional
from scipy.spatial import cKDTree
import pygame
import matplotlib.pyplot as plt

class Prey:
    def __init__(self, reproduction_prob: float, moving_prob: float, x: Optional[int] = 0, y: Optional[int] = 0) -> None:
        """
        Initialise une proie avec une probabilité de reproduction et de mouvement.
        Arguments:
        - reproduction_prob : probabilité de reproduction
        - moving_prob : probabilité de mouvement
        - x : position x de la proie
        - y : position y de la proie
        """
        self.reproduction_prob = reproduction_prob
        self.moving_prob = moving_prob
        self.x = x
        self.y = y


    def update(self, local_contents: list, local_empty_cells: list, **kwargs) -> Optional[bool]:
        """
        Met à jour l'état de la proie à chaque pas de temps.

        La proie tente d'abord une reproduction facultative (probabiliste) dans une cellule voisine vide.
        Si la reproduction n'est pas possible, elle tente de se déplacer dans une cellule vide adjacente.

        Arguments :
        - local_contents[Cell] : liste des cellules voisines occupées.
        - local_empty_cells (list[Cell]) : liste des cellules voisines vides.

        Retourne Optional[bool] :
        - None : si la proie s'est reproduite ou n'a rien pu faire.
        - False : si la proie s'est déplacée.
        """
        if self.reproduce(local_contents, local_empty_cells):
            return None
        if self.move(local_empty_cells):
            return False
        return None


    def move(self, local_empty_cells: list) -> Optional[bool]:
        """
        Tente de déplacer la proie vers une cellule vide voisine.

        La proie choisit aléatoirement une cellule vide parmi celles disponibles.
        Le déplacement a lieu avec une probabilité donnée par `moving_prob` pour éviter un mouvement systématique.

        Arguments :
        local_empty_cells (list[Cell]) : liste des cellules voisines vides.

        Retourne Optional[bool] :
        - True : si la proie s'est déplacée.
        - None : si aucune cellule vide n'était disponible ou si elle n’a pas bougé.
        """
        if len(local_empty_cells) == 0:
            return None
        if random.random() < self.moving_prob:
            cell = random.choice(local_empty_cells)
            self.x = cell.x
            self.y = cell.y
            cell.set_content(self)
            return True
        return None

    def reproduce(self, local_contents: list, local_empty_cells: list) -> Optional[bool]:
        """
        Tente de reproduire la proie dans une cellule vide voisine, selon une probabilité.

        La reproduction n’est possible que si 1 à 4 autres proies se trouvent dans les cellules voisines (afin de ne pas surpeupler).
        Pour chaque proie voisine, un tirage aléatoire est effectué avec la probabilité `reproduction_rate`.
        Dès qu’un tirage réussit, une nouvelle proie est placée dans une cellule vide aléatoire adjacente.

        Arguments :
        local_contents (list[Cell]) : liste des cellules voisines occupées.
        local_empty_cells (list[Cell]) : liste des cellules voisines vides.

        Retourne Optional[bool] :
        - True : si une nouvelle proie a été créée.
        - None : si aucune reproduction n’a eu lieu.
        """

        if len(local_empty_cells) == 0:
            return None
        nb_prey = len([content for content in local_contents if content.is_prey])
        if nb_prey == 0 or nb_prey >= 4:
            return None
        for content in local_contents:
            if content.is_prey and random.random() < self.reproduction_prob:
                cell = random.choice(local_empty_cells)
                cell.set_content(Prey(self.reproduction_prob, self.moving_prob, cell.x, cell.y))
                return True
        return None


class Predator:
    def __init__(self, hunting_prob, reproduction_prob, predator_max_hunger, x=0, y=0):
        """
        Initialise un prédateur avec ses caractéristiques de chasse, de reproduction et de survie.

        Arguments :
        - hunting_prob (float) : Probabilité de réussir une chasse.
        - reproduction_prob (float) : Probabilité de reproduction.
        - predator_max_hunger (int) : Nombre de tours sans manger avant la mort du prédateur.
        - x : Position x du prédateur
        - y  : Position y du prédateur

        Attributs initiaux :
        - hunger : Niveau de faim du prédateur (moitié de predator_max_hunger).
        """

        self.hunting_prob = hunting_prob
        self.reproduction_prob = reproduction_prob
        self.predator_max_hunger = predator_max_hunger
        self.hunger = predator_max_hunger // 2
        self.x = x
        self.y = y


    def update(self, nearest_prey, local_contents, local_empty_cells, **kwargs):
        """
        Met à jour l'état du prédateur pour un tour de simulation.

        Déroulement :
        1. Le niveau de faim (`hunger`) augmente de 1.
        2. Mort par famine : si `hunger` atteint `death_after`, le prédateur meurt.
        3. Chasse : tente de capturer une proie voisine avec la méthode `hunt`.
        4. Si aucune cellule vide n'est disponible, l'action s'arrête.
        5. Reproduction : tente de se reproduire dans une cellule vide adjacente avec `reproduce`.
        6. Déplacement : tente de se déplacer vers une cellule vide plus proche d'une proie (`nearest_prey`).

        Arguments :
        - nearest_prey (tuple[int, int]) : Position/référence vers la proie la plus proche (utilisé pour guider le déplacement des prédateurs).
        - local_contents (list[Cell]) : Liste des cellules voisines occupées.
        - local_empty_cells (list[Cell]) : Liste des cellules voisines vides disponibles.

        Retourne Optional[bool] :
        - False : si le prédateur est mort ou s'est déplacé.
        - None : sinon (s'il a seulement chassé ou reproduit).
        """

        self.hunger += 1
        if self.hunger >= self.predator_max_hunger:
            return False
        self.hunt(local_contents, local_empty_cells)
        if not local_empty_cells:
            return None
        if self.reproduce(local_contents, local_empty_cells):
            return None
        if self.move(nearest_prey, local_empty_cells):
            return False
        return None


    def hunt(self, local_contents, local_empty_cells):
        """
        Tente de chasser une proie parmi les cellules voisines.

        Pour chaque proie détectée dans les cellules voisines, un tirage aléatoire est effectué.
        Si le tirage est inférieur à `hunting_factor`, la chasse réussit :
        - la proie est éliminée (cellule vidée),
        - la faim (`hunger`) du prédateur est réinitialisée à 0,
        - la cellule est ajoutée à la liste des cellules vides.

        Arguments :
        - local_contents (list[Cell]) : Liste des cellules voisines occupées.
        - local_empty_cells (list[Cell]) : Liste des cellules voisines vides (sera modifiée si la chasse réussit).

        Retourne Optional[bool] :
        - True : si une proie a été chassée avec succès.
        - None : sinon (aucune chasse réussie).
        """

        for content in local_contents:
            if content.is_prey and random.random() < self.hunting_prob:
                self.hunger = 0
                content.empty()
                local_empty_cells.append(content)
                return True
        return None


    def reproduce(self, local_contents, local_empty_cells):
        """
        Tente de reproduire un nouveau prédateur dans une cellule vide voisine.

        Conditions pour tenter la reproduction :
        - Le prédateur doit avoir une faim (`hunger`) inférieure à la moitié de `death_after`.
        - Le nombre de prédateurs voisins doit être compris entre 1 et 3 inclus.
        - Un tirage aléatoire doit réussir selon la probabilité `reproduction_rate` (il faut que le nombre aléatoire entre 0 et 1 soit inférieur à `reproduction_rate`).

        En cas de succès, un nouveau prédateur est créé dans une cellule vide adjacente.

        Arguments :
        - local_contents (list[Cell]) : Liste des cellules voisines occupées.
        - local_empty_cells (list[Cell]) : Liste des cellules voisines vides disponibles.

        Retourne Optional[bool] :
        - True : si un nouveau prédateur a été créé.
        - None : si aucune reproduction n’a eu lieu.
        """

        if self.hunger >= self.predator_max_hunger/2:
            return None
        nb_predator = len([content for content in local_contents if content.is_predator])
        if 0 < nb_predator < 4 and random.random() < self.reproduction_prob:
            cell = random.choice(local_empty_cells)
            cell.set_content(
                Predator(self.hunting_prob, self.reproduction_prob, self.predator_max_hunger, cell.x, cell.y))
            return True
        return None

    def move(self, nearest_prey_pos, local_empty_cells):
        """
        Tente de déplacer le prédateur vers la proie la plus proche.

        Si une position de proie est connue, le prédateur calcule un mouvement unitaire
        (déplacement de ±1 sur chaque axe) pour se rapprocher de la proie.
        Si la cellule ciblée dans cette direction est vide, le prédateur s'y déplace et met à jour sa position.

        Arguments :
        - nearest_prey_pos (tuple[int, int]) : Position (x, y) de la proie la plus proche, ou None si inconnue.
        - local_empty_cells (list[Cell]) : Liste des cellules voisines vides.

        Retourne Optional[bool] :
        - True : si le prédateur s'est déplacé vers la proie.
        - None : si aucun déplacement n'a été effectué.
        """

        if nearest_prey_pos:
            x_prey, y_prey = nearest_prey_pos
            dx = x_prey - self.x
            dy = y_prey - self.y
            if dx != 0:
                dx = dx // abs(dx)
            if dy != 0:
                dy = dy // abs(dy)
            new_x = self.x + dx
            new_y = self.y + dy
            for cell in local_empty_cells:
                if (new_x, new_y) == (cell.x, cell.y):
                    self.x = new_x
                    self.y = new_y
                    cell.set_content(self)
                    return True
        return None

class Cell:

    def __init__(self, x, y, simulation):
        """
        Initialise une cellule dans la grille de simulation.

        Chaque cellule possède une position (x, y), un contenu initialement vide,
        et une liste vide pour ses cellules voisines.

        Arguments :
        - x (int) : Coordonnée horizontale de la cellule.
        - y (int) : Coordonnée verticale de la cellule.
        - simulation : Référence à l'objet de simulation auquel la cellule appartient.

        Attributs initiaux :
        - content : Contenu actuel de la cellule (None au départ).
        - neighbors : Liste des cellules voisines (vide au départ).
        - is_empty (bool) : True si la cellule est vide.
        - is_prey (bool) : True si la cellule contient une proie.
        - is_predator (bool) : True si la cellule contient un prédateur.
        """

        self.x = x
        self.y = y
        self.content: Optional[Cell] = None
        self.simulation = simulation
        self.neighbors = []
        self.is_empty = True
        self.is_prey = False
        self.is_predator = False

    def update(self, nearest_prey):
        """
        Met à jour l'état de la cellule pour un tour de simulation.

        La cellule met à jour son contenu,
        en fonction de la proie la plus proche et des cellules voisines.
        Si le contenu indique qu'il doit disparaître (retour False), la cellule est vidée.

        Arguments :
        - nearest_prey : Position (x, y) de la proie la plus proche.

        Retourne :
        - None
        """
        local_empty_cells = [cell for cell in self.neighbors if cell.is_empty]
        new_content = self.content.update(nearest_prey=nearest_prey, local_contents=self.neighbors,
                                          local_empty_cells=local_empty_cells)
        if new_content == False:
            self.empty()

    def set_content(self, content):
        """
        Définit le nouveau contenu de la cellule et met à jour son état.

        La méthode ajuste également :
        - la liste des positions de proies ou de prédateurs dans la simulation,
        - les compteurs de proies et de prédateurs,
        - les indicateurs `is_empty`, `is_prey` et `is_predator`.

        Arguments :
        - content : Nouvel occupant de la cellule (objet `Prey`, `Predator` ou None).

        Retourne :
        - None
        """

        self.content = content
        if self.is_prey:
            self.simulation.prey_positions.discard((self.x, self.y))
            self.simulation.nb_prey -= 1
        elif self.is_predator:
            self.simulation.predator_positions.discard((self.x, self.y))
            self.simulation.nb_predator -= 1
        if isinstance(content, Prey):
            self.simulation.prey_positions.add((self.x, self.y))
            self.simulation.nb_prey += 1
            self.is_prey = True
            self.is_empty = False
            self.is_predator = False
        elif isinstance(content, Predator):
            self.simulation.predator_positions.add((self.x, self.y))
            self.simulation.nb_predator += 1
            self.is_predator = True
            self.is_empty = False
            self.is_prey = False
        else:
            self.is_prey = False
            self.is_predator = False
            self.is_empty = True

    def get_content(self):
        """
        Retourne le contenu actuel de la cellule (proie, prédateur ou None).
        """
        return self.content

    def empty(self):
        """
        Vide la cellule après la disparition de son occupant (proie ou prédateur).

        Cette méthode est appelée lorsqu'une proie est mangée ou qu'un prédateur meurt.
        Elle supprime l'occupant, met à jour les listes de positions et les compteurs dans la simulation,
        et marque la cellule comme vide.

        Arguments :
        - Aucun

        Retourne :
        - None
        """

        if self.is_prey:
            self.simulation.prey_positions.discard((self.x, self.y))
            self.simulation.nb_prey -= 1
        elif self.is_predator:
            self.simulation.predator_positions.discard((self.x, self.y))
            self.simulation.nb_predator -= 1
        self.is_prey = False
        self.is_predator = False
        self.content = None
        self.is_empty = True

    def get_position(self):
        """
        Retourne la position (x, y) de la cellule.
        """
        return self.x, self.y



class Simulation:

    def __init__(self, width, height, prey_reproduction_prob, prey_moving_prob, predator_hunting_prob, predator_reproduction_prob, predator_max_hunger, nb_prey_init, nb_predator_init, pixel_size):
        """
        Initialise une nouvelle simulation de proies et de prédateurs.

        La grille est construite vide, les paramètres biologiques des proies et prédateurs sont enregistrés,
        et les structures de suivi des positions sont préparées.

        Arguments :
        - width (int) : Largeur de la grille.
        - height (int) : Hauteur de la grille.
        - prey_reproduction_prob (float) : Probabilité de reproduction d'une proie.
        - prey_moving_prob (float) : Probabilité de déplacement d'une proie.
        - predator_hunting_prob (float) : Probabilité de réussite d'une chasse pour un prédateur.
        - predator_reproduction_prob (float) : Probabilité de reproduction d'un prédateur.
        - predator_max_hunger (int) : Nombre de tours avant qu'un prédateur meure de faim.
        - nb_prey_init (int) : Nombre initial de proies à placer.
        - nb_predator_init (int) : Nombre initial de prédateurs à placer.
        - pixel_size (int) : Taille d'un pixel pour l'affichage graphique.

        Retourne :
        - None
        """

        self.width = width
        self.height = height
        self.grid = [[Cell(x, y, self) for x in range(width)] for y in range(height)]
        self.prey_positions = set()
        self.predator_positions = set()
        self.np_prey_pos = None
        self.prey_reproduction_prob = prey_reproduction_prob
        self.prey_moving_prob = prey_moving_prob
        self.predator_hunting_prob = predator_hunting_prob
        self.predator_reproduction_prob = predator_reproduction_prob
        self.predator_max_hunger = predator_max_hunger
        self.nb_prey_init = nb_prey_init
        self.nb_predator_init = nb_predator_init
        self.pixel_size = pixel_size
        # Pré-calcul des décalages pour trouver les voisins
        self.neighbor_offsets = [(i, j) for i in range(-1, 2) for j in range(-1, 2) if not (i == 0 and j == 0)]
        # Suivi des positions des prédateurs pour accélérer les mises à jour
        self.nb_prey = 0
        self.nb_predator = 0
        self.init_grid()

    def init_grid(self):
        """
        Initialise la grille en plaçant les proies et les prédateurs, et en configurant les voisins.

        Cette méthode effectue les opérations suivantes :
        - Place les proies initiales : pour chaque proie, génère aléatoirement une position vide,
        crée un objet `Prey` avec les paramètres de la simulation et sa position (x, y),
        puis assigne cet objet à la cellule correspondante.
        - Place les prédateurs initiaux de manière similaire
        - Si un double placement est détecté (double couple de même coordonnées), un nouveau tirage est effectué (la cellule n'est pas écrasée).
        - Détermine les voisins de chaque cellule, en connectant les bords de la grille (topologie en tore).
        - Construit un tableau numpy des positions des proies (`np_prey_pos`) pour accélérer les calculs.

        Arguments :
        - Aucun

        Retourne :
        - None
        """

        # Génère la liste de toutes les cases, puis en sélectionne k sans doublon
        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        random.shuffle(all_positions)

        # On prend d’abord les cases pour les proies
        for x, y in all_positions[:self.nb_prey_init]:
            self.grid[y][x].set_content(Prey(self.prey_reproduction_prob,
                                            self.prey_moving_prob, x, y))
            self.prey_positions.add((x, y))

        # Puis, dans la suite de la liste, celles pour les prédateurs
        start = self.nb_prey_init
        for x, y in all_positions[start:start + self.nb_predator_init]:
            self.grid[y][x].set_content(Predator(self.predator_hunting_prob,
                                                self.predator_reproduction_prob,
                                                self.predator_max_hunger, x, y))
            self.predator_positions.add((x, y))

        for y in range(self.height):
            for x in range(self.width):
                for dx, dy in self.neighbor_offsets:
                    nx, ny = x + dx, y + dy
                    if nx < 0:
                        nx = self.width - 1
                    elif nx >= self.width:
                        nx = 0
                    if ny < 0:
                        ny = self.height - 1
                    elif ny >= self.height:
                        ny = 0
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.grid[y][x].neighbors.append(self.grid[ny][nx])
        self.np_prey_pos = np.array(list(self.prey_positions))

    def update(self):
        """
        Met à jour la simulation d’un pas de temps.

        1. Récupère toutes les cellules contenant des proies (prey_cell)
        et des prédateurs (predator_cell).
        2. Pour chaque prédateur, calcule la position (x, y) de la proie
        la plus proche et rassemble ces coordonnées dans nearest_prey
        3. Met à jour chaque proie en lui passant le tableau global
        nearest_prey.
        4. Met à jour chaque prédateur en lui transmettant sa cible
        individuelle (extraite de nearest_prey via son index).
        5. Reconstruit np_prey_pos, tableau NumPy des positions actuelles
        des proies, pour accélérer les recherches au tour suivant.
        """

        prey_cell = []
        predator_cell = []
        for y in range(0, self.height):
            for x in range(0, self.width):
                cell = self.grid[y][x]
                if cell.is_prey:
                    prey_cell.append(cell)
                elif cell.is_predator:
                    predator_cell.append(cell)
        if len(prey_cell) == 0:
            raise RuntimeError("No prey in the simulation")
        nearest_prey = self.get_nearest_prey(self.predator_positions)
        for cell in prey_cell:
            cell.update(None)
        for cell in predator_cell:
            x, y = cell.get_position()
            cell.update(tuple(nearest_prey[y + self.width * x]))
        self.np_prey_pos = np.array(list(self.prey_positions))

    def get_nearest_prey(self, predator_pos):
        """
        Calcule la position de la proie la plus proche pour chaque prédateur.

        Utilise un arbre de recherche KD (`cKDTree`) pour accélérer la recherche
        de la proie la plus proche en distance de Manhattan (p=1).

        Arguments :
        - predator_pos (set) : Ensemble des positions (x, y) des prédateurs.

        Retourne :
        - dict : Dictionnaire associant à chaque identifiant unique de prédateur (y + width * x)
                la position (x, y) de la proie la plus proche.
                Retourne un tableau de zéros si aucune proie ou prédateur n'est présent.
        """

        # Early return if no prey or predators
        if not self.np_prey_pos.size or not predator_pos:
            return np.zeros((len(predator_pos), 2))

        # Convert predator positions to numpy array if not already
        predator_pos_array = np.array(list(predator_pos))

        # Build KD-Tree from prey positions
        tree = cKDTree(self.np_prey_pos)

        # Query the tree for the nearest prey for each predator
        # p=1 specifies Manhattan distance
        _, indices = tree.query(predator_pos_array, k=1, p=1)

        # Get the positions of the nearest prey
        nearest_prey = self.np_prey_pos[indices]
        # Convert to dict with a unique key for each predator

        return dict(zip(predator_pos_array[:,1] + self.width * predator_pos_array[:,0], nearest_prey))


    def render_grid(self, screen):
        """
        Affiche la grille actuelle sur l'écran en représentant les proies et les prédateurs.

        - Remplit l'écran en blanc.
        - Dessine chaque proie en bleu aux coordonnées correspondant à sa position.
        - Dessine chaque prédateur en rouge aux coordonnées correspondantes.
        - Les tailles des cases sont ajustées selon `pixel_size`.

        Arguments :
        - screen : Surface Pygame sur laquelle dessiner la grille.

        Retourne :
        - None
        """

        screen.fill((255, 255, 255))
        color = (0, 0, 255)
        pxl = self.pixel_size
        for prey_pos in self.prey_positions:
            x, y = prey_pos
            pygame.draw.rect(screen, color, (x * pxl, y * pxl, pxl, pxl))

        color = (255, 0, 0)
        for predator_pos in self.predator_positions:
            x, y = predator_pos
            pygame.draw.rect(screen, color, (x * pxl, y * pxl, pxl, pxl))


    def get_grid(self):
        """Renvoie la grille actuelle de la simulation."""
        return self.grid


# Fix KeyboardInterrupt exception
import IPython


def custom_exc(shell, etype, evalue, tb, tb_offset=None):
    if etype == KeyboardInterrupt:
        print("Simulation interrompue par l'utilisateur.")
    else:
        shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)


ip = IPython.get_ipython()
if ip is not None:
    ip.set_custom_exc((KeyboardInterrupt,), custom_exc)

width = 100
height = 100
prey_reproduction_prob = 0.4
prey_moving_prob = 0.7
predator_hunting_prob = 0.5
predator_reproduction_prob = 0.25
predator_max_hunger = 8

nb_prey_init = 1000
nb_predator_init = 1000
pixel_size = 3


def run_simulation(render=False):
    pygame.init()

    nb_preys = []
    nb_predators = []
    if render:
        screen = pygame.display.set_mode((width * pixel_size, height * pixel_size))

    simulation = Simulation(width, height, prey_reproduction_prob, prey_moving_prob, predator_hunting_prob,
                            predator_reproduction_prob, predator_max_hunger, nb_prey_init, nb_predator_init, pixel_size)

    def update_simulation(render):
        simulation.update()
        if render:
            simulation.render_grid(screen)

    try:
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            update_simulation(render)

            nb_preys.append(simulation.nb_prey)
            nb_predators.append(simulation.nb_predator)
            if render:
                pygame.display.flip()
            clock.tick(60)  # Cap at 60 FPS
    except Exception as e:
        if isinstance(e, KeyboardInterrupt):
            print("Simulation interrupted by user.")
        elif isinstance(e, RuntimeError):
            print("Simulation ended: no prey left.")
        else:
            print(e)
            import traceback
            traceback.print_exc()
    finally:
        plt.plot(nb_preys, label="Proies")
        plt.plot(nb_predators, label="Predateurs")
        plt.title("Nombre de proies et de prédateurs au cours du temps")
        plt.xlabel("Temps")
        plt.ylabel("Nombre d'individus")
        plt.legend()
        plt.show()

        plt.plot(nb_preys, nb_predators)
        plt.title("Diagramme de phase")
        plt.xlabel("Nombre de proies")
        plt.ylabel("Nombre de prédateurs")
        plt.show()
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    run_simulation(render=True)