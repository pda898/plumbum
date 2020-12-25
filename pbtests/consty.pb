\\
f_0 = 2 + 4; \\

w_0(x) = {
    w_1(y) = {
        w_2(z) = x + y + z;
        w_2
    }; w_1
}; \\

f_1 = w_0(1).(2).(3); \\

g(t) = \left(
    r = \overbrace{\text{macro}}.(\text{replac}).(
        t(2),
        \prec(?(\text{a}) + ?(\text{b})).(2),
        \prec(?(\text{a}) + ?(\text{b}) - 1).(2),
        \top
    );
    g = \succ(r);
    g
\right); \\

f_2 = g(\prec({
    f(a, b) = a + 2(b + 3);
    f
})); \\

f_3 = g(\prec({
    f(a) = a + 43;
    f
})); \\

f_4 = w_0(1); \\

\left\{ f_0, f_1, f_2(2, 3), f_3(4), f_4(2) \right\}
