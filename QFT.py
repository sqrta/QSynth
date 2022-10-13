def QFT(N):
	circuit=QuantumCircuit(N+1)
	def S(circ, n):
		if(n==0):
			circ.h(0)
		else:
			circ.C_RZN(n)
			S(circ,n-1)
			circ.id()
	S(circuit,N)
	return circuit