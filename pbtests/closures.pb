f(x) = {
    g(y) = 3 + {
        z = x + y;
        z
    };
    h(y) = {
        z = x + y;
        z + 3
    };
    w(y) = x + y + 3;
    \left\{ g, h(3), {
        q = w(3);
        q
    } \right\}
};
r = f(4);
t = r(0);
\models(
    \left\{ t(3), r(1), r(2) \right\}
    \equiv
    \left\{ 10, 10, 10 \right\}
)
