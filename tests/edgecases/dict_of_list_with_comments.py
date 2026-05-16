
from OpenHosta import emulate

# def answer_exactly_this(input:str)->dict[str, list[str]]: # This is the fix for the issue below. The point is that the error report is missleading.
def answer_exactly_this(input:str)->dict[list[str]]: # This is a bad annotation that is being captured by pylance but not by OpenHosta. 
    """
    This is a test function that echo exactliy the input as row text output.
    It is used to test the post processing of the LLM assistant answer.
    
    Argument:
        - input: the content text to echo in the assistant answer quoted in a string
        
    Return:
       The content of input wthout the external string quotes even if it is not a valid string
    """
    return emulate()

vector1 = """
{
    "etapes": [
        "1. Ramasser quotidiennement ou en début de semaine les feuilles mortes sous les érables et chênes, ainsi que l’herbe tondue du jardin ou récupérée auprès de voisins (sans traitement chimique), pour constituer une réserve régulière de matières organiques destinée au paillage.",
        "2. Stocker légèrement les matériaux (feuilles et herbe) dans un bac ou sac en jute à proximité du jardin, en assurant une aération minimale pour éviter la fermentation, tout en respectant un rythme d’intervention d’environ 1 heure par jour ou par semaine selon les besoins.",
        "3. Nettoyer la zone autour des framboisiers en retirant manuellement les limaces tôt le matin ou en soirée, lorsqu’elles sont visibles, afin de préparer un sol propre avant l’application du paillis.",
        "4. Appliquer dès février-mars une première couche de feuilles mortes de 5 à 8 cm d’épaisseur autour des pieds de framboisiers, en laissant un espace libre de 2–3 cm autour du collet pour éviter les pourritures.", # This is a comment
        "5. Recouvrir cette couche de feuilles par 2 à 3 cm d’herbe tondue fraîche, de préférence coupée depuis au moins 24h (légèrement fanée), afin d’améliorer l’adhérence et limiter l’envol du matériau avec le vent.",
        "6. Renouveler le paillage toutes les 6 à 8 semaines durant la saison de croissance (avril à septembre), en ajoutant de nouvelles couches superficielles selon l’état de décomposition, les pluies récentes ou les périodes de sécheresse.",
        "7. Étendre progressivement le paillage vers les zones adjacentes prévues pour les cultures futures (salades, radis, haricots), en ciblant prioritairement les zones ombragées ou à évaporation rapide.",
        "8. Combiner le paillage avec des mesures anti-limaces passives : installer des anneaux de cuivre ou des bords de bouteilles plastiques coupés autour des jeunes plants sensibles, renforçant ainsi la protection sans intrants chimiques.",
        "9. Surveiller mensuellement l’impact du paillage : noter toute réduction dans la fréquence ou la quantité d’arrosage nécessaire, et observer la présence ou non de limaces ; ajuster l’épaisseur ou les matériaux si des carences ou compaction apparaissent.",
        "10. Tenir un suivi léger (notes manuscrites ou numériques) sur la dégradation du paillis, la texture du sol et l’évolution de la végétation, afin d’évaluer à l’automne ou au printemps suivant l’effet bénéfique sur la structure du sol tourbeux."
    ],
    "calendrier": [
        "Fin d'hiver (février-mars) : Appliquer la première couche de paillage épais autour des framboisiers et sur les zones préparées pour les futures plantations, juste avant la reprise végétative.",
        "Printemps à été (avril à septembre) : Renouveler le paillage toutes les 6 à 8 semaines, en alternant couches de feuilles mortes et d’herbe tondue pour éviter l’anaérobiose ; vérifier l’épaisseur (cible : 8–10 cm) et aérer légèrement si nécessaire.",
        "Toute l'année (suivi ponctuel) : Inspecter régulièrement l’état du paillis après fortes pluies ou épisodes de sécheresse ; ajuster localement et intégrer des observations simples dans un carnet de jardin ou système de notes.",
        "Automne (octobre-novembre) : Laisser les dernières couches se décomposer sur place ; prévoir la collecte d’un nouveau stock de feuilles mortes pour l’année suivante sans perturber le sol."
    ]
}
"""

