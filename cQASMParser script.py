import math
from fractions import Fraction
from typing import List, Dict, Tuple, Optional
import collections 
from collections import Counter
import re
from pyzx.circuit import Circuit
from pyzx.circuit.gates import Gate, qasm_gate_table, ZPhase, XPhase, CRZ, gate_types

class cQASMParser(object):
    "This is going to be the class that outputs cQASM files into a circuit"
    def __init__(self) -> None:
        self.gates : List[Gate] = []
        self.qubit_count : int = 0
        self.binary_count : int = 0
        self.circuit: Optional[Circuit] = None
    
    def parse(self, s: str, strict: bool = True) -> Circuit:
        "Split and parse the commands individually"
        s = s.lower()
        lines = s.splitlines()
        r = []
        for s in lines:
            if s.find('#')!=-1:
                t = s[0:s.find('#')].strip()
            else:
                t = s.strip()
            if t : r.append(t)
        if r[0].startswith('version'):
            r.pop(0)
        elif strict:
            raise TypeError("File doesnt start with cqasm denotation")
        data = "\n".join(r)
        commands = [s.strip() for s in data.split(";") if s.strip()]
        for c in commands:
           # print(c)
            if c.startswith(".") == False:
                if c.count("{") == 0:
                    self.gates.extend(self.parse_command(c))
                elif c.count("{") > 0:
                    c = c.split("|")
                    for i in range(len(c)):
                        c[i] = c[i].strip()
                        if c[i].count("{") == 1:
                            c[i] = (c[i])[1:].strip()
                            self.gates.extend(self.parse_command(c[i]))
                        elif c[i].count("}") == 1:
                            c[i] = (c[i])[:-1].strip()
                            self.gates.extend(self.parse_command(c[i]))  
                        else:
                            self.gates.extend(self.parse_command(c[i]))             
        circ = Circuit(self.qubit_count)
        circ.gates = self.gates
        self.circuit = circ
        return self.circuit
    
    
    def parse_command(self, c:str) -> List[Gate]:
        "Take the split arguements, pass them up and move on"
        gates : List[Gate] = []
        if c.startswith("measure"): return gates 
        if c.startswith("prep"): return gates
        ### qubit number
        name, rest = c.split(" ",1)
        qlist = []
        qlisttrue =[]
        if name.startswith('qubits'):
            if type(int(rest)) == int:
                self.qubit_count = int(rest)
                self.binary_count = int(rest)
            else:
                raise TypeError("Non integer number of qubits")
        ### 1 qubit gates
        if name in ("x","z","s","t","h","sdag","tdag","h"):
            if rest.count("q[") != 0: ###for where there ARE qubits
                if rest.count("q[") == 1:
                    rest = rest.split("[")[1]
                    rest = rest.split("]")[0]
                    rest = rest.split(",") 
#above commands strip the numbers inside the square brackets,& split at the comma
                    for l in range(len(rest)):
                        if rest[l].count(":") == 0:
                            qlist.append(rest[l])
                        else: 
                            firstside = (rest[l].split(":")[0])[-1]
                            secondside = (rest[l].split(":")[1])[0]
                            for k in range(int(firstside),int(secondside)+1):
                                qlist.append(k)
                qlist = [int(i) for i in qlist]
                for i in qlist:
                    if i not in qlisttrue:
                        qlisttrue.append(i)  
                qlisttrue.sort() 
            for i in qlisttrue:
                if name in ('sdag'):
                    g = qasm_gate_table["sdg"](i)
                elif name in ("tdag"):
                 g = qasm_gate_table["tdg"](i)
                else:
                    g = qasm_gate_table[name](i)
                gates.append(g) 
                
