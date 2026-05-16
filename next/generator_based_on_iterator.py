from OpenHosta import emulate

ideas = [
    "Planter des bandes de couvre-sol comme le trèfle blanc autour des cultures pour limiter l'évaporation, enrichir le sol en azote et créer un habitat pour les auxiliaires contre les limaces.",
    "Installer un système de paillage épais avec des feuilles mortes et de l'herbe tondue pour protéger le sol tourbeux, réduire l'arrosage et empêcher la prolifération des limaces en leur ôtant des abris.",
    "Placer des cultures grimpantes comme les haricots et les pois gourmands sur des tipis en bois léger près de la palissade, orientés sud-ouest pour capter un maximum de lumière tout en préservant l'espace.",
    "Introduire des plantes compagnes répulsives pour les limaces, comme l'ail, la ciboulette et le thym, autour des salades et des jeunes pousses vulnérables.",
    "Prévoir des cultures en successions échelonnées pour les radis et les salades afin d’étaler les récoltes sur toute la saison et éviter les surplus en une seule fois.",
    "Utiliser des bouteilles en plastique coupées comme protections individuelles contre les limaces pour les jeunes plants, méthode peu coûteuse et facile à déplacer.",
    "Planifier une association de plantes en guildes autour des framboisiers existants, incluant du fenouil, de la coriandre et de l’aneth pour attirer les insectes bénéfiques et améliorer la pollinisation.",
    "Créer un petit banc en bois près du jardin pour encourager des observations régulières et des interventions douces, adaptées à une disponibilité limitée de 1h/jour, facilitant un suivi permacole serein.",
    "Utiliser des bacs de culture en bois ou en plastique recyclé installés près de la maison pour cultiver les salades et les radis, permettant un contrôle facile du sol et de l'humidité tout en évitant les limaces grâce à une élévation simple.",
    "Créer un semis en carrés successifs pour les haricots et les pois gourmands, espacés de deux semaines, afin d’échelonner la récolte et mieux adapter l’entretien à 1h/jour.",
    "Planter des fleurs comestibles comme les capucines et les soucis autour des légumes pour repousser naturellement les ravageurs et attirer les pollinisateurs, tout en ajoutant de la diversité alimentaire.",
    "Mettre en place un arrosage manuel ciblé le matin, en utilisant un arrosoir avec une rose fine, pour éviter l’humidité stagnante qui attire les limaces, tout en s’adaptant aux besoins réels des plantes.",
    "Délimiter une petite zone ensoleillée pour un carré de pommes de terre en sacs ou en grands contenants, facile à gérer et à vidanger en fin de saison, sans perturber le sol existant.",
    "Utiliser du marc de café récupéré localement, épandu modérément autour des jeunes plants sensibles, pour repousser les limaces de manière simple et renouvelable.",
    "Utiliser des bâtonnets de cendre de bois autour des jeunes pousses comme barrière naturelle contre les limaces, en alternance avec les anneaux de cuivre pour varier les protections et éviter l’habitude.",
    "Planter des pieds de fraisiers en carrés espacés près des framboisiers existants, en les protégeant avec des rondelles de bouteilles en plastique pour limiter les limaces et favoriser une microzone de chaleur.",
    "Semer des radis en lignes courtes toutes les deux semaines dans des bacs surélevés, en alternant avec de la roquette et de la cresson pour une diversité rapide de microsalades sans rotation de sol.",
    "Mettre en œuvre un arrosage au goutte-à-goutte simple avec des bouteilles en plastique percées enterrées à côté des pieds de tomates, pour une irrigation lente et ciblée le matin.",
    "Utiliser des feuilles de chou ramassées localement comme paillage temporaire autour des salades, pour créer une barrière physique contre les limaces tout en s’intégrant au compost progressivement."
    ]

from typing import Iterator

def identify_main_thematic(sentences:list[str]) ->  str:
    """
    Identify the main thematic of this list of sentences
    
    Return:
       The thematic in a document title style
    """
    return emulate()

thematic = identify_main_thematic(ideas)    

def find_common_concepts(sentences:list[str], max_concepts:int=10) ->  Iterator[str]:
    """
    Identify common concepts in a list of sentences
    """
    return emulate()

common = list(find_common_concepts(ideas))

