from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.result import marginal_counts
from qiskit.circuit.classical import expr
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

#size of ghz
n=4

# old school ghz
co = QuantumCircuit(n, n)
co.h(0)
for i in range(1,n):
    co.cx(0, i)
    co.measure(range(0, n), range(0, n))
simulator = AerSimulator()
job = simulator.run(co, shots=1000)
result = job.result()
counts = result.get_counts()
print("Measurement Counts:", counts)
plot_histogram(counts)
plt.show()

# simple dynamic
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.classical import expr

def construct_ghz_circuit_v5(n):
    qr = QuantumRegister(2 * n - 1, 'q')
    cr = ClassicalRegister(2*n-1, 'c')
    circ = QuantumCircuit(qr, cr)
 
    for m in range(n):
        circ.h(2 * m)
 
    for m in range(n - 1):
        circ.cx(2 * m, 2 * m + 1)
 
    for m in range(n - 1):
        circ.cx(2 * m + 2, 2 * m + 1)
 
    for m in range(n - 1):
        circ.measure(2 * m + 1, m)
 
    for m in range(n - 1):
        _condition = cr[m] if m == 0 else expr.bit_xor(_condition, cr[m])
        with circ.if_test(expr.equal(_condition, True)):
            circ.x(2 * m + 2)
    circ.measure(range(0, 2*n-1), range(0,2*n-1))
    return circ

gd = construct_ghz_circuit_v5(n)
simulator = AerSimulator()
result = simulator.run(gd, shots = 1000).result()
original_counts = result.get_counts()
# Specify the classical bits associated with the 4 qubits you want to keep
qubits_of_interest = [i for i in range(0, 2*n-1) if i%2==0]

# Generate the marginalized counts dictionary
filtered_counts = marginal_counts(original_counts, indices=qubits_of_interest)

print("Filtered 4-qubit counts:", filtered_counts)
print("Measurement Counts:", counts)
# Plot the 4-qubit histogram
plot_histogram(filtered_counts, title="Marginalized Counts (Qubits 1, 2, 4, 5)")
plt.show()
gd.draw('mpl')
plt.show()


#### teleportation-based


def construct_ghz_circuit_tel(n):
    if n < 1:
        raise ValueError("n must be at least 1")
        
    if n == 1:
        qr = QuantumRegister(1, 'q')
        cr = ClassicalRegister(1, 'c')
        circ = QuantumCircuit(qr, cr)
        circ.h(0)
        circ.measure(0, 0)
        return circ
        
    # We use 3n - 2 qubits. Data qubits are placed at indices 3*i.
    # The Right (R) ancillas are at 3*i + 1, Left (L) ancillas at 3*i - 1.
    qr = QuantumRegister(3 * n - 2, 'q')
    cr = ClassicalRegister(3 * n - 2, 'c')
    circ = QuantumCircuit(qr, cr)
    
    # 1. State preparation (O(1) Depth)
    # Prepare basic superposition for all data qubits
    for i in range(n):
        circ.h(3 * i)
        
    # Entangle data qubits with their respective local ancillas
    for i in range(n):
        if i < n - 1:
            circ.cx(3 * i, 3 * i + 1)  # Entangle D_i with R_i
        if i > 0:
            circ.cx(3 * i, 3 * i - 1)  # Entangle D_i with L_i
            
    # 2. Full Bell State Measurement (O(1) Depth)
    # Perform BSMs on adjacent ancillas to teleport and stitch the GHZ state
    for j in range(n - 1):
        R_j = 3 * j + 1
        L_j1 = 3 * j + 2
        
        circ.cx(R_j, L_j1)
        circ.h(R_j)
        
        # Measure BSM outcomes into the corresponding classical bits
        circ.measure(R_j, R_j)
        circ.measure(L_j1, L_j1)
        
    # 3. Dynamic classical feed-forward (O(1) Quantum Depth)
    # X corrections (bit-flips) based on Z-parity (L ancilla measurements)
    _cond_X = None
    for k in range(1, n):
        if k == 1:
            _cond_X = cr[2]
        else:
            _cond_X = expr.bit_xor(_cond_X, cr[3 * (k - 1) + 2])
        
        with circ.if_test(expr.equal(_cond_X, True)):
            circ.x(3 * k)
            
    # Z corrections (phase-flips) based on X-parity (R ancilla measurements)
    _cond_Z = None
    for j in range(n - 1):
        if j == 0:
            _cond_Z = cr[1]
        else:
            _cond_Z = expr.bit_xor(_cond_Z, cr[3 * j + 1])
            
    with circ.if_test(expr.equal(_cond_Z, True)):
        # We only need a single Z gate on ANY data qubit to fix global relative phase.
        # We apply it to the last data qubit.
        circ.z(3 * (n - 1))
        
    # 4. Final measurements (Verifying final state)
    circ.measure(range(3 * n - 2), range(3 * n - 2))
    
    return circ

gd = construct_ghz_circuit_tel(n)
simulator = AerSimulator()
result = simulator.run(gd, shots = 1000).result()
original_counts = result.get_counts()
# Specify the classical bits associated with the 4 qubits you want to keep
qubits_of_interest = [i for i in range(0, 3*n-2) if i%3==0]

# Generate the marginalized counts dictionary
filtered_counts = marginal_counts(original_counts, indices=qubits_of_interest)

print("Filtered 4-qubit counts:", filtered_counts)
print("Measurement Counts:", counts)
# Plot the 4-qubit histogram
plot_histogram(filtered_counts, title="Marginalized Counts (Qubits 1, 2, 4, 5)")
plt.show()
gd.draw('mpl')
plt.show()