########################## 2 qubit gates 
        if name in ("cnot","cz","swap"):
            if rest.count("q[") != 2:
                raise TypeError("Incorrect number of gates")
            elif rest.count("q[") ==2:
                rest = rest.split("],")
                restcontrolqubit = rest[0]
                resttargetqubit = rest[1]
                restcontrolqubit = restcontrolqubit.split("[")[1]
                restcontrolqubit = restcontrolqubit.split("]")[0]
                restcontrolqubit = restcontrolqubit.split(",")
                resttargetqubit = resttargetqubit.split("[")[1]
                resttargetqubit = resttargetqubit.split("]")[0]
                resttargetqubit = resttargetqubit.split(",")   
                qlistcont = []
                qlisttarg = []
                for l in range(len(restcontrolqubit)):
                    if restcontrolqubit[l].count(":") == 0:
                        qlistcont.append(restcontrolqubit[l])
                    else: 
                        firstside = (restcontrolqubit[l].split(":")[0])[-1]
                        secondside = (restcontrolqubit[l].split(":")[1])[0]
                        for k in range(int(firstside),int(secondside)+1):
                            qlistcont.append(k)
                qlistcont = [int(i) for i in qlistcont]
                qlistconttrue = []
                for i in qlistcont:
                    if i not in qlistconttrue:
                        qlistconttrue.append(i)  
                qlistconttrue.sort()
     
                for l in range(len(resttargetqubit)):
                    if resttargetqubit[l].count(":") == 0:
                        qlisttarg.append(resttargetqubit[l])
                    else: 
                        firstside = (resttargetqubit[l].split(":")[0])[-1]
                        secondside = (resttargetqubit[l].split(":")[1])[0]
                        for k in range(int(firstside),int(secondside)+1):
                            qlisttarg.append(k)
                qlisttarg = [int(i) for i in qlisttarg]
                qlisttargtrue = []
                for i in qlisttarg:
                    if i not in qlisttargtrue:
                        qlisttargtrue.append(i)  
                qlisttargtrue.sort() 
            if len(qlistconttrue) == len(qlisttargtrue): 
                for i in range(len(qlistconttrue)):
                    if name in ('cnot'):
                        g = qasm_gate_table["cx"](qlistconttrue[i],qlisttargtrue[i])
                    elif name in ("cz"):
                        g = qasm_gate_table["cz"](qlistconttrue[i],qlisttargtrue[i])
                    elif name in ("swap"):
                        g = qasm_gate_table["swap"](qlistconttrue[i],qlisttargtrue[i])
                    gates.append(g)  
    
########## 1 qubit gates with arguments
        if name in ("rx","ry","rz"):
            if rest.count("q[") != 0: ###for where there ARE qubits
                if rest.count("q[") == 1:
                    rest = rest.split("],")
                    rest[0] = rest[0].split("[")[1]
                    rest[0] = rest[0].split("]")[0]
                    rest[0] = rest[0].split(",") 
                    qubitstring = rest[0]
                    argstring = rest[1]
                    args = int(argstring)
                    for l in range(len(qubitstring)):
                        if rest[l].count(":") == 0:
                            qlist.append(qubitstring[l])
                        else: 
                            firstside = (qubitstring[l].split(":")[0])[-1]
                            secondside = (qubitstring[l].split(":")[1])[0]
                            for k in range(int(firstside),int(secondside)+1):
                                qlist.append(k)
                qlist = [int(i) for i in qlist]
                for i in qlist:
                    if i not in qlisttrue:
                        qlisttrue.append(i)  
                qlisttrue.sort() 
            
            for i in qlisttrue:
                phase = self.parse_phase_arg(args)
                if name in ('rx'):
                    g = gate_types['XPhase'](i,phase = phase)
                #elif name in ("ry"):
                    #    g = qasm_gate_table['ry'](i,args)
                elif name in ("rz"):
                    g = gate_types['ZPhase'](i,phase = phase)
            gates.append(g)  
            
            