def find_differanciating_concepts(sentences:list[str], max_concepts:int=10) ->  Iterator[str]:
    """
    Identify differanciating concepts in a list of sentences
    """
    return emulate()

diff = list(find_differanciating_concepts(ideas))

def group_by_thematics(concepts:list[str]) ->  dict[str, list[str]]:
    """
    Group concepts by disjoint thematics
    """
    return emulate()

classes = group_by_thematics(common+diff)    
len(classes)

def extend_classes_within_thematic(overall_thematic:str, thematic:str, concepts:list[str], max_concepts:int=5) -> list[str]:
    """
    Extend the list of concepts with the given thematic knowing the overall thematic.
    
    Arguments:
      overall_thematic: the overall thematic of the
      thematic: the thematic of the concepts
      concepts: the list of concepts to extend within the
      max_concepts: the maximum number of concepts to return
      
    Return:
      the list of concepts extended within the thematic
    """
    return emulate()
    
extended_classes = {k:extend_classes_within_thematic(thematic, k, v) for k,v in classes.items()}
print(extended_classes)

def reformulate_as_exclusive_classes(thematic:str, concepts:list[str]) -> list[str]:
    """
    Rearange the list of concepts to make them exclusive. 
    This produces a list of concepts that are mutually exclusive.
    The returned list is of the same size or smaller if concepts were redundant.
    
    Arguments:
       thematic: the thematic of the concepts
       concepts: the list of concepts to rearange within the themtic
       
    Return:
      the list of concepts rearanged to be exclusive
    """
    return emulate()
    
from typing import TypeAlias
Classification: TypeAlias = dict[str, str]
ClassificationPoint: TypeAlias = dict[str, dict[str, list[int]]]

exclusive_classes:Classification = {k:reformulate_as_exclusive_classes(k, v) for k,v in extended_classes.items()}

