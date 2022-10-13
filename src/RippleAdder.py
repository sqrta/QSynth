def RippleAdder(N):
	circuit=QuantumCircuit(2*N+1)
	def S(circ, n):
		if(n==0):
			circ.id()
		else:
			circ.cx(2*N-n,N-n)
			circ.cx(2*N-n,0)
			circ.ccx(0,N-n,2*N-n)
			S(circ,n-1)
			circ.ccx(0,N-n,2*N-n)
			circ.cx(2*N-n,0)
			circ.cx(0,N-n)
	S(circuit,N)
	return circuit