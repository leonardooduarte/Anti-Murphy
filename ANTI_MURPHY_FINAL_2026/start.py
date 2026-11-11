"""Anti-Murphy, local single-process launch. Python 3.10+; no additional packages."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from atelier.server import main
if __name__=='__main__':main()
