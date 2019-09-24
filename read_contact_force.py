from abaqus import *
from abaqusConstants import *
import __main__
import math
import json
import visualization
import sys


# Variable parameters. These must be changed acoordingly.

STEP = 'Step-1'
FIELD_TYPE = 'CNORMF'
NODESET = 'CONTACT'
PART = 'BODY-1'


# Establish file placement
FILE = session.odbData.keys()[0]


# Open ODB
ODB = session.openOdb(FILE)

# Establish coordinate system for output field
scratchOdb = session.ScratchOdb(ODB)
scratchOdb.rootAssembly.DatumCsysByThreePoints(name='CSYS-2', 
    coordSysType=CYLINDRICAL, origin=(0.0, 0.0, 0.0), point1=(1.0, 0.0, 0.0), 
    point2=(0.0, 1.0, 0.0))

dtm = session.scratchOdbs[FILE].rootAssembly.datumCsyses['CSYS-2']



# Move to correct frame and step

FRAME = ODB.steps[STEP].frames[-1]

# Find all nodes in established nodeset
NODE_LIST = ODB.rootAssembly.nodeSets[NODESET].nodes[0]

# Save all nodes in given part
NODE_PART_LIST = ODB.rootAssembly.instances[PART].nodes

# Save field, transformed by coordinate system
FIELD = FRAME.fieldOutputs[FIELD_TYPE].getTransformedField(dtm).values

# Empty list for value storage
NODE_OUTPUT_LIST = []

# Go through all nodes
for global_node in FIELD:

    # If the node is inside the correct part
    if global_node.instance.name == PART:
        for node in NODE_LIST:

            # If the node in the part is in the correct set
            if node.label == global_node.nodeLabel:

                # Save coordinates
                coordinates = node.coordinates

                # Append coordinates and field value. data[0] is CNORMF1, data[1] is CNORMF2...
                NODE_OUTPUT_LIST.append(
                    {
                        'label': node.label,
                        'x': str(coordinates[0]),
                        'y': str(coordinates[1]),
                        'z': str(coordinates[2]),
                        'field': str(global_node.data[0])
                    }
                )

# Dump to JSON
with open('field_export', 'w') as outfile:
    json.dump(NODE_OUTPUT_LIST, outfile)
