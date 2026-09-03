import os, sys
import numpy as np

def d2(p0:list, p1:list, root=False) -> float:
    """
    Calculates square distance between two points. Optionally return the square root of the square distance.
    :param p0: First set of coordinates.
    :param p1: Second set of coordinates.
    :param root: Whether to return the square root of the square distance.
    :return: Square distance (or root square distance).
    """
    if root:
        return np.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2 + (p0[2] - p1[2]) ** 2)
    else:
        return (p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2 + (p0[2] - p1[2]) ** 2

ply_path = sys.argv[1]
num_sites = int(sys.argv[2])
print(f" * Filtering {num_sites} sites in :", ply_path)


target_vertices = []
sorted_vertices = []
with open(ply_path) as ply:
    n = 0
    for line in ply:
        if len(line.split(" ")) == 10:
            x, y, z, b = [float(x) for x in line.split(" ")[:4]]
            sorted_vertices.append((n, x, y, z, b))
            n+=1

sorted_vertices = sorted(sorted_vertices, key=lambda x: x[4], reverse=True)

n = 0
while (len(target_vertices) <= min(num_sites, len(sorted_vertices))) and (n < len(sorted_vertices)):
    vert = sorted_vertices[n]
    p1 = vert[1:4]
    #print(p1)
    is_too_close=False
    for vv in target_vertices:
        p2 = vv[1:4]
        #print(p2)
        if d2(p1, p2) <= 25:
            is_too_close = True
            #print("Too close")
            break
    if not is_too_close:
        target_vertices.append(vert)

    n+=1

vix_path = ply_path.replace(".ply", f".filtered_{num_sites}.vix")
with open(vix_path, "w") as vix:
    for vert in target_vertices:
        vix.write(f"{vert[0]}\n")

print("Filtered vertices save to:", vix_path)