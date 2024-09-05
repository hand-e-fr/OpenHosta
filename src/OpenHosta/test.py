class MonExceptionPersonnalisee(Exception):
    """Exception personnalisée avec des attributs supplémentaires."""
    
    def __init__(self, message, code_erreur, details):
        super().__init__(message)
        self.code_erreur = code_erreur
        self.details = details

    def __str__(self):
        return f"{self.args} (Code d'erreur: {self.code_erreur}, Détails: {self.details})"

def fonction_critique(valeur):
    if valeur < 0:
        raise MonExceptionPersonnalisee(
            "La valeur ne peut pas être négative.", 
            code_erreur=1001, 
            details=f"Valeur fournie : {valeur}"
        )
    return valeur ** 0.5

def main():
    try:
        resultat = fonction_critique(-5)
        print(f"Le résultat est : {resultat}")
    except MonExceptionPersonnalisee as e:
        print(e)  # Cela utilisera la méthode __str__ redéfinie

if __name__ == "__main__":
    main()