import bpy
from bpy.props import BoolProperty, PointerProperty, FloatProperty
from . window_operations import splitV3DtoBLS
import os

class Blender_Light_Studio_Properties(bpy.types.PropertyGroup):
    initialized = BoolProperty(default = False)
    
    def get_light_x(self):
        obs = bpy.context.scene.objects
        lightGrp = obs.active
        light_no = lightGrp.name.split('.')[1]
        lightMesh = obs[obs.find('BLS_LIGHT_MESH.'+light_no)]
        #lightMesh = [ob for ob in bpy.context.scene.objects if ob.name.startswith('BLS_LIGHT_MESH') and ob.name.endswith(light_no)][0]
        return lightMesh.location.x
    
    def set_light_x(self, context):
        obs = bpy.context.scene.objects
        lightGrp = obs.active
        light_no = lightGrp.name.split('.')[1]
        lightMesh = obs[obs.find('BLS_LIGHT_MESH.'+light_no)]
        lightMesh.location.x = context
    
    light_radius = FloatProperty(name="Light Distance", default=30.0, min=0.5, set=set_light_x, step=5, get=get_light_x)
    

class CreateBlenderLightStudio(bpy.types.Operator):
    bl_idname = "scene.create_blender_light_studio"
    bl_label = "Create Light Studio"
    bl_description = "Append Blender Light Studio to current scene"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT' and not context.scene.BLStudio.initialized
        #return not [ob for ob in bpy.context.scene.objects if ob.name.startswith('BLENDER_LIGHT_STUDIO')]
    
    def execute(self, context):
        script_file = os.path.realpath(__file__)
        dir = os.path.dirname(script_file)
        
        bpy.ops.wm.append(filepath='//BLS_V1_02_simple.blend\\Object\\',
        #directory="D:/Downloads/BlightStudio/BLS_V1_02_simple.blend\\Object\\",
        directory=dir+"\\BLS_V1_02_simple.blend\\Object\\",
        filename="BLENDER_LIGHT_STUDIO",
        active_layer=False)

        bpy.ops.wm.append(filepath='//BLS_V1_02_simple.blend\\Object\\',
        directory=dir+"\\BLS_V1_02_simple.blend\\Object\\",
        filename="BLS_PANEL",
        active_layer=False)
        
        cpanel = [ob for ob in bpy.context.scene.objects if ob.name.startswith('BLS_PANEL')][0]
        cpanel.parent = [ob for ob in bpy.context.scene.objects if ob.name.startswith('BLENDER_LIGHT_STUDIO')][0]

        context.scene.BLStudio.initialized = True
        
        return {"FINISHED"}
    
class DeleteBlenderLightStudio(bpy.types.Operator):
    bl_idname = "scene.delete_blender_light_studio"
    bl_label = "Delete Studio"
    bl_description = "Delete Blender Light Studio from current scene"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT' and context.scene.BLStudio.initialized
    
    def execute(self, context):
        scene = context.scene
        scene.BLStudio.initialized = False
        obsToRemove = [ob for ob in scene.objects if ob.name.startswith('BLS_') or ob.name.startswith('BLENDER_LIGHT_STUDIO')]
        for ob in obsToRemove:
            scene.objects.unlink(ob)
            for gr in ob.users_group:
                gr.objects.unlink(ob)
            ob.user_clear()
            bpy.data.objects.remove(ob)
        
        return {"FINISHED"}
     
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Deleting Studio is irreversible!")
        col.label(text="Your lighting setup will be lost.")

