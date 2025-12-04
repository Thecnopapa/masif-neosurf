"""
protonate.py: Wrapper method for the reduce program: protonate (i.e., add hydrogens) a pdb using reduce
                and save to an output file.
Pablo Gainza - LPDI STI EPFL 2019
Released under an Apache License 2.0
"""

from subprocess import Popen, PIPE
from IPython.core.debugger import set_trace
import os
import prody
from rdkit import Chem
from io import StringIO

from triangulation.ligand_utils import assign_bond_orders_to_pdb_ligand


def protonate(in_pdb_file, out_pdb_file, het_dict=os.environ.get('REDUCE_HET_DICT')):
    # protonate (i.e., add hydrogens) a pdb using reduce and save to an output file.
    # in_pdb_file: file to protonate.
    # out_pdb_file: output file where to save the protonated pdb file.

    # Remove protons first, in case the structure is already protonated
    args = ["reduce", "-Trim", in_pdb_file]
    p2 = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p2.communicate()
    outfile = open(out_pdb_file, "w")
    outfile.write(stdout.decode('utf-8').rstrip())
    outfile.close()

    # Now add them again.
    args = ["reduce", out_pdb_file, "-HIS"]
    if het_dict is not None:
        args.extend(["-DB", het_dict])
        args.extend([ "-NONMETALBump0.110"])  # default NONMETALBump=0.125 leads to issues for some ligands

    p2 = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p2.communicate()

    if p2.returncode != 0:
        print("### REDUCE ###\n", stderr.decode('utf-8'))
        raise RuntimeError("REDUCE exited with an error")

    outfile = open(out_pdb_file, "w")
    outfile.write(stdout.decode('utf-8'))
    outfile.close()


def make_pdb3_format_atom(atomstring):
  #put atoms into a PDB3-like format
  #Note that this reformatting does not distinguish between calcium 'CA  ' and
  #  alpha carbons ' CA '.  Both will be rendered as ' CA '.
  #No issues are known to result, but the possibility remains.
  atomstring = atomstring.strip()
  l = len(atomstring)
  if   l == 4: return atomstring
  elif l == 3: return ' '+atomstring
  elif l == 2: return ' '+atomstring+' '
  elif l == 1: return ' '+atomstring+'  '


def get_pdb_conect(pdb_file, ligand_name, ligand_chain, template_ligand=None, save_txt=None):
    pdb = prody.parsePDB(pdb_file)
    ligand = pdb.select(f'chain {ligand_chain} and resname {ligand_name}')
    assert ligand is not None and len(ligand) > 0, "Ligand not found"
    out = StringIO()
    prody.writePDBStream(out, ligand)

    rdmol = assign_bond_orders_to_pdb_ligand(out.getvalue(), ligand_name, template_ligand, remove_hydrogens=True)
    rdmol = Chem.AddHs(rdmol, addCoords=True)

    mi  =  Chem.AtomPDBResidueInfo()
    h_num = 1
    for a in rdmol.GetAtoms():
        if a.GetSymbol() == 'H':
            mi.SetName(f'H{h_num}')
            a.SetMonomerInfo(mi)
            h_num += 1

    lines = []
    first_line = f'RESIDUE   {ligand_name}    {rdmol.GetNumAtoms()}\n'
    lines.append(first_line)
    for a in rdmol.GetAtoms():
      new_line = 'CONECT'
      pdb_res_name = a.GetPDBResidueInfo().GetName().strip()
      new_line += ' ' * 6
      new_line += pdb_res_name
      num_neighbors = len(a.GetNeighbors())
      gap = 7 - len(pdb_res_name)
      new_line += ' ' * gap
      new_line += str(num_neighbors)
      nb_names = [nb.GetPDBResidueInfo().GetName().strip() for nb in a.GetNeighbors()]
      for nb_name in nb_names:
          atomstr = make_pdb3_format_atom(nb_name)
          new_line += atomstr
          new_line += ' '
      new_line += '\n'
      lines.append(new_line)

    lines.append('END\n')

    if save_txt is not None:
        with open(save_txt, 'w') as f:
            f.writelines(lines)

    return lines
