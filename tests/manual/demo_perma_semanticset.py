

# Créer un routeur sémantique
my_ideas = SemanticDict(key_axis="Permaculture ideas", tolerance=0.05)

if "Faire pousser les haricots avec des tuteurs" not in my_ideas: 
    my_ideas["Faire pousser les haricots avec des tuteurs"] = []

my_ideas["Faire pousser les haricots avec des tuteurs"].append("Faire pousser les haricots avec des tuteurs")

idea1= "Faire pousser les haricots avec des tuteurs"
idea2= "Enrichir le sol avec des composts"
idea3= "Mettre du compost dans le sol"
idea4= "Mettre du paillis"

all_ideas = [idea1, idea2, idea3, idea4]

for idea in all_ideas:
    if idea not in my_ideas:
        my_ideas[idea] = []
    my_ideas[idea].append(idea)
    
print(my_ideas)

out = {
    'Faire pousser les haricots avec des tuteurs': 
        ['Faire pousser les haricots avec des tuteurs'],
    'Enrichir le sol': 
        ['Enrichir le sol avec des composts', 
         'Mettre du compost dans le sol', 
         'Mettre du paillis']
}