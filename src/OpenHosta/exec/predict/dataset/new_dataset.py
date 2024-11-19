from typing import Any, Dict, List, Optional, Tuple

from .sample_type import Sample

class Hostadataset:
    ### Gestion de données ###
    def add(self, sample) -> None:
        """Ajoute un sample à l'ensemble de données."""
        pass

    def remove(self, condition: callable, dataset: Optional[List[Sample]] = None) -> List[Sample]:
        """Supprime les samples qui remplissent une certaine condition."""
        pass

    def filter_data(self, condition: callable, dataset: Optional[List[Sample]] = None) -> List[Sample]:
        """Filtre les données en fonction d'une condition donnée."""
        pass

    def duplicate_data(self, factor: int, dataset: Optional[List[Sample]] = None) -> List[Sample]:
        """Duplique chaque sample un certain nombre de fois."""
        pass

    def shuffle_data(self, dataset: Optional[List[Sample]] = None) -> List[Sample]:
        """Mélange les données pour éviter les biais d’ordre."""
        pass

    ### Préparation et conversion ###
    def encode(self, max_tokens: int, dataset: Optional[List[Sample]] = None) -> None:
        """Encode les données avec une limite de tokens."""
        pass

    def decode(self, dataset: Optional[List[Sample]] = None) -> List[Sample]:
        """Décodage des données."""
        pass

    def encode_inference(self, sample: Sample) -> Sample:
        """Encode un échantillon unique pour l'inférence."""
        pass

    def split_data(self, ratios: tuple = (0.8, 0.1, 0.1), dataset: Optional[List[Sample]] = None) -> Tuple[List[Sample], List[Sample], List[Sample]]:
        """Divise les données en ensembles train, validation et test selon les ratios donnés."""
        pass

    @staticmethod
    def convert_list(data: list) -> List[Sample]:
        """Convertit une liste en une liste de samples."""
        pass

    @staticmethod
    def convert_dict(data: dict) -> List[Sample]:
        """Convertit un dictionnaire en une liste de samples."""
        pass

    @staticmethod
    def convert_files(path: str, source_type: Optional[SourceType] = None) -> List[Sample]:
        """Convertit des fichiers situés dans un chemin en une liste de samples."""
        pass

    @staticmethod
    def convert_to_dataframe(data: List[Sample]) -> "pandas.DataFrame":
        """Convertit les données en un DataFrame pandas."""
        pass

    @staticmethod
    def convert_from_dataframe(df: "pandas.DataFrame") -> List[Sample]:
        """Crée des samples à partir d’un DataFrame pandas."""
        pass

    @staticmethod
    def normalize_data(data: List[Sample]) -> List[Sample]:
        """Applique une normalisation sur les données."""
        pass

    ### Visualisation ###
    def plot_data_distribution(self, dataset: Optional[List[Sample]] = None) -> None:
        """Affiche la distribution des données pour analyse."""
        pass

    def preview_samples(self, n: int = 5, dataset: Optional[List[Sample]] = None) -> None:
        """Affiche un aperçu de N samples."""
        pass

    ### Opérations avancées ###
    def balance_classes(self, dataset: Optional[List[Sample]] = None) -> List[Sample]:
        """Rééquilibre les classes pour éviter les biais."""
        pass

    def augment_data(self, method: str = "default", dataset: Optional[List[Sample]] = None) -> List[Sample]:
        """Augmente les données selon une méthode spécifiée."""
        pass

    def cache_processed_data(self, path: str, dataset: Optional[List[Sample]] = None) -> None:
        """Met en cache les données traitées pour réutilisation."""
        pass

    def generate_synthetic_samples(self, model: Any, num_samples: int) -> List[Sample]:
        """Utilise un modèle pour générer des données synthétiques."""
        pass

    ### Statistiques ###
    def compute_statistics(self, dataset: Optional[List[Sample]] = None) -> Dict[str, Any]:
        """Calcule des statistiques globales sur les données (moyenne, écart type, etc.)."""
        pass

    def count_classes(self, dataset: Optional[List[Sample]] = None) -> Dict[Any, int]:
        """Compte les occurrences pour chaque classe dans les données."""
        pass

    ### Interaction avec des modèles ###
    def evaluate_model(self, model: Any, metric: str = "accuracy", dataset: Optional[List[Sample]] = None) -> float:
        """Évalue un modèle sur les données."""
        pass

    def batch_inference(self, model: Any, dataset: Optional[List[Sample]] = None) -> List[Any]:
        """Applique une inférence par lot avec un modèle donné."""
        pass

    def generate_predictions(self, model: Any, dataset: Optional[List[Sample]] = None) -> List[Any]:
        """Génère des prédictions pour les données."""
        pass

    ### Sauvegarde et export ###
    def save_data(self, path: str) -> None:
        """Sauvegarde les données dans un fichier."""
        pass

    def load_data(self, path: str) -> List[Sample]:
        """Charge les données à partir d’un fichier."""
        pass

    def export_to_csv(self, path: str, dataset: Optional[List[Sample]] = None) -> None:
        """Exporte les données au format CSV."""
        pass

    def export_to_json(self, path: str, dataset: Optional[List[Sample]] = None) -> None:
        """Exporte les données au format JSON."""
        pass

    @staticmethod
    def load_from_csv(path: str) -> List[Sample]:
        """Charge des données à partir d’un fichier CSV."""
        pass

    @staticmethod
    def load_from_json(path: str) -> List[Sample]:
        """Charge des données à partir d’un fichier JSON."""
        pass

    ### Création de dataloaders ###
    def create_dataloaders(self, batch_size: int, shuffle: bool = True, dataset: Optional[List[Sample]] = None) -> Any:
        """Crée des DataLoaders à partir des données."""
        pass
