import os
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join((Path(__file__).parent.parent), "models")
