w(g, f) = {
    \begin{cases}
        o_{i,r} = {
            v = g(i);
            \begin{cases}
                v, v \equiv \otimes \\
                {
                    q = f(v);
                    \begin{cases}
                        i, q \\
                        \gets_{i+r,r}
                    \end{cases}
                }
            \end{cases}
        } \\
        s_{p,p_i,p_o,r} = {
            v = o_{p_i,r};
            \begin{cases}
                v, v \equiv \otimes \\
                v, p \equiv p_o \\
                \gets_{p,v+r,p_o+r,r}
            \end{cases}
        }
    \end{cases};

    q(p) = {
        i = \begin{cases}
            s_{1,0,1,1}, p \equiv 0 \\
            s_{p,0,1,1}, p > 0 \\
            s_{p,0,-1,-1}
        \end{cases};
        \begin{cases}
            i, i \equiv \otimes \\
            g(i)
        \end{cases}
    };

    q
};

g = \left\{ 1, 5, 2, 6 \right\};
f(e) = e < 4;
a_s = w(g, f);

* = \models(a_s(1) \equiv 1);
* = \models(a_s(2) \equiv 2);
* = \models(a_s(3) \equiv \otimes);
* = \models(a_s(0) \equiv 1);
* = \models(a_s(-1) \equiv 1);
* = \models(a_s(-2) \equiv \otimes);
0
