\binsearch(f, a, b, \varepsilon) = {
    \begin{cases}
        c_0 &= a \\
        d_0 &= b \\
        m_i &= (c_i + d_i) / 2 \\
        g_i &= f(c_i) * f(m_i) \\
        c_i &= \begin{cases}
            c_{i-1},& g_{i-1} \leq 0 \\
            m_{i-1},& else
        \end{cases} \\
        d_i &= \begin{cases}
            m_{i-1},& g_{i-1} \leq 0 \\
            d_{i-1},& else
        \end{cases}
    \end{cases};
    s = \left\{ i \mid d_i - c_i < \varepsilon \right\};
    i = s_0;
    \left\{ m_i, c, d \right\}
};
g(x) = (x+500)*(x-1000);
r = \binsearch(g, 0, 2000, 10^{-6});
\models(r_0 - 1000 < 0.000001)