answer_exactly_this(vector1)

##### Rapport d'erreur:

# >>> answer_exactly_this(vector1)
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "<stdin>", line 10, in answer_exactly_this
#   File "/home/ebatt/VSCode_GitRepos/OpenHosta.git/src/OpenHosta/exec/emulate.py", line 51, in emulate
#     return pipeline.execute(inspection, force_llm_args)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/ebatt/VSCode_GitRepos/OpenHosta.git/src/OpenHosta/pipelines/simple_pipeline.py", line 583, in execute
#     raise last_exception
#   File "/home/ebatt/VSCode_GitRepos/OpenHosta.git/src/OpenHosta/pipelines/simple_pipeline.py", line 549, in execute
#     response_data = self.pull(inspection, response_dict)
#                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/ebatt/VSCode_GitRepos/OpenHosta.git/src/OpenHosta/pipelines/simple_pipeline.py", line 514, in pull
#     response_data   = self.pull_type_data_section(inspection, response_string)
#                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/ebatt/VSCode_GitRepos/OpenHosta.git/src/OpenHosta/pipelines/simple_pipeline.py", line 406, in pull_type_data_section
#     l_ret_data = type_returned_data(response, inspection.analyse.type)
#                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/ebatt/VSCode_GitRepos/OpenHosta.git/src/OpenHosta/guarded/resolver.py", line 89, in type_returned_data
#     raise ValueError(error_msg)
# ValueError: Impossible de convertir la réponse du LLM vers le type dict[list[str]].

# === Réponse du LLM ===
# {
#     "etapes": [
#         "1. Ramasser quotidiennement ou en début de semaine les feuilles mortes sous les érables et chênes, ainsi que l’herbe tondue du jardin ou récupérée auprès de voisins (sans traitement chimique), pour constituer une réserve régulière de matières organiques destinée au paillage.",
#         "2. Stocker légèrement les matériaux (feuilles et herbe) dans un bac ou sac en jute à proximité du jardin, en assurant une aération minimale pour éviter la fermentation, tout en respectant un rythme d’intervention d’environ 1 heure par jour ou par semaine selon les besoins.",
#         "3. Nettoyer la zone autour des framboisiers en retirant manuellement les limaces tôt le matin ou en soirée, lorsqu’elles sont visibles, afin de préparer un sol propre avant l’application du paillis.",
#         "4. Appliquer dès février-mars une première couche de feuilles mortes de 5 à 8 cm d’épaisseur autour des pieds de framboisiers, en laissant un espace libre de 2–3 cm autour du collet pour éviter les pourritures.",
#         "5. Recouvrir cette couche de feuilles par 2 à 3 cm d’herbe tondue fraîche, de préférence coupée depuis au moins 24h (légèrement fanée), afin d’améliorer l’adhérence et limiter l’envol du matériau avec le vent.",
#         "6. Renouveler le paillage toutes les 6 à 8 semaines durant la saison de croissance (avril à septembre), en ajoutant de nouvelles couches superficielles selon l’état de décomposition, les pluies récentes ou les périodes de sécheresse.",
#         "7. Étendre progressivement le paillage vers les zones adjacentes prévues pour les cultures futures (salades, radis, haricots), en ciblant prioritairement les zones ombragées ou à évaporation rapide.",
#         "8. Combien le paillage avec des mesures anti-limaces passives : installer des anneaux de cuivre ou des bords de bouteilles plastiques coupés autour des jeunes plants sensibles, renforçant ainsi la protection sans intrants chimiques.",
#         "9. Surveiller mensuellement l’impact du paillage : noter toute réduction dans la fréquence ou la quantité d’arrosage nécessaire, et observer la présence ou non de limaces ; ajuster l’épaisseur ou les matériaux si des carences ou compaction apparaissent.",
#         "10. Tenir un suivi léger (notes manuscrites ou numériques) sur la dégradation du paillis, la texture du sol et l’évolution de la végétation, afin d’évaluer à l’automne ou au printemps suivant l’effet bénéfique sur la structure du sol tourbeux."
#     ],
#     "calendrier": [
#         "Fin d'hiver (février-mars) : Appliquer la première couche de paillage épais autour des framboisiers et sur les zones préparées pour les futures plantations, juste avant la reprise végétative.",
#         "Printemps à été (avril à septembre) : Renouveler le paillage toutes les 6 à 8 semaines, en alternant couches de feuilles mortes et d’herbe tondue pour éviter l’anaérobiose ; vérifier l’épaisseur (cible : 8–10 cm) et aérer légèrement si nécessaire.",
#         "Toute l'année (suivi ponctuel) : Inspecter régulièrement l’état du paillis après fortes pluies ou épisodes de sécheresse ; ajuster localement et intégrer des observations simples dans un carnet de jardin ou système de notes.",
#         "Automne (octobre-novembre) : Laisser les dernières couches se décomposer sur place ; prévoir la collecte d’un nouveau stock de feuilles mortes pour l’année suivante sans perturber le sol."
#     ]
# }
# ======================

