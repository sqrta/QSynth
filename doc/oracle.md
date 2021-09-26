# Synthesis For Oracle Algorithms
Target DeutschJozsa Program
```coq
Definition deutsch_jozsa' {n} (U : base_ucom n) : base_ucom n :=
  X 0 ; npar n U_H ; U; npar n U_H.
```
Given an oracle $f:\{0,1\}^n\rightarrow \{0,1\}$, we need to find a program $P$ that the corresponding $\alpha_P$ satisfies
$$
\sum_{i=0}^{2^n-1} f(i) = 2^{n-1} \rightarrow \alpha_P(n+1,\ket{0}^{n+1}, \ket{0}^{n+1}) = 0
$$
and
$$
\sum_{i=0}^{2^n-1} f(i) = 2^{n} \lor \sum_{i=0}^{2^n-1} f(i) = 0 \rightarrow \alpha_P(n+1,\ket{0}^{n+1}, \ket{0}^{n+1}) = \pm1
$$
When we meet the target program in the search, after SMT solver's simplication, its $\alpha$ is an expression
$$
\frac{1}{2^n}\sum_{i=0}^{2^n-1} If(f(i)==0, 1, -1) \qquad//(-1)^{f(i)}
$$
To verify the two target propositions, we need a hint function from user or we encode it the synthesizer: $\lambda a. 2\cdot a-1$. Then we use SMT solver to verify
$$
\forall i\in \{0,1\}^n, 2\cdot f(i)-1 = If(f(i)==0, 1, -1)
$$
Then we can calculate the final expression to
$$
\frac{1}{2^n}\sum_{i=0}^{2^n-1} If(f(i)==0, 1, -1) = 2\cdot \sum_{i=0}^{2^n-1} f(i) - 2^{n-1}
$$
and verify the two target propositions easily.
<!-- Given an classical oracle function $f: \{0,1\}^n\rightarrow \{0,1\}^c$ where $c$ is a known constant, $f$ can be represented by a bit-vector $b_f \in \{0,1\}^{2^n\cdot c}$. Calling oracle $f$ with input $x\in \{0,1\}^n$ equals to extracting the corresponding bits in $b_f$.
$$
f(x) = Extract(b_f, cx, cx+c)
$$
Consider an quantum oracle algorithm with $n=n'+c$ qubits and qubits $q_0,...,q_{c-1}$ are used to store the output of the oracle and the oracle $f: \{0,1\}^{n'}\rightarrow \{0,1\}^c$. Then the quantum oracle can be represent as an $\alpha(n,x,y)$ function
$$
\alpha_f(n,x,y) = \delta(x[c:n], y[c:n])\cdot \delta(y[0:c-1], x[0:c-1]\oplus f(x[c:n]))\\
=\delta(x[c:n], y[c:n])\cdot \delta(y[0:c-1], x[0:c-1]\oplus Extract(b_f, cx, cx+c))
$$
and this function can be transferred to an SMT instance. So the oracle can be regarded as an $n$-bit sparse components and used in the circuit construction. In the synthesis process we need to verify that the circuit satisfies the specification given all legal oracle $f$. So we just need to add $b_f$ as a quantifier variable like $x,y,n$.
$$
\forall n,x,y, b_f\in \{0,1\}^{2^{n-c}},  \alpha_{left} = \alpha_{right}
$$ -->


