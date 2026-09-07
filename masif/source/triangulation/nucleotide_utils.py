from io import StringIO
from rdkit import Chem
from Bio.PDB.Entity import Entity as BioEntity
from Bio.PDB.Residue import Residue
from Bio.PDB.PDBIO import PDBIO


# https://proteopedia.org/wiki/index.php/Standard_residues
# note: rdkit's MolFromSequence doesn't support inosine
NUCLEOTIDES = ["A", "C", "G", "U", "DA", "DC", "DG", "DT", "DU"]


def biopython_to_rdkit(pdb_object: BioEntity):
    bio_io = PDBIO()
    bio_io.set_structure(pdb_object)
    string_io = StringIO()
    bio_io.save(string_io)
    rdmol = Chem.MolFromPDBBlock(string_io.getvalue(), proximityBonding=True, removeHs=False)
    return rdmol


def nucleotide_as_rdmol(name):
    # https://www.rdkit.org/docs/source/rdkit.Chem.rdmolfiles.html#rdkit.Chem.rdmolfiles.MolFromSequence
    rna_no_cap = 2
    dna_no_cap = 6
    return Chem.MolFromSequence(name[-1:], flavor=dna_no_cap if name.startswith("D") else rna_no_cap)
