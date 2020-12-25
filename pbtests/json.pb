a = \prec(\begin{cases}
\text{params} : & t(\text{dict}, t(\text{str}), t(\text{float})) \vdash 0, \\
\text{array}: & \begin{cases}
        \text{arr}: & t(\text{arr}, t(\text{arr}, t(\text{float})^2)) \vdash 1, \\
        \text{sizes}: & t(?) \vdash \text{q}
    \end{cases}, \\
\text{cb}: & t(\text{func}, t(?), \begin{cases}
    \text{arr}: & t(\text{arr}, t(\text{arr}, t(\text{float})^2)) \vdash 0, \\
    \text{sizes}: & t(?) \vdash 1
\end{cases}) \vdash \text{cb}
\end{cases}); \\

b = \overbrace{\text{json}}.(a); \\

b
