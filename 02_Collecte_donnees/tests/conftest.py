import sys
from pathlib import Path

# Permet d'exécuter les tests sans installer le package (pip install -e .)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
