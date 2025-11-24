



bl_info = {
    "name": "Nanomaterials generator",
    "author": "nikita.gordeev@skoltech.ru",
    "version": (0, 3),
    "blender": (5, 0, 0),
    "location": "View3D > UI > Nanomaterials generator",
    "description": "Create a set of Nanomaterials for further use in your papers",
    "category": "Object",
}

import bpy
import bmesh
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import IntProperty,FloatProperty, PointerProperty, FloatVectorProperty


class MaterialProperties(PropertyGroup):
    
    color: FloatVectorProperty(
        name = "color",
        subtype = 'COLOR',
        default = (0.0,0.0,0.1,1.0),
        size = 4,
        min = 0.0,
        max = 1.0
    )

    roughness: FloatProperty(
        name = "Roughness",
        description= "Material rough",
        default = 0.5,
        min = 0.0,
        max = 1.0
    )

    metallic: FloatProperty(
        name = "Metallic",
        description= "Material metal",
        default = 0.5,
        min = 0.0,
        max = 1.0
    )

class MyProperties(PropertyGroup):

    cube_height: FloatProperty(
        name="Film Height",
        description="CNT film height",
        default=0.02,
        min=0.01,
        max=10.0
    )

    cube_width: FloatProperty(
        name="Film Width",
        description="CNT film width",
        default=1.0,
        min=0.01,
        max=10.0
    )

    cube_length: FloatProperty(
        name="Film Length",
        description="CNT film length",
        default=1.0,
        min=0.01,
        max=10.0
    )
    seed: IntProperty(
        name="Seed",
        description="Generation seed",
        default = 1,
        min = 0,
        max = 100
    )
    
    porosity: IntProperty(
        name = "Density",
        description = "Density of the film",
        default = 1,
        min = 1,
        max = 1000
    )
    
    CNT_thickness: FloatProperty(
        name = 'CNT_thickness',
        description = "CNT_thickness",
        default = 0.1,
        min = 0.001,
        max = 10
    )

    CNT_diameter: FloatProperty(
        name = 'CNT diameter',
        description= 'CNT diameter',
        default = 0.2,
        min = 0.01,
        max = 10
    )

    CNT_height: FloatProperty(
        name = 'CNT height',
        description= 'CNT height',
        default = 1,
        min = 0.01,
        max = 10
    )

    Carbon_num: IntProperty(
        name = 'Carbon atoms',
        description= 'Amount of carbon atoms in one ring',
        default = 8,
        min = 4,
        max = 32
    )

    Carbon_sphere: FloatProperty(
        name = 'Carbon spheres size',
        default = 1.6,
        min = 0.1,
        max = 32,        
    )

    Carbon_wires: FloatProperty(
        name = 'Carbon wires size',
        default = 0.75,
        min = 0.1,
        max = 32,        
    )


#-----------------------------------------------------------------
#Graphene params
    graphene_width: FloatProperty(
        name = 'Graphene_sheet_width',
        description= 'Graphene_sheet_width',
        default = 1.0,
        min = 0.01,
        max = 10
    )

    Carbon_num_gr: IntProperty(
        name = 'Carbon atoms',
        description = 'Amount of carbon atoms on edge',
        default = 8,
        min = 4,
        max = 32
    )

    Carbon_sphere_gr: FloatProperty(
        name = 'Carbon spheres size',
        default = 3.0,
        min = 0.1,
        max = 32,        
    )

    Carbon_wires_gr: FloatProperty(
        name = 'Carbon wires size',
        default = 1.0,
        min = 0.1,
        max = 32,        
    )

#-----------------------------------------------------------------