class AddBSLight(bpy.types.Operator):
    bl_idname = "scene.add_blender_studio_light"
    bl_label = "Add Studio Light"
    bl_description = "Add Light to Studio"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT' and context.scene.BLStudio.initialized
    
    def execute(self, context):
        script_file = os.path.realpath(__file__)
        dir = os.path.dirname(script_file)
        
        scene = context.scene
        bls = [ob for ob in bpy.context.scene.objects if ob.name.startswith('BLENDER_LIGHT_STUDIO')][0]
    
        # before
        #A = set(bpy.data.objects[:])
        A = set(bpy.data.groups[:])
        
        bpy.ops.wm.append(filepath='//BLS_V1_02_simple.blend\\Group\\',
        directory=dir+"\\BLS_V1_02_simple.blend\\Group\\",
        filename="BLS_Light",
        active_layer=False)
        
        
        # after operation
        #B = set(bpy.data.objects[:])
        B = set(bpy.data.groups[:])

        # whats the difference
        new_objects = (A ^ B).pop().objects
        
        lightGrp = [l for l in new_objects if l.name.startswith('BLS_LIGHT_GRP')][0]
        lightGrp.parent = [ob for ob in bpy.context.scene.objects if ob.name.startswith('BLENDER_LIGHT_STUDIO')][0]
        
        textId = [l for l in new_objects if l.name.startswith('BLS_ID')][0]
        #textId.data.body = str(len(bls.children)-1)
        
        bpy.ops.object.select_all(action='DESELECT')
        panel = [p for p in new_objects if p.name.startswith('BLS_CONTROLLER')][0]
        panel.select = True
        textId.data.body = str(int(panel.name.split('.')[1])+1)
        context.scene.objects.active = panel
                
        return {"FINISHED"}
    
class DeleteBSLight(bpy.types.Operator):
    bl_idname = "scene.delete_blender_studio_light"
    bl_label = "Delete Studio Light"
    bl_description = "Delete selected Light from Studio"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        #light = context.active_object
        light = context.scene.objects.active
        return context.area.type == 'VIEW_3D' and \
               context.mode == 'OBJECT' and \
               context.scene.BLStudio.initialized and \
               light and \
               light.name.startswith('BLS_CONTROLLER')

    def execute(self, context):
        scene = bpy.context.scene
        oldlaysArea = context.area.spaces[0].layers[:]
        oldlaysScene = context.scene.layers[:]
        context.area.spaces[0].layers = [True] + [False]*18 + [True]
        context.scene.layers = [True] + [False]*18 + [True]
        
        light = bpy.context.active_object
        
        lightGrp = light.parent
        ending = lightGrp.name.split('.')[1]
        obsToRemove = [ob for ob in scene.objects if ob.name.startswith('BLS_') and ob.name.endswith(ending)]
        
        for ob in obsToRemove:
            scene.objects.unlink(ob)
            for gr in ob.users_group:
                gr.objects.unlink(ob)
            ob.user_clear()
            bpy.data.objects.remove(ob)
        
        context.area.spaces[0].layers = oldlaysArea
        context.scene.layers = oldlaysScene
                
        return {"FINISHED"}
    
class PrepareBSLV3D(bpy.types.Operator):
    bl_idname = "scene.prepare_blender_studio_light"
    bl_label = "Prepare Studio Light"
    bl_description = "Split current Viewport for easier Studio usage."
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT' and context.scene.BLStudio.initialized
    
    def execute(self, context):
        splitV3DtoBLS(context)
        context.scene.render.engine="CYCLES"
        return {"FINISHED"}

class BlenderLightStudioPanel(bpy.types.Panel):
    bl_idname = "blender_light_studio_panel"
    bl_label = "Blender Light Studio"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Light Studio"
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'    
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Create/Delete:")
        if not context.scene.BLStudio.initialized: col.operator('scene.create_blender_light_studio')
        if context.scene.BLStudio.initialized: col.operator('scene.delete_blender_light_studio')

        col = layout.column(align=True)
        col.label(text="Lights:")
        row = col.row(align=True)
        row.operator('scene.add_blender_studio_light', text='Add Light')
        row.operator('scene.delete_blender_studio_light', text='Delete Light')
        
        ol = layout.column(align=True)
        col.label(text="Studio:")
        row = col.row(align=True)
        row.operator('scene.prepare_blender_studio_light')

class BlenderLightStudioPanelProps(bpy.types.Panel):
    bl_idname = "blender_light_studio_panel_props"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "BLS Properties"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT' and context.scene.objects.active and context.scene.objects.active.name.startswith('BLS_CONTROLLER')
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Light:")
        row = col.row(align=True)
        row.prop(context.scene.BLStudio, 'light_radius')
        #row.prop(context.scene.objects.active, "scale")
        