classes_2 =  {"gestion de l'eau": ['arrosage traditionnel ou manuel', 'irrigation au goutte-à-goutte', 'récupération des eaux de pluie', 'méthodes de culture en lasagnes pour retenir l’humidité', "économie d'eau par techniques combinées"],                                                                                                                                   'agencement et planification': ['plantation en succession sans utilisation de conteneurs', 'successions échelonnées en plein sol', 'cultures en conteneurs sans support vertical', 'bacs de culture surélevés non associés à des successions', 'cultures grimpantes indépendantes des successions et conteneurs'], 'protection des plantes': ['protection physique des jeunes plants (ex. : capuchons, filets, tuteurs)', 'utilisation de plantes compagnes répulsives pour protéger les cultures', 'encouragement des insectes bénéfiques par des habitats ou ressources attractives', 'paillage organique ou minéral empêchant l’accès ou la prolifération des ravageurs'],                                                                                                                                                                                                                                                          'biodiversité et synergies végétales': ["plantes compagnes (symbiose fonctionnelle sans superposition avec d'autres rôles)", "guildes de plantes (groupes fonctionnels complets structurés autour d'une niche écologique, non chevauchante avec l'intercalage)", 'fleurs comestibles à usage alimentaire distinct des interactions biotiques', 'plantes résistantes aux ravageurs (défense intrinsèque, sans recouvrement avec le compagnonnage actif)', 'intercalage cultural (technique temporo-spatiale de culture, indépendante des propriétés biologiques des espèces)'], 'pratiques durables et matériaux': ['utilisation de matériaux recyclés', 'paillage organique pour la rétention d’eau', 'rotation des cultures pour prévenir les maladies du sol', 'emploi de compost maison enrichi en micro-organismes bénéfiques'], 'observation et suivi': ['observation régulière des cultures ou sites', 'suivi exclusif des cycles de croissance des espèces ciblées', 'évaluation indépendante des populations de ravageurs', 'enregistrement exclusif des conditions météorologiques locales', 'analyse des interactions écologiques sans chevauchement avec le suivi biotique']}
classes =    {"Gestion de l'eau": ['arrosage', 'arrosage manuel ciblé', 'arrosage au goutte-à-goutte maison', 'récupération de matériaux locaux', 'optimisation de l’espace', 'collecte des eaux de pluie', 'bassins de rétention d’eau', 'paillage pour réduire l’évaporation', 'zonestion hydrique en terrasses', 'swales pour infiltration', 'rotation des zones d’arrosage'], 'Paillage et couverture du sol': ['paillage', 'paillage épais', 'couvre-sol', 'paillage avec feuilles de chou', 'amélioration du sol', 'mulching organique', 'résidus végétaux comme paillis', "paillage pour la rétention d'eau", 'suppression des mauvaises herbes par couverture', 'paillage et biodiversité du sol', 'rotation du type de paillis', 'paillage et succession des cultures', 'couverture végétale vivante', 'paillage et activités microbiennes', 'paillage en permaculture forestière'], 'Protection des plantes': ['protection des jeunes plants', 'protections individuelles en bouteilles', 'fraisiers protégés avec rondelles', 'bacs de culture élevés', 'utilisation de filets anti-insectes', 'paillage pour limiter les nuisibles', 'plantes compagnes répulsives (tagète, basilic)', 'barrières physiques en cuivre contre les limaces', 'pièges à phéromones pour papillons', 'abris tunnel amovibles'], 'Lutte naturelle et biodiversité': ['soutien aux insectes bénéfiques', 'méthodes naturelles de répulsion', 'plantes compagnes répulsives', 'diversité végétale', 'fleurs comestibles', 'bâtonnets de cendre', 'marc de café', 'haies insectifuges', 'pièges naturels à limaces', 'rotation des cultures associée', 'bandes fleuries', 'abris pour prédateurs naturels', 'infusions de plantes répulsives'],                                                                                                                                                                     'Associations et organisation végétale': ['plantes compagnes', 'guildes de plantes', 'guildes de plantes', 'cultures grimpantes sur tipis', 'cultures en successions échelonnées', 'semis en carrés successifs', 'successions échelonnées', 'association sol-poissons-plantes (aquaponie implicite)', 'organisation en guildes fonctionnelles (sol, sous-sol, canopée)', 'rotation de cultures inspirée des écosystèmes naturels', 'couverture végétale permanente pour la santé du sol', 'diversité végétale pour résilience aux ravageurs'], 'Aménagements et recyclage': ["utilisation d'objets recyclés", "banc d'observation", 'pommes de terre en contenants', 'radis en bacs surélevés', 'récupération de matériaux locaux', 'paillage avec déchets organiques', 'buttes maraîchères en pallets recyclés', 'collecte des eaux de pluie dans des fûts réutilisés', 'sentiers en bouteilles plastiques compressées', 'composteur bricolé à partir de palettes'], 'Faible intensité temporelle': ['adaptation à une faible disponibilité temporelle', 'techniques de jardinage peu exigeantes en temps', 'plantations en couches étagées pour minimiser l’entretien', 'utilisation de couvre-sols vivants pour réduire le désherbage', 'mélanges de plantes compagnes favorisant l’autorégulation', 'systèmes de culture en lasagnes (sheet mulching) nécessitant peu d’intervention ultérieure', 'choix de variétés rustiques et pérennes adaptées à la gestion passive'], 'Amélioration des sols et fertilisation': ['amélioration du sol', 'marc de café', 'bâtonnets de cendre', 'compost maison', 'paillage organique', 'rotation des cultures', 'plantes de couverture', 'fertilisation naturelle'], 'Mollusques et ravageurs': ['limaces', 'escargots', 'limaces grises', 'limaces noires', 'petits mollusques', 'ravageurs nocturnes', 'vers de terre parasites']}
ex_classes = {"Gestion de l'eau": ['arrosage manuel ciblé', 'arrosage au goutte-à-goutte maison', 'collecte des eaux de pluie', 'bassins de rétention d’eau', 'paillage pour réduire l’évaporation', 'zonestion hydrique en terrasses', 'swales pour infiltration', 'rotation des zones d’arrosage'], 'Paillage et couverture du sol': ['paillage épais (applications >10 cm)', 'couvre-sol mince ou partiel (applications <10 cm)', 'couverture végétale vivante (engrais vert, graminées, légumineuses)', 'mulching organique spécifique (feuilles de chou, résidus végétaux localisés)', 'paillage fonctionnel pour rétention hydrique', 'paillage visant la suppression des adventices', 'paillage stimulant la biodiversité microbienne du sol', 'rotation planifiée des matériaux de paillage', 'intégration du paillage dans la succession culturale', 'application du paillage en système de permaculture forestière'], 'Protection des plantes': ['Protection mécanique individuelle des jeunes plants (ex. : bouteilles, rondelles)', 'Structures de protection collective (ex. : bacs élevés, abris tunnels)', 'Barrières physiques ou matérielles contre les nuisibles (ex. : filets anti-insectes, bandes de cuivre)', 'Techniques culturales de lutte contre les nuisibles (ex. : paillage, plantes compagnes répulsives)', 'Pièges ciblés pour insectes ravageurs (ex. : pièges à phéromones)'], 'Lutte naturelle et biodiversité': ['soutien aux insectes bénéfiques', 'méthodes naturelles de répulsion chimique ou olfactive', 'utilisation de plantes compagnes répulsives ou attractives', 'diversité végétale favorisant la biodiversité', 'aménagement d’habitats pour prédateurs naturels (haies, abris, bandes fleuries)', 'pratiques culturales préventives (rotation des cultures, diversité spatiale)', 'pièges naturels pour ravageurs (limaces, insectes)', 'utilisation de sous-produits naturels répulsifs (cendre, marc de café)'], 'Associations et organisation végétale': ['plantes compagnes', 'guildes de plantes', 'cultures grimpantes sur tipis', 'cultures en successions échelonnées', 'semis en carrés successifs', 'association sol-poissons-plantes (aquaponie implicite)', 'organisation en guildes fonctionnelles (sol, sous-sol, canopée)', 'rotation de cultures inspirée des écosystèmes naturels', 'couverture végétale permanente pour la santé du sol', 'diversité végétale pour résilience aux ravageurs'], 'Aménagements et recyclage': ['Aménagements utilisant des objets recyclés ou récupérés', 'Structures de culture surélevées (bacs, conteneurs, pallets)', 'Techniques de gestion organique (paillage, compostage)', 'Systèmes de collecte et de réutilisation de l’eau', 'Sentiers ou chemins en matériaux recyclés'], 'Faible intensité temporelle': ["aménagement visant l'adaptation à une faible disponibilité temporelle, incluant la conception globale du jardin pour minimiser les interventions", 'techniques spécifiques de jardinage peu exigeantes en temps, telles que le binage simplifié ou les arrosages espacés', 'plantations en couches étagées (agroforesterie réduite) conçues pour autonomie accrue et entretien minimal', 'utilisation exclusive de couvre-sols vivants comme stratégie de réduction du désherbage manuel', 'association de plantes compagnes sélectionnées pour favoriser l’autorégulation naturelle (protection biologique, limitation des ravageurs)', 'mise en place de systèmes de culture en lasagnes (sheet mulching) sans besoin d’interventions régulières après l’installation', 'choix ciblé de variétés végétales rustiques, pérennes et adaptées à une gestion passive, excluant tout entretien fréquent'], 'Amélioration des sols et fertilisation': ['amélioration du sol par apport organique (compost maison, paillage organique)', 'utilisation de sous-produits spécifiques (marc de café, bâtonnets de cendre)', 'techniques culturales favorisant la fertilité (rotation des cultures, plantes de couverture)', 'fertilisation naturelle généralisée (hors cas spécifiques)'], 'Mollusques et ravageurs': ['limaces grises', 'limaces noires', 'escargots', 'autres mollusques (non spécifiés)', 'ravageurs nocturnes non-mollusques', 'vers de terre parasites']}