def create_bsdf_material(name,color,roughness,metallic):
    
    mat = bpy.data.materials.new(name = name)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    bsdf = mat.node_tree.nodes.new(type = 'ShaderNodeBsdfPrincipled')
    bsdf.location = (0,0)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    output = mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    output.location = (400,0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'],output.inputs['Surface'])

    return mat    

class OBJECT_OT_my_addon(Operator):
    bl_idname = "object.my_addon"
    bl_label = "Create Film"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        material_tool = scene.material_tool

        film_mat = create_bsdf_material(
            "CNT_Film_Material",
            material_tool.color,
            material_tool.roughness,
            material_tool.metallic,
        )

        # Создаем основу для баунса
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            calc_uvs=True,
            enter_editmode=False,
            align='WORLD',
            location=(0, 0, 0.5*mytool.cube_height)
        )


        cube = context.active_object
        cube.name = "_transparent_cube"
        cube.scale = (mytool.cube_length, mytool.cube_width, mytool.cube_height)
        bpy.context.view_layer.objects.active = cube
        bpy.ops.object.add_bounce_spline(refresh = True, ang_noise =  1.2, bounce_number = 100*mytool.porosity, random_seed = mytool.seed)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        transparent_cube = bpy.data.objects.get("_transparent_cube")
        if transparent_cube:
                # Сохраняем текущий активный объект (bounce spline)
                current_active = context.active_object
            
                # Удаляем куб
                bpy.data.objects.remove(transparent_cube, do_unlink=True)
            
             # Восстанавливаем активность bounce spline
                if current_active and current_active.name != "_transparent_cube":
                    context.view_layer.objects.active = current_active
                    current_active.select_set(True)
       



        bounce_spline = bpy.data.objects.get("BounceSpline") 

        
        bounce_spline.data.bevel_depth = mytool.CNT_thickness/100
        bounce_spline.data.bevel_resolution = 4
        bounce_spline.data.resolution_u = 16

            
     
        bpy.context.view_layer.objects.active = bounce_spline
        bounce_spline.select_set(True)
        bpy.ops.object.convert(target='MESH')
        
        if bounce_spline.data.materials:
            bounce_spline.data.materials[0] = film_mat

        else:
            bounce_spline.data.materials.append(film_mat)
        
       
        

        return {'FINISHED'}
    
