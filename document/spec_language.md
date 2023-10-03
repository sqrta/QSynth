# Specification language

$$
\begin{align*}
Spec &::= |Input\rangle \mapsto |Output\rangle\\
Input &::= \text{\textbf{const}}_{r_n} \mid \text{\textbf{var}}_{r_n} \mid |Input_1 \otimes Input_2\rangle\\
Output &::= \text{\textbf{const}}_{r_n} \mid \text{\textbf{var}}^{\text{bond}}_{r_n} \mid |Output_1 \otimes Output_2\rangle \mid e^{i \phi}|Output'\rangle \\&\qquad  \mid |\text{\textbf{uop }} Output'\rangle \mid |Output_1 \text{\textbf{ bop }} Output_2\rangle \mid \sum_{y\in \{0,1\}^{r_n}} |Output^y\rangle\\
r_n &::= \text{\textbf{const}} \mid n \mid r_n^1 \text{\textbf{ bop }} r_n^2
\end{align*}
$$