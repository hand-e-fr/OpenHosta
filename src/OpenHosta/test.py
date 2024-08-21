def my_decorator(func):
    def wrapper(*args, **kwargs):
        # Vous pouvez ajouter ici tout comportement que vous souhaitez pour le décorateur
        print("Fonction appelée avec les arguments:", args, kwargs)
        return func(*args, **kwargs)

    # Ajouter un attribut à la fonction décorée
    wrapper.custom_attribute = "Ceci est un attribut personnalisé"
    return wrapper

@my_decorator
def example_function(x, y):
    return x + y

# Appel de la fonction décorée
print(example_function(2, 3))

# Accès à l'attribut personnalisé ajouté par le décorateur
print(example_function.custom_attribute)