class OBJECT_OT_create_cnt(Operator):
    bl_idname = "object.create_cnt"
    bl_label = "Create CNT"
    bl_options = {'REGISTER', 'UNDO'}

    

    def create_geometry_nodes_setup(self,obj,material_tool):
    
        
        node_group = bpy.data.node_groups.new('CNT_Geometry_Nodes','GeometryNodeTree')

        input_geometry = node_group.interface.new_socket(
                name="Geometry",
                in_out='INPUT',
                socket_type='NodeSocketGeometry'
            )
        output_geometry = node_group.interface.new_socket(
            name="Geometry",
            in_out='OUTPUT',
            socket_type='NodeSocketGeometry'
        )


        group_input = node_group.nodes.new('NodeGroupInput')
        group_input.location = (-800, 0)
        
        group_output = node_group.nodes.new('NodeGroupOutput') 
        group_output.location = (1200, 0)

        triangulate_node = node_group.nodes.new('GeometryNodeTriangulate')
        triangulate_node.location = (-400,0)
        triangulate_node.inputs['Quad Method'].default_value = 'Fixed'  # Changed
        triangulate_node.inputs['N-gon Method'].default_value = 'Beauty'
        

        dual_mesh_node = node_group.nodes.new('GeometryNodeDualMesh')
        dual_mesh_node.location = (-200,0)

        mesh_to_curve_node = node_group.nodes.new('GeometryNodeMeshToCurve')
        mesh_to_curve_node.location = (0,200)

        curve_circle_node = node_group.nodes.new('GeometryNodeCurvePrimitiveCircle')
        curve_circle_node.location = (0, 400)
        curve_circle_node.inputs['Radius'].default_value = b/100
        curve_circle_node.inputs['Resolution'].default_value = 8
        curve_circle_node.mode = 'RADIUS'

        curve_to_mesh_node = node_group.nodes.new('GeometryNodeCurveToMesh')
        curve_to_mesh_node.location = (200,200)

        set_material_1_node = node_group.nodes.new('GeometryNodeSetMaterial')
        set_material_1_node.location = (400,200)

        instances_on_points_node = node_group.nodes.new('GeometryNodeInstanceOnPoints')
        instances_on_points_node.location = (0, -200)

        uv_sphere_node = node_group.nodes.new('GeometryNodeMeshUVSphere')
        uv_sphere_node.location = (0, -400)
        uv_sphere_node.inputs['Segments'].default_value = 16
        uv_sphere_node.inputs['Rings'].default_value = 8
        uv_sphere_node.inputs['Radius'].default_value = a/100

        set_material_2_node = node_group.nodes.new('GeometryNodeSetMaterial')
        set_material_2_node.location = (200,-200)

        join_geometry_node = node_group.nodes.new('GeometryNodeJoinGeometry')
        join_geometry_node.location = (800,0)

        wire_mat = create_bsdf_material(
            'CNT_wire_Material',
            material_tool.color,
            material_tool.roughness,
            material_tool.metallic
        )
        
        sphere_mat = create_bsdf_material(
            'CNT_Sphere_Material',
            material_tool.color,
            material_tool.roughness,
            material_tool.metallic
        )

        # Set material inputs
        set_material_1_node.inputs['Material'].default_value = wire_mat
        set_material_2_node.inputs['Material'].default_value = sphere_mat




        #node_group.input.new('NodeSocketMaterial', 'Material_1')
        #node_group.input['Material_1'].default_value = material_1
        
        #node_group.input.new('NodeSocketMaterial', 'Material_2')
        #node_group.input['Material_2'].default_value = material_2





        links = node_group.links

        links.new(group_input.outputs[0], triangulate_node.inputs[0])
        links.new(triangulate_node.outputs['Mesh'], dual_mesh_node.inputs['Mesh'])

        links.new(dual_mesh_node.outputs['Dual Mesh'], mesh_to_curve_node.inputs['Mesh'])
        links.new(mesh_to_curve_node.outputs[0], curve_to_mesh_node.inputs[0])
        links.new(curve_circle_node.outputs['Curve'], curve_to_mesh_node.inputs[1])
        links.new(curve_to_mesh_node.outputs[0], set_material_1_node.inputs['Geometry'])
        links.new(set_material_1_node.outputs['Geometry'], join_geometry_node.inputs['Geometry'])
        
       
        #links.new(group_input.outputs['Material_1'], set_material_1_node.inputs['Material'])
        
    
        links.new(dual_mesh_node.outputs['Dual Mesh'], instances_on_points_node.inputs['Points'])
        links.new(uv_sphere_node.outputs['Mesh'], instances_on_points_node.inputs['Instance'])
        links.new(instances_on_points_node.outputs['Instances'], set_material_2_node.inputs['Geometry'])
        links.new(set_material_2_node.outputs['Geometry'], join_geometry_node.inputs[0])
        
   
        #links.new(group_input.outputs['Material_2'], set_material_2_node.inputs['Material'])
        

        links.new(join_geometry_node.outputs[0], group_output.inputs[0])





        return node_group


    
    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        material_tool = scene.material_tool

        global a, b
        a = mytool.Carbon_sphere
        b = mytool.Carbon_wires
        h = mytool.CNT_height
        r = mytool.CNT_diameter/2

        
    
        k = -50.8
        correction = -5.2 * h + 18.3 * r
    
        base_angle = k * (h / r) + correction

         

        base_angle = base_angle/360*3.1415
    
        deform_angle = base_angle

        circumference = 2 * 3.1415 * mytool.CNT_diameter/2
        segment_width = circumference /(mytool.Carbon_num - 1)
        segment_height_num = int(round(mytool.CNT_height/segment_width) - 1)
        bpy.ops.mesh.primitive_circle_add(vertices=mytool.Carbon_num, radius = mytool.CNT_diameter/2, fill_type = 'NOTHING')
        #bpy.ops.mesh.primitive_cylinder_add(vertices=mytool.Carbon_num, radius = mytool.CNT_diameter/2, depth = mytool.CNT_height, end_fill_type = 'NOTHING')
        bpy.ops.object.mode_set(mode='EDIT')
        for i in range(segment_height_num):
            bpy.ops.mesh.extrude_edges_move()
            bpy.ops.transform.translate(value = (0,0,segment_width))    
        


        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        cnt_obj = bpy.context.active_object
        deform_modifier = cnt_obj.modifiers.new(name='SimpleDeform', type = 'SIMPLE_DEFORM')
        deform_modifier.deform_method = 'TWIST'
        deform_modifier.deform_axis = 'Z'
        deform_modifier.angle = deform_angle
        
        geo_modifier = cnt_obj.modifiers.new(name = "CNT_Geometry", type = 'NODES')
        node_group = self.create_geometry_nodes_setup(cnt_obj,material_tool)
        geo_modifier.node_group = node_group
        
        bpy.ops.object.shade_auto_smooth()
        
        bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 0.937212
        bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 0.92
        bpy.context.object.modifiers["Smooth by Angle"]["Socket_1"] = True
        bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 0.937212
        bpy.context.object.modifiers["Smooth by Angle"]["Socket_1"] = True

        self.refresh = True
        
        return {'FINISHED'}

