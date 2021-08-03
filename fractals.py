from maya import cmds
import random

'''
Place this file and "runFractals.py" into your "scripts" folder for your current Maya project
Load and run "runFractals.py" in the Maya script editor to test
Select the object you'd like to instance, or select nothing and the script will create a base cube
The group created is the fractal/stack
The individual cube is the source object, which will update all instances when modified
'''

#Lists of directions pointing to corners, edges, and faces of a cube. Some fractals can be generated using a combination of these sets of directions.
CORNERS = [[1,1,1],[-1,1,1],[1,-1,1],[1,1,-1],[1,-1,-1],[-1,1,-1],[-1,-1,1],[-1,-1,-1]]
FACES = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]
EDGES = [[0,1,1],[0,-1,1],[0,1,-1],[0,-1,-1],[1,0,1],[-1,0,1],[1,0,-1],[-1,0,-1],[1,1,0],[-1,1,0],[1,-1,0],[-1,-1,0]]
MENGER = CORNERS + EDGES
MOSLEY = FACES + EDGES

def buildStack(size=1, num=3, maxRotate=0, maxTranslate=0, maxScale=1, suffix='_stack#'):
	'''
	Not a fractal, but another use of instancing to procedurally generate an ordered set of objects
	Customizeable transform jittering to make life-like stack of varied objects
	Most of the heavy lifting is handled by the "stack" function (below)

	maxRotate: maximum randomized rotation amount of individual objects in stack, in degrees
	maxTranslate: maximum randomized x-z translation of individual objects in stack
	maxScale: maximum randomized uniform scale of individual objects in stack

	Groups the final collection of instanced objects
	'''
	baseTrans = collectBaseTransform()
	grpName = baseTrans + suffix
	collection = stack(obj=baseTrans, size=size, num=num, maxRotate=maxRotate, maxTranslate=maxTranslate, maxScale=maxScale)
	cmds.group(collection, n=grpName)

def buildFractal(size=1, scaleFac=0.5, offset=0.5, directions=FACES, depth=2, suffix='_fractal#', allDepths=True):
	'''
	Generic recursive fractal generator based on instancing
	Most of the heavy lifting is handled by the "frac" function (below)

	scaleFac: side-length (1D) scale ratio between recursion depths
	offset: translation of child objects in each given direction
	directions:
	directions: list of 3-element lists, each representing a direction for child objects to spawn. length of this list gives branching factor of fractal
	allDepths: controls whether objects are created on only the deepest (smallest) recursion level or at all levels

	Groups the final collection of instanced objects
	'''
	baseTrans = collectBaseTransform()
	grpName = baseTrans + suffix
	collection = frac(obj=baseTrans, size=size, depth=depth, directions=directions, scaleFac=scaleFac, offset=offset, allDepths=allDepths)
	cmds.group(collection, n=grpName)

def mengerSponge(size=1, depth=2, suffix='_menger#'):
	if depth > 4:
		cmds.error("Please use a depth of 4 or less", n=True)
	buildFractal(size=size, scaleFac=(1.0/3.0), offset=(1.0/3.0), directions=MENGER, depth=depth, suffix=suffix, allDepths=False)

def mosleySnowflake(size=1, depth=2, suffix='_mosley#'):
	if depth > 4:
		cmds.error("Please use a depth of 4 or less", n=True)
	buildFractal(size=size, scaleFac=(1.0/3.0), offset=(1.0/3.0), directions=MOSLEY, depth=depth, suffix=suffix, allDepths=False)



### HELPER FUNCTIONS ###



def deleteCubes():
	cubeList = cmds.ls('myCube*') + cmds.ls('hello*')
	if len(cubeList) > 0:
		cmds.delete(cubeList)

def collectBaseTransform():
	selection = cmds.ls(selection=True)

	if len(selection) < 1:
		return cube(1)

	baseTrans = selection[0]
	baseShape = cmds.listRelatives(baseTrans, shapes=True)[0]
	if cmds.objectType(baseShape) != 'mesh':
		cmds.error(baseShape + " is not a valid mesh", n=True)

	return baseTrans

def frac(obj=None, size=1, pos=[0,0,0], scaleFac=0.5, offset=0.5, directions=CORNERS, depth=2, allDepths=True):
	if (depth == 1):
		return [cube(s=size, p=pos, o=obj)]

	collection = []
	if allDepths:
		collection = [cube(s=size, p=pos, o=obj)]

	for dir in directions:
		collection += frac(obj, size * scaleFac, [pos[i] + size * offset * dir[i] for i in range(3)], scaleFac, offset, directions, depth-1, allDepths=allDepths)
	return collection

def cube(s=1, p=[0,0,0], r=[0,0,0], n='myCube#', o=None):
	'''
	Create new cube, or an instance of an arbitrary object, with particular transforms
	'''
	if o == None:
		c = cmds.polyCube(name=n)
	else:
		c = cmds.instance(o, name = o + '_instance#')
	cmds.scale(s, s, s, c)
	cmds.move(p[0], p[1], p[2], c)
	cmds.rotate(r[0], r[1], r[2], c)
	return c[0]

def stack(obj=None, size=1, num=3, maxRotate=0, maxTranslate=0, maxScale=1):
	collection = []
	nextY = 0
	randSize = 0
	for i in range(num):
		nextY += randSize / 2
		randSize = size * (1 + (maxScale-1) * random.random())
		nextY += randSize / 2

		randX = maxTranslate * random.random()
		randZ = maxTranslate * random.random()
		randRot = maxRotate * random.random()

		newCube = cube(s=randSize, p=[randX, nextY, randZ], r=[0, randRot, 0], o=obj)
		collection.append(newCube)
	return collection
