a_0 = 3;
a_1(x_3, x) = {
    x_3 + x
};
a_2(x_5) = x_5 + 3;
a = a_0 + a_1(a_0, 3) + a_2(-3);
\models(a \equiv 9)
