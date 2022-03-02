import math
from fractions import Fraction
from typing import List, Dict, Tuple, Optional

from pyzx.circuit import Circuit
from pyzx.circuit.gates import Gate, qasm_gate_table, ZPhase, XPhase, CRZ

class cQASMParser(object):
    "A class to parse cqasm txt files into zx circuit diagrams"
    def __init__(self)-> None: #initializing lists we will be using later
        self.gates: List[Gate] = []
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
        circ = Circuit(self.qubit_count)
        circ.gates = self.gates
        self.circuit = circ
        return self.circuit
        
        
    def parse_command(commands):
        c = commands.split(' ')
        
        if len(c) == 1:
                com = c
        elif len(c) == 2:
                if c[1].count('[')== 1:
                        name = c[0]
                        rest = c[1]
                        name = name.lower()
                        rest = rest.lower()
                        if name in ["i","h","x","y","z","x90","y90","mx90","my90","s","sdag","t","tdag"]:
                                val = rest.split('[',1)[1].split(']')[0]
                                #these are the group of 1 qubit gates that do not take arguments
                                #print("There is a ",name, " gate on the ", val, " qubit(s)")
                        if name.split('_')[0] in ["prep"]:
                                val = name.split('_')[1]
                                qubits = rest.split('[')[1].split(']')[0]
                                #these are the where we prepare the gates in their various states
                                #print("The qubits ",qubits ,"are prepared in the", val,"basis.")
                        if name.split('_')[0] == "measure":
                                val = name.split('_')[1]
                                #check how it is measured
                        if name == 'qubits':
                                self.qubit_count = rest
                elif c[1].count('[') == 2:
                        name = c[0]
                        rest = c[1]
                        name = name.lower()
                        rest = rest.lower()
                        if name in ["cnot"]:
                                val = rest.split(",")
                                qubits = []
                                for i in range(len(val)):
                                        qubit = val[i].split('[')[1].split(']')[0]
                                        qubits.append(int(qubit))
                                        qubits = sorted(qubits)
                                        print(qubits)
                                print("There is a ",name,"gate on the qubits ", qubits)
    