# === Détail de l'erreur ===
# → Valeur pour la clé 'etapes': Type invalide. Reçu ['1. Ramasser quotidiennement ou en début de semaine les feuilles mortes sous les érables et chênes, ainsi que l’herbe tondue du jardin ou récupérée auprès de voisins (sans traitement chimique), pour constituer une réserve régulière de matières organiques destinée au paillage.', '2. Stocker légèrement les matériaux (feuilles et herbe) dans un bac ou sac en jute à proximité du jardin, en assurant une aération minimale pour éviter la fermentation, tout en respectant un rythme d’intervention d’environ 1 heure par jour ou par semaine selon les besoins.', '3. Nettoyer la zone autour des framboisiers en retirant manuellement les limaces tôt le matin ou en soirée, lorsqu’elles sont visibles, afin de préparer un sol propre avant l’application du paillis.', '4. Appliquer dès février-mars une première couche de feuilles mortes de 5 à 8 cm d’épaisseur autour des pieds de framboisiers, en laissant un espace libre de 2–3 cm autour du collet pour éviter les pourritures.', '5. Recouvrir cette couche de feuilles par 2 à 3 cm d’herbe tondue fraîche, de préférence coupée depuis au moins 24h (légèrement fanée), afin d’améliorer l’adhérence et limiter l’envol du matériau avec le vent.', '6. Renouveler le paillage toutes les 6 à 8 semaines durant la saison de croissance (avril à septembre), en ajoutant de nouvelles couches superficielles selon l’état de décomposition, les pluies récentes ou les périodes de sécheresse.', '7. Étendre progressivement le paillage vers les zones adjacentes prévues pour les cultures futures (salades, radis, haricots), en ciblant prioritairement les zones ombragées ou à évaporation rapide.', '8. Combien le paillage avec des mesures anti-limaces passives : installer des anneaux de cuivre ou des bords de bouteilles plastiques coupés autour des jeunes plants sensibles, renforçant ainsi la protection sans intrants chimiques.', '9. Surveiller mensuellement l’impact du paillage : noter toute réduction dans la fréquence ou la quantité d’arrosage nécessaire, et observer la présence ou non de limaces ; ajuster l’épaisseur ou les matériaux si des carences ou compaction apparaissent.', '10. Tenir un suivi léger (notes manuscrites ou numériques) sur la dégradation du paillis, la texture du sol et l’évolution de la végétation, afin d’évaluer à l’automne ou au printemps suivant l’effet bénéfique sur la structure du sol tourbeux.'] (type: list).
# >>> 