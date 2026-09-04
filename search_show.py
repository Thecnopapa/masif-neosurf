import sys, os, bioiain

from bioiain.visualisation.pymol import PymolScript
from bioiain.utilities import relative_path
import numpy as np

results_folder=os.environ["EXAMPLE_RESULTS_FOLDER"]

target_name = sys.argv[1]
print("Target name:", target_name)
target_folder=os.path.join(results_folder, target_name)
print("Target fodler:", target_folder)

sites = []
for site in os.listdir(target_folder):
    site_path = os.path.join(target_folder, site)
    if os.path.isdir(site_path):
        sites.append(site)

sites = sorted(sites)
print("Sites:", sites)

script_name=f"search_{target_name}"
script = PymolScript(script_name, pymol_path="/usr/bin/pymol")
script.raw(f"import numpy as np",  is_fun=False)
print(script)

pdb_path = os.path.join(target_folder, target_name+".pdb")
ply_path = os.path.join(target_folder, target_name+".ply")
selected_sites_path = os.path.join(target_folder, f"selected_sites.vert")
script.raw(f"cd {os.path.abspath(os.getcwd())}",  is_fun=False)
script.raw(f"cd {script.subfolder}",  is_fun=False)

script.load(pdb_path)
script.raw(f"loadply {relative_path(ply_path, script.subfolder)}",  is_fun=False)
for site in sites:
    site_path = os.path.join(target_folder, site)
    n_in_site=0
    for match in os.listdir(site_path):
        match_path=os.path.join(site_path, match)
        if not os.path.isdir(match_path):
            continue
        name = f"{site}_{match}"
        for file in os.listdir(match_path):
            if file.endswith(".pdb"):
                path = os.path.join(match_path, file)
            elif file.endswith(".npy"):
                matrix = f"matrix_{name}"
                script.raw(f"{matrix} = np.load('{relative_path(os.path.join(match_path, file), script.subfolder)}').flatten()", is_fun=False)

        script.load(path, name)
        n_in_site += 1
        #script.raw(f"cmd.transform_object('{name}', {matrix})", is_fun=False)
    if n_in_site > 0:
        script.group(site)
script.disable("vert*")
script.disable("pb*")
script.disable("hbond*")
script.disable("mesh*")
script.disable("hphobic*")
with open(selected_sites_path) as f:
    for n, line in enumerate(f):
        #print(n)
        coord_str = [c.strip() for c in line.split(",")]
        coord = [float(x) for x in coord_str]
        b=0
        with open(ply_path) as ply:
            for vert in ply:
                #print(vert)
                #print([float(c) % 1 for c in coord_str])
                cc =" ".join([c if (float(c) % 1 != 0) else str(int(float(c))) for c in coord_str])
                #print(cc)
                if vert.startswith(cc):
                    data = vert.split(" ")
                    #print(data)
                    b = data[3]
                    #print(b)
                    break
        script.pseudoatom(f"sites{n}", coord=coord, elem="'ca'", b=b)




script.group("sites", "sites")
script.show("sites", "spheres")
script.spectrum("sites", minimum=0, maximum=1)

script.execute(extra_options=None, quiet=False)









