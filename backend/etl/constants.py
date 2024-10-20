from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
HF_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".huggingface"
MODEL_DIR = ROOT_DIR.parent / "models"