class OBJECT_OT_create_graphene(Operator):
    bl_idname = "object.create_graphene"
    bl_label = "Create graphene"
    bl_options = {'REGISTER', 'UNDO'}

    

    def create_geometry_nodes_setup1(self,obj,material_tool):
    
        
        node_group = bpy.data.node_groups.new('Graphene_Geometry_Nodes','GeometryNodeTree')

        input_geometry = node_group.interface.new_socket(
                name="Geometry",
                in_out='INPUT',
                socket_type='NodeSocketGeometry'
            )
        output_geometry = node_group.interface.new_socket(
            name="Geometry",
            in_out='OUTPUT',
            socket_type='NodeSocketGeometry'
        )


        group_input = node_group.nodes.new('NodeGroupInput')
        group_input.location = (-800, 0)
        
        group_output = node_group.nodes.new('NodeGroupOutput') 
        group_output.location = (1200, 0)

        triangulate_node = node_group.nodes.new('GeometryNodeTriangulate')
        triangulate_node.location = (-400,0)
        triangulate_node.inputs['Quad Method'].default_value = 'Fixed'  # Changed
        triangulate_node.inputs['N-gon Method'].default_value = 'Beauty'

        dual_mesh_node = node_group.nodes.new('GeometryNodeDualMesh')
        dual_mesh_node.location = (-200,0)

        mesh_to_curve_node = node_group.nodes.new('GeometryNodeMeshToCurve')
        mesh_to_curve_node.location = (0,200)

        curve_circle_node = node_group.nodes.new('GeometryNodeCurvePrimitiveCircle')
        curve_circle_node.location = (0, 400)
        curve_circle_node.inputs['Radius'].default_value = b/100
        curve_circle_node.inputs['Resolution'].default_value = 8
        curve_circle_node.mode = 'RADIUS'

        curve_to_mesh_node = node_group.nodes.new('GeometryNodeCurveToMesh')
        curve_to_mesh_node.location = (200,200)

        set_material_1_node = node_group.nodes.new('GeometryNodeSetMaterial')
        set_material_1_node.location = (400,200)

        instances_on_points_node = node_group.nodes.new('GeometryNodeInstanceOnPoints')
        instances_on_points_node.location = (0, -200)

        uv_sphere_node = node_group.nodes.new('GeometryNodeMeshUVSphere')
        uv_sphere_node.location = (0, -400)
        uv_sphere_node.inputs['Segments'].default_value = 16
        uv_sphere_node.inputs['Rings'].default_value = 8
        uv_sphere_node.inputs['Radius'].default_value = a/100

        set_material_2_node = node_group.nodes.new('GeometryNodeSetMaterial')
        set_material_2_node.location = (200,-200)

        join_geometry_node = node_group.nodes.new('GeometryNodeJoinGeometry')
        join_geometry_node.location = (800,0)

        wire_mat = create_bsdf_material(
            'CNT_wire_Material',
            material_tool.color,
            material_tool.roughness,
            material_tool.metallic
        )
        
        sphere_mat = create_bsdf_material(
            'CNT_Sphere_Material',
            material_tool.color,
            material_tool.roughness,
            material_tool.metallic
        )

        # Set material inputs
        set_material_1_node.inputs['Material'].default_value = wire_mat
        set_material_2_node.inputs['Material'].default_value = sphere_mat




        #node_group.input.new('NodeSocketMaterial', 'Material_1')
        #node_group.input['Material_1'].default_value = material_1
        
        #node_group.input.new('NodeSocketMaterial', 'Material_2')
        #node_group.input['Material_2'].default_value = material_2





        links = node_group.links

        links.new(group_input.outputs[0], triangulate_node.inputs[0])
        links.new(triangulate_node.outputs['Mesh'], dual_mesh_node.inputs['Mesh'])

        links.new(dual_mesh_node.outputs['Dual Mesh'], mesh_to_curve_node.inputs['Mesh'])
        links.new(mesh_to_curve_node.outputs[0], curve_to_mesh_node.inputs[0])
        links.new(curve_circle_node.outputs['Curve'], curve_to_mesh_node.inputs[1])
        links.new(curve_to_mesh_node.outputs[0], set_material_1_node.inputs['Geometry'])
        links.new(set_material_1_node.outputs['Geometry'], join_geometry_node.inputs['Geometry'])
        
       
        #links.new(group_input.outputs['Material_1'], set_material_1_node.inputs['Material'])
        
    
        links.new(dual_mesh_node.outputs['Dual Mesh'], instances_on_points_node.inputs['Points'])
        links.new(uv_sphere_node.outputs['Mesh'], instances_on_points_node.inputs['Instance'])
        links.new(instances_on_points_node.outputs['Instances'], set_material_2_node.inputs['Geometry'])
        links.new(set_material_2_node.outputs['Geometry'], join_geometry_node.inputs[0])
        
   
        #links.new(group_input.outputs['Material_2'], set_material_2_node.inputs['Material'])
        

        links.new(join_geometry_node.outputs[0], group_output.inputs[0])





        return node_group


    
    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        material_tool = scene.material_tool

        global a, b
        a = mytool.Carbon_sphere_gr
        b = mytool.Carbon_wires_gr
