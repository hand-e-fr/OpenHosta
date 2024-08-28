from OpenHosta.emulate_pydantic import _exec_emulate, thought
from config import model_config
from analytics import Models
from OpenHosta.exec_pydantic import ExecutiveFunction

emulate = ExecutiveFunction(_exec_emulate)

__all__ = emulate, thought, model_config, Models


# TODO:
#  The pydantic models is send in JSON to the emulate
#  Changer La demande au modèle pour qu'il sorte que le pydantic demandé
#  Changer donc le prompt +(sortie si elle est spécifié autrement)