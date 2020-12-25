\\

\sigma_w(c, t) = (0.0123 + 3647.2 / c ^ 0.955) \cdot 82 / (1.8t + 39); \\

\sigma_{f_m}(S, C, n, T) = S ^ n \cdot \sigma_w(10^6 \cdot C, T); \\

\sigma_r(\sigma_f, \sigma_c, \varphi, p) = { \\
    \begin{cases}
        s_0 = 1.0 \\
        s_n = \sigma_f \cdot \varphi^{3/2} \cdot \left (
            \frac {1 + (1-3p) \cdot \sigma_c / (2 s_{n-1})}
                {1 - (1-3p) \cdot \sigma_c / (2 \sigma_f)}
            \right ) ^ {3p / (1-3p)} \\
    \end{cases};
    r = \left\{ i \mid
        \left\| s_i - s_{i+1} \right\| < 0.000001
        \lor i \geqslant 100
    \right\};
    i = r_1;
    \begin{cases}
        s_{i+1}, i < 100 \\
        0
    \end{cases}
}; \\

* = \models( \left\|
    \sigma_r(10, 0.2, 0.2, 0.2) - 0.9568313735926898
\right\| < 0.000001 ); \\

r = {
    k = \left\{ i \mid i \right\}; \\
    o = \left\{ {
        \varphi = 0.01 + (0.4 - 0.01) / (10 - 1) * (i - 1);
        s = \sigma_r(10, 0.02, \varphi, 0.2);
        d = \left\| s / 10 - 1 * \varphi^{3/2} \right\|;
        * = \models(d < 0.001);
        \left\{ i, d \right\}
    } \mid i \in k \right\}; \\
    \begin{cases}
        r_11 = 0 \\
        r_n = \left\{ o_n, r_{n+1} \right\}
    \end{cases};
    r_1
};

r
