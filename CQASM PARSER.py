import math
from fractions import Fraction
from typing import List, Dict, Tuple, Optional

from pyzx.circuit import Circuit
from pyzx.circuit.gates import Gate, qasm_gate_table, ZPhase, XPhase, CRZ

class cQASMParser(object):
    "A class to parse cqasm txt files into zx circuit diagrams"
    def __init__(self)-> None: #initializing lists we will be using later
        self.gates: List[Gate] = []
        self.customgates: Dict[str,Circuit] = {}
        self.registers: Dict[str,Tuple[int,int]] = {}
        self.qubit_count: int = 0
        self.circuit: Optional[Circuit] = None
    
    def parse(self, s: str, strict:bool=True) -> Circuit:
        lines = s.splitlines() # spliting the input file by line
        r=[]
        for s in lines:
            if s.find("#")!=-1: # clearing out the portion of any lines that comes after a hashtag ie. is commmented
                t = s[0:s.find('#')].strip()
            else: t = s.strip
            if t: r.append(t) # creating a list of the lines without comments
            
        if r[0].startswith("Version"):
            r.pop(0) # if the first line starts with version, pop it out
        elif strict:
            raise TypeError("File doesn't start with cQasm denotation") # denotes that wearent sure if it is a cqasm file
        data = "\n".join(r) # combines the list back into a text file with \n meaning new line
        
        
        commands = [s.strip() for s in data.split(";") if s.strip()]
        
        
        
        
        #### this is the command parsing function
        def parse_command(self, c: str, registers: Dict[str,Tuple[int,int]]) -> List[Gate]:
        gates: List[Gate] = []
        name, rest = c.split(" ",1)
        args = [s.strip() for s in rest.split(",") if s.strip()]
        if name == 'qubits':
            regname, sizep = args[1].split("")