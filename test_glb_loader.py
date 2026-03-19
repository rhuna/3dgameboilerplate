from pathlib import Path
from panda3d.core import Filename
from direct.showbase.ShowBase import ShowBase

base = ShowBase(windowType='offscreen')

model_path = Path("assets/models/characters/player9.glb").resolve()
print("Testing GLB loading...")
print("Windows path:", model_path)
print("Exists:", model_path.exists())

panda_path = Filename.from_os_specific(str(model_path)).get_fullpath()
print("Panda path:", panda_path)

try:
    model = base.loader.loadModel(panda_path)
    print("LOAD SUCCESS")
    print("Node name:", model.getName())
    print("Children:", model.getNumChildren())
    print("Tight bounds:", model.getTightBounds())
except Exception as e:
    print("LOAD FAILED:", e)