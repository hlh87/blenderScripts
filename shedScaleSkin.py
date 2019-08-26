'''
Creates a separate prism object (scale) for every face in an object.
Each scale is displaced away from the original object's origin.
Each scale has the same material as the face it was made from.

The original object is not altered by this script.
Subdivided geometry that is not applied will be ignored.
Scales are not UV-unwrapped, so texture orientation may be incorrect
    on non-outward faces of the scales.
Only quad faces are processed properly; others will throw errors.
Saving your Blender file is highly recommended before using this script,
    as execution times are long for objects with high face counts.

Used with Blender 2.80

Author: Helen Lily Hu
2019
'''
import bpy
import bmesh
import mathutils


originalObjectName= 'Cube'  #replace w/name of your object
SCALE_THICKNESS= 0.05       #alter as you wish
DISPLACEMENT_DISTANCE= 1    #alter as you wish


#select original object and only that object
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
o= bpy.data.objects[originalObjectName]
o.select_set(True)

#create BMesh out of object mesh to modify with edit mode operations
oBM= bmesh.new()
oM= o.data
oBM.from_mesh(oM)
#transform BMesh to global coordinates based on object (in case of scaling issues)
bmesh.ops.transform(oBM, matrix= o.matrix_world, verts= oBM.verts)

oLoc= mathutils.Vector(o.location)
faceNum= 0
#For each face of the object:
for face in oBM.faces:
    #Create a new BMesh for this scale; copy data from face
    sBM= bmesh.new()
    for v in face.verts:
        sBM.verts.new(v.co)
    scale= sBM.faces.new(sBM.verts)

    #Extrude outwards a little so the BMesh has volume/is a prism
    extruded= bmesh.ops.extrude_face_region(sBM, geom= [scale])
    extrusionVerts= [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    vecOtoS= scale.calc_center_median() - oLoc
    vecOtoS.normalize()
    bmesh.ops.translate(sBM, vec= vecOtoS * SCALE_THICKNESS, verts= extrusionVerts)

    #assign face UV coordinates to all of the scale's faces
    uvLayer = sBM.loops.layers.uv.new()
    for loop in face.loops:
        loopIndex= loop.index
        faceUV= oM.uv_layers.active.data[loopIndex].uv
        for sFace in sBM.faces:
            sFace.loops[loopIndex % 4][uvLayer].uv= faceUV

    #Write BMesh into a new scale mesh
    sName= "scale" + originalObjectName + str(faceNum)
    faceNum += 1
    sM= bpy.data.meshes.new(sName)
    sBM.to_mesh(sM)
    sBM.free() #free mesh explicitly to prevent trash pile up

    #Add new scale object that references scale mesh to scene
    sO= bpy.data.objects.new(sName, sM)
    bpy.context.collection.objects.link(sO)

    #Move each scale object away from the original object
    bpy.ops.object.select_all(action='DESELECT')
    sO.select_set(True)
    bpy.ops.object.origin_set(type= 'ORIGIN_GEOMETRY') #center scale origin
    bpy.ops.transform.translate(value= vecOtoS * DISPLACEMENT_DISTANCE)

    #apply face material to scale object
    sO.data.materials.append(bpy.data.materials[face.material_index])

#clean up
oBM.free()
bpy.ops.object.select_all(action='DESELECT')
