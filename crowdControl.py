'''
Contains procedures that manipulate similarly named objects en masse.

A precondition for all procedures in this module is that Blender must be
in object mode.

Used with Blender 2.80

Author: Helen Lily Hu
2019
'''
import bpy
import mathutils


def _getObjList(nameRoot):
    '''
    Return a list of all objects whose names begin with nameRoot.
    Helper for procedures in this module.

    Parameter nameRoot: nameRoot is a string
    '''
    objects= bpy.data.objects
    return [o for o in objects if o.name.startswith(nameRoot)]


def select(nameRoot):
    '''
    Select all objects whose names begin with nameRoot.

    Parameter nameRoot: nameRoot is a string
    '''
    all= _getObjList(nameRoot)
    for o in all:
        o.select_set(True)


def deselect(nameRoot):
    '''
    Deselect all objects whose names begin with nameRoot.

    Parameter nameRoot: nameRoot is a string
    '''
    all= _getObjList(nameRoot)
    for o in all:
        o.select_set(False)


def move(nameRoot, vector):
    '''
    Move all objects whose names begin with nameRoot by vector.

    Parameter nameRoot: nameRoot is a string
    Parameter vector: vector is a tuple or list of length 3
    '''
    bpy.ops.object.select_all(action='DESELECT') #prevent unintentionally moving something
    select(nameRoot)
    bpy.ops.transform.translate(value= vector)


def move_towards(nameRoot, target, value):
    '''
    Move all objects whose names begin with nameRoot value units towards target.

    Use a negative value to move objects away from target.

    Parameter nameRoot: nameRoot is a string
    Parameter target: target is a tuple or list of length 3
    Parameter value: value is a number
    '''
    bpy.ops.object.select_all(action='DESELECT') #prevent unintentionally moving something
    targetV= mathutils.Vector(target)
    all= _getObjList(nameRoot)
    for o in all:
        o.select_set(True)
        vector= targetV - mathutils.Vector(o.location)
        vector.normalize()
        bpy.ops.transform.translate(value= vector * value)
        o.select_set(False)


def enable_rigidbody(nameRoot, type= 'ACTIVE'):
    '''
    Enable rigidbody physics for all objects whose names begin with nameRoot.

    Parameter nameRoot: nameRoot is a string
    Parameter type: 'ACTIVE' or 'PASSIVE'
    '''
    c= bpy.context.view_layer.objects
    all= _getObjList(nameRoot)
    for o in all:
        c.active= o
        bpy.ops.rigidbody.object_add(type= type)
    c.active= None


def disable_rigidbody(nameRoot):
    '''
    Disable rigidbody physics for all objects whose names begin with nameRoot.

    Parameter nameRoot: nameRoot is a string
    Precondition: All objects whose names begin with nameRoot have rigidbody
    physics enabled.
    '''
    c= bpy.context.view_layer.objects
    all= _getObjList(nameRoot)
    for o in all:
        c.active= o
        bpy.ops.rigidbody.object_remove()
    c.active= None


def bake_rigidbody(nameRoot, startFrame= 1, endFrame= 250, step= 1):
    '''
    Bake rigidbody physics for all objects whose names begin with nameRoot
    from frameStart to frameEnd with step.

    Parameter nameRoot: nameRoot is a string
    Parameter startFrame: startFrame is an integer in 0..300000
    Parameter endFrame: endFrame is an integer in 1..300000
    Parameter step: step is an integer in 1..120
    '''
    bpy.ops.object.select_all(action='DESELECT') #prevent unintentionally baking something
    select(nameRoot)
    bpy.ops.rigidbody.bake_to_keyframes(frame_start= startFrame,
        frame_end= endFrame, step= step)


def copy_rigidbody_settings(nameRoot, template):
    '''
    Copy rigidbody settings from object named template and applies those
    settings to all objects whose names begin with nameRoot

    Parameter nameRoot: nameRoot is a string
    Parameter template: template is a string
    Precondition: There exists a rigid body object named template in the scene
    '''
    bpy.ops.object.select_all(action='DESELECT') #prevent unintentional application
    bpy.context.view_layer.objects.active= bpy.data.objects[template]
    select(nameRoot)
    bpy.ops.rigidbody.object_settings_copy()


def assign_material(nameRoot, material):
    '''
    Assign material to all objects whose names begin with nameRoot.

    Deletes all other material slots.

    Parameter nameRoot: nameRoot is a string
    Parameter material: material is a string
    Precondition: There exists a material named material
    '''
    m= bpy.data.materials.get(material)
    cv= bpy.context.view_layer.objects
    co= bpy.context.object
    all= _getObjList(nameRoot)
    for o in all:
        #delete all material slots
        cv.active= o
        totalSlots= len(co.material_slots)
        while totalSlots != 0:
            co.active_material_index= 0
            bpy.ops.object.material_slot_remove()
            totalSlots -= 1
        #assign material
        o.data.materials.append(m)
    cv.active= None
