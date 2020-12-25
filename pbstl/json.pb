f(\tree) = \left(
    \src = \prec(?(\text{key}) : ?(\text{val})).(2);
    \print = \inject(\text{print});
    * = \print(\src);
    \dstf(a) = \print(a);
    \dst = \prec(?(\text{key}) / ?(\text{val})).(2);
    \replac = \overbrace{\text{macro}}.(\text{replac});
    \res = \replac(\tree(2), \src, \dst);
    \res
\right);
f
