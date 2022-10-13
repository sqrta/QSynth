def GHZ(N):
	circuit=QuantumCircuit(N+1)
	def S(circ, n):
		if(n==0):
			circ.h(0)
		else:
			circ.id()
			S(circ,n-1)
			circ.cx(n-1,n)
	S(circuit,N)
	return circuit