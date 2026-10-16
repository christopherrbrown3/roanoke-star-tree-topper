"""Private mesh helpers for the continuous-ridge V2 build.

Kept beside the build so regeneration does not need earlier cover experiments.
"""
import hashlib
import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def solid(mesh):
    # Keep offset edges and exact tangent placement in double precision during
    # unions; premature float32 rounding creates microscopic coincident slivers.
    value=mf.Manifold(mf.Mesh64(np.asarray(mesh.vertices,np.float64),np.asarray(mesh.faces,np.uint64)))
    assert value.status()==mf.Error.NoError,value.status()
    return value


def mesh_of(value):
    data=value.to_mesh64()
    result=trimesh.Trimesh(data.vert_properties[:,:3],data.tri_verts,process=True)
    assert result.is_watertight and result.is_winding_consistent and result.volume>0
    assert result.body_count==1 and result.area_faces.min()>1e-10
    return result


def extrusion(shape, z0, z1):
    polygons = [shape] if shape.geom_type == 'Polygon' else list(shape.geoms)
    parts = []
    for polygon in polygons:
        if polygon.area < 1e-8:
            continue
        mesh = trimesh.creation.extrude_polygon(polygon, z1-z0, engine='earcut')
        mesh.apply_translation([0, 0, z0])
        parts.append(solid(mesh))
    return mf.Manifold.batch_boolean(parts, mf.OpType.Add)


def placed(mesh, clip):
    result = mesh.copy()
    c, t, n = (np.asarray(clip[k]) for k in ['center_xy', 'tangent_xy', 'outward_xy'])
    v = result.vertices.copy()
    xy = c[None, :]+v[:, 0, None]*t[None, :]-v[:, 1, None]*n[None, :]
    result.vertices = np.column_stack([xy, v[:, 2]])
    if result.volume < 0:
        result.invert()
    return result


def flat_faces(mesh, z):
    triangles = mesh.triangles[np.all(abs(mesh.triangles[:, :, 2]-z) < 1e-5, axis=1)]
    return unary_union([Polygon(triangle[:, :2]) for triangle in triangles])


def print_mesh(mesh, flip=False, z_origin=0., outside_z=60.):
    mesh = mesh.copy()
    if flip:
        mesh.apply_transform(np.array([[1, 0, 0, 0], [0, -1, 0, 0],
                                       [0, 0, -1, outside_z], [0, 0, 0, 1]], float))
    else:
        mesh.apply_translation([0, 0, -z_origin])
    assert mesh.bounds[0, 2] > -1e-5
    return mesh


def export_mesh(value, destination):
    mesh = mesh_of(value)
    mesh.export(destination)
    return mesh
