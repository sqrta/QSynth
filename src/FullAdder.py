def FullAdder(N):
	circuit=QuantumCircuit(3*N+1)
	def S(circ, n):
		if(n==0):
			circ.id()
		else:
			circ.id()
			S(circ,n-1)
			circ.ccx(n,N+n,2*N+n)
			circ.cx(n,N+n)
			circ.ccx(N+n,0,2*N+n)
			circ.cx(N+n,0)
			circ.cx(n,N+n)
			circ.swap(0,2*N+n)
	S(circuit,N)
	return circuit