#Carbon_wires_gr: FloatProperty(
#Carbon_num_gr: IntProperty(
#Graphene_width: FloatProperty(
#Carbon_sphere_gr: FloatProperty(

        bpy.ops.mesh.primitive_plane_add(size = mytool.graphene_width,location= (0,0,0),rotation = (0,0,45*2*3.1415/360))
        plane = bpy.context.view_layer.objects.active 
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        plane.scale = (1.73205, 1, 1)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts = mytool.Carbon_num_gr -2)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        graphene = bpy.context.active_object
        
        geo_modifier = graphene.modifiers.new(name = "CNT_Geometry", type = 'NODES')
        node_group = self.create_geometry_nodes_setup1(graphene,material_tool)
        geo_modifier.node_group = node_group
        
        bpy.ops.object.shade_auto_smooth()
        
        bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 0.937212
        bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 0.92
        bpy.context.object.modifiers["Smooth by Angle"]["Socket_1"] = True
        bpy.context.object.modifiers["Smooth by Angle"]["Input_1"] = 0.937212
        bpy.context.object.modifiers["Smooth by Angle"]["Socket_1"] = True

        self.refresh = True
        
        return {'FINISHED'}



class VIEW3D_PT_my_panel(Panel):
    bl_label = "Carbon Generator"
    bl_idname = "VIEW3D_PT_my_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Carbon Generator"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        material_tool = scene.material_tool

        box = layout.box()
        box.label(text="Material Settings")
        box.prop(material_tool, "color")
        box.prop(material_tool, "roughness")
        box.prop(material_tool, "metallic")


        box = layout.box()
        box.label(text="CNT film")
        box.prop(mytool, "cube_height")
        box.prop(mytool, "cube_length")
        box.prop(mytool, "cube_width")
        box.prop(mytool, "porosity")
        box.prop(mytool, "seed")
        box.prop(mytool, "CNT_thickness")

        self.refresh = True
        layout.operator("object.my_addon")

        box = layout.box()
        box.label(text="Single carbon nanotube")
        box.prop(mytool, "CNT_diameter")
        box.prop(mytool, "CNT_height")
        box.prop(mytool, "Carbon_num")
        box.prop(mytool, "Carbon_sphere")
        box.prop(mytool, "Carbon_wires")
        layout.operator("object.create_cnt")

        box = layout.box()
        box.label(text="Graphene flake")
        box.prop(mytool, "graphene_width")
        box.prop(mytool, "Carbon_num_gr")
        box.prop(mytool, "Carbon_sphere_gr")
        box.prop(mytool, "Carbon_wires_gr")
        layout.operator("object.create_graphene")


classes = (
    MaterialProperties,
    MyProperties,
    OBJECT_OT_my_addon,
    OBJECT_OT_create_cnt,
    OBJECT_OT_create_graphene,
    VIEW3D_PT_my_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    bpy.types.Scene.material_tool = PointerProperty(type=MaterialProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.material_tool
if __name__ == "__main__":
    register()