### ### 2 qubit gates that take 1 argument
        if name in ("crk","cr"):
            rest = rest.split("],")
            restcontrolqubit = rest[0]
            resttargetqubit = rest[1]
            args = int(rest[2])
            restcontrolqubit = restcontrolqubit.split("[")[1]
            restcontrolqubit = restcontrolqubit.split("]")[0]
            restcontrolqubit = restcontrolqubit.split(",")
            resttargetqubit = resttargetqubit.split("[")[1]
            resttargetqubit = resttargetqubit.split("]")[0]
            resttargetqubit = resttargetqubit.split(",")   
            qlistcont = []
            qlisttarg = []
            for l in range(len(restcontrolqubit)):
                if restcontrolqubit[l].count(":") == 0:
                    qlistcont.append(restcontrolqubit[l])
                else: 
                    firstside = (restcontrolqubit[l].split(":")[0])[-1]
                    secondside = (restcontrolqubit[l].split(":")[1])[0]
                    for k in range(int(firstside),int(secondside)+1):
                        qlistcont.append(k)
            qlistcont = [int(i) for i in qlistcont]
            qlistconttrue = []
            for i in qlistcont:
                if i not in qlistconttrue:
                    qlistconttrue.append(i)  
            qlistconttrue.sort()
     
            for l in range(len(resttargetqubit)):
                if resttargetqubit[l].count(":") == 0:
                    qlisttarg.append(resttargetqubit[l])
            else: 
                firstside = (resttargetqubit[l].split(":")[0])[-1]
                secondside = (resttargetqubit[l].split(":")[1])[0]
                for k in range(int(firstside),int(secondside)+1):
                    qlisttarg.append(k)
            qlisttarg = [int(i) for i in qlisttarg]
            qlisttargtrue = []
            for i in qlisttarg:
                if i not in qlisttargtrue:
                    qlisttargtrue.append(i)  
            qlisttargtrue.sort() 
    
            if len(qlistconttrue) == len(qlisttargtrue): 
                for i in len(qlistconttrue):
                    phase = self.parse_phase_arg(args)
                    
                    if name in ('cr'):
                        g = qasm_gate_table["crz"](qlistconttrue[i],qlisttargtrue[i],phase)
                    elif name in ("crk"):
                        g = qasm_gate_table["crz"](qlistconttrue[i],qlisttargtrue[i],(math.pi/(2^args)))
                gates.append(g)  
            
            
            ### toffoli gate implementation
        if name in ("toffoli"):
            rest = rest.split("],")
            for i in range(len(rest)):   
                rest[i] = rest[i].split("[")[1]
                rest[i] = rest[i].split("]")[0]
                rest[i] = rest[i].split(",") 
            for l in range(len(rest)):
                qlist=[]
                qlisttrue=[]
                if rest[l].count(":") == 0:
                    qlist.append((int(rest[l][0])))
                else: 
                    firstside = (rest[l].split(":")[0])[-1]
                    secondside = (rest[l].split(":")[1])[0]
                    for k in range(int(firstside),int(secondside)+1):
                        qlist.append(int(k))
                qlist = [int(i) for i in qlist]
                for i in qlist:
                    if i not in qlisttrue:
                        qlisttrue.append(i)  
            rest[l] = qlisttrue
            for i in range(len(rest)):
                if type(rest[i]) == list:
                    rest[i] = int(rest[i][0])
            g = gate_types['TOF'](rest[0],rest[1],rest[2])
            gates.append(g)
        return gates
    
    def parse_phase_arg(self, val):
        try:
            phase = float(val)/math.pi
        except ValueError:
            if val.find('pi') == -1: raise TypeError("Invalid specification {}".format(name))
            try:
                val = val.replace('pi', '')
                val = val.replace('*','')
                if val.find('/') != -1:
                    n, d = val.split('/',1)
                    n = n.strip()
                    if not n: n = 1
                    elif n == '-': n = -1
                    else: n = int(n)
                    d = int(d.strip())
                    phase = Fraction(n,d)
                else:
                    val = val.strip()
                    if not val: phase = 1
                    else: phase = float(val)
            except: raise TypeError("Invalid specification {}".format(val))
            phase = Fraction(phase).limit_denominator(100000000)
            return phase           
           
def cqasm(s: str) -> Circuit:
    "Parses a string representing a program in cQasm and outputs a circuit"
    p = cQASMParser()
    return p.parse(s, strict=False)