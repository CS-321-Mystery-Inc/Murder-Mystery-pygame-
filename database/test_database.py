
from database import *

initialize_database()

collect_evidence(
    1,
    "Mysterious Letter",
    "A letter discovered in the library.",
    "Player 1"
)

collect_evidence(
    2,
    "Broken Watch",
    "A watch found near the crime scene.",
    "Player 2"
)

update_game_state("investigation_stage", "2")

print(get_evidence())