str_classes = [f"[{k}]/{v}" for k,u in exclusive_classes.items() for v in u]
len(str_classes)

def rate_idea(idea:str, classes:list[str]) -> dict[str, int]:
    """
    Provide a rating between 1 and 9 that indicates if the idea is a good fit for the class.
    The rating is based on the semantic similarity between the idea and the class.
    
    Rating = 1: the idea is explicitly at the opposite of the class
    Rating = 2: the idea explicitly mean that the opposite of the class is expected
    Ratinf = 3: the idea implicitly mean that the opposite of the class is expected
    Ratinf = 4: the idea could implicitly mean that an idea that is the opposite of the class is expected 
    Rating = 5: there is no way to deduce if the idea is a good fit for the class or not
    Rating = 6: the idea could implicitly mean that an idea that is a good fit for the class is expected
    Rating = 7: the idea implicitly mean that the class is expected
    Rating = 8: the idea explicitly mean that the class is expected
    Rating = 9: the idea is explicitly a good of the class
        
    Arguments:
       idea: The idea to rate
       classes: The classes to rate the idea for
       
    Returns:
        A dictionary with the class as key and the rating as value. Do not provide any explanation or comment
    """
    return emulate()

estimate = rate_idea(idea=ideas[0], classes=str_classes)
len([k for k in estimate.keys() if k in str_classes])
len([k for k in estimate.keys() if k not in str_classes])
# Il en résulta une grande matrice avec le niveau de corrélation par combinatoire de classifications

def print_estimate(estimate:dict[str, int]):
    last_cat = ""
    for k,v in estimate.items():
        category = k.split("]/")[0].strip("[")
        subcat = k.split("]/")[1]
        if last_cat != category:
          print(f"\n{category}:\n==============")
        last_cat = category
        print(f"    {subcat:<100}:{v-5:>3}")

print(ideas[0])
print_estimate(estimate)

print_estimate(rate_idea("Analyser des interactions écologiques sans chevauchement avec le suivi biotique", str_classes))    
print_estimate(rate_idea("Analyser des interactions écologiques qui ont un chevauchement avec le suivi biotique", str_classes))    

def clean_estimate(estimate:dict[str, int]) -> ClassificationPoint:
    structured_estimate:ClassificationPoint = {}
    for d, value in estimate.items():
        category = d.split("]/")[0].strip("[")
        sub_category = d.split("/")[1]
        if category not in structured_estimate:
            structured_estimate[category] = {}
            structured_estimate[category]["total"] = []
        if sub_category not in structured_estimate[category]:
            structured_estimate[category][sub_category] = []
        structured_estimate[category][sub_category] += [value]
        structured_estimate[category]["total"] += [value]


    # le faire dans l'autre sens pour ignorer les erreurs de génération
    for k,v in exclusive_classes.items():
        if k not in structured_estimate:
            print(f"Missing {k}")
            structured_estimate[k] = {vv:[5] for vv in v}
            structured_estimate[k] |= {"total":[5 for _ in v]} 
        for vv in v:
            if vv not in structured_estimate[k]:
                print(f"Missing {vv} in {k}")
                structured_estimate[k][vv] = [5]
            
    return structured_estimate
      
def compute_distance(estimate_a:dict[str, int],estimate_b:dict[str, int])->tuple[float, dict[str,float]]:
    """
    Compute the distance between two classification points
    """
    a = clean_estimate(estimate_a)
    b = clean_estimate(estimate_b)
    
    flat_element_count = 0
    flat_distance = 0
    flat_distance_normalized:float = 0
    by_category_distance:dict[str,int] = {}
    by_category_distance_normalized:dict[str,float] = {}
    for cat,subcat_list in a.items():
        by_category_distance[cat] = 0
        for subcat in subcat_list:
            flat_element_count += 1
            subcat_distance = abs(a[cat][subcat][0] - b[cat][subcat][0])
            by_category_distance[cat] += subcat_distance
            flat_distance += subcat_distance
        by_category_distance_normalized[cat] = float(by_category_distance[cat]) / len(subcat_list)
    flat_distance_normalized = float(flat_distance) / (flat_element_count)
    
    return flat_distance_normalized, by_category_distance_normalized
    
estimate1 = rate_idea(idea="labourer le jardin avec un tracteur", classes=str_classes)
print_estimate(estimate1)
estimate1bis = rate_idea(idea="labourer le jardin avec un tracteur et de l'engrais", classes=str_classes)

estimate1b = rate_idea(idea="mettre un insecticide pour tuer les vers et un fongicide", classes=str_classes)
print_estimate(estimate1b)

estimate2 = rate_idea(idea="faucher l'herbe", classes=str_classes)

estimate3 = rate_idea(idea="tondre la pelouse", classes=str_classes)

hors_sujet = off_topic_location(exclusive_classes)
point_neutre = neutral_location(exclusive_classes)

compute_distance(estimate1, estimate1bis)
compute_distance(estimate1, estimate1b)
compute_distance(estimate1, estimate2)
compute_distance(estimate2, estimate3)