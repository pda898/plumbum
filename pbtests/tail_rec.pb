\begin{cases}
    f_{0,0,50} = 54 \\
    f_{n,m,s} = \begin{cases}
        \gets(n-1,m-1,s+10), n < 10 \\
        \gets({
            q = n-5;
            q
        }, {
            q = m-5;
            q
        },s)
    \end{cases}
\end{cases};
g = f(*,*,0);
\models(g(15,15) \equiv 54)
