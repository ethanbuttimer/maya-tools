import sys
import os
from maya import cmds
sys.path.append(os.path.join(cmds.workspace(q=True, rd=True), 'scripts'))
import fractals as f
reload(f)

f.mosleySnowflake(size=2, depth=3)
cmds.select(clear=True)

f.mengerSponge(depth=3)
cmds.select(clear=True)

f.buildStack(num=10, maxRotate=12, maxTranslate=0.1, maxScale=1.4)
cmds.select(clear=True)

f.buildFractal(depth=3)
