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
script.raw(f"cd {os.path.abspath(os.getcwd())}",  is_fun=False)
script.raw(f"cd {script.subfolder}",  is_fun=False)

script.load(pdb_path)
script.raw(f"loadply {relative_path(ply_path, script.subfolder)}",  is_fun=False)

for site in sites:
    site_path = os.path.join(target_folder, site)
    script.load(pdb_path)
    for match in os.listdir(site_path):
        match_path=os.path.join(site_path, match)
        if not os.path.isdir(match_path):
            continue
        for file in os.listdir(match_path):
            if file.endswith(".pdb"):
                name = f"{site}_{file.split('.')[0]}"
                path = os.path.join(match_path, file)
            elif file.endswith(".npy"):
                matrix = f"matrix_{name}"
                script.raw(f"{matrix} = np.load('{relative_path(os.path.join(match_path, file), script.subfolder)}').flatten()", is_fun=False)

        script.load(path, name)
        #script.raw(f"cmd.transform_object('{name}', {matrix})", is_fun=False)
    script.group(site)

script.execute(extra_options=None, quiet=False)









