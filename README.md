# maya-tools
Creator tools for Autodesk Maya, built using Python, MEL, and PyQt

## subsTexturesUI.py

- Script to build a PxrSurface network from a directory containing various textures
- Launch the UI with the following script:<br /><br />
import subsTexturesUI as stui<br /> 
reload(stui)<br />
ui = stui.showUI()

## fractals.py

- Script to create a variety of fractals, out of instances of a selected object
- Also contains a function to build a randomized, jittered stack of an instanced object
- Load and run "runFractals.py" in Maya to try it out, the four usable functions are given

