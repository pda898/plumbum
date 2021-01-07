## Variables

`a = 2; b = 3; a + b`

Creates new local with vars `a` and `b`

Result value is last sequence

In one local all variables is unique, but in sublocal may present variables from upper local

`a = 2; {a = 3; a}`

Quotes `{}` uses only for grouping and not present in LaTeX syntax, so you can write that

`a = 2; \left\( a = 3; a \right\)`

## Functions

Base function can writed like that

`f(a, b) = {c = a + b; c - 3}`

Rules for arguments is rules for variables

In sequence of function variable `f` don't present, so recursion must be written by that case

`\begin{cases} f_x = f_{x+1} \\ f_0 = 0 \end{cases}`

All recursions is memoize

For use tail rec we can use `f_x = \gets(x+1)` for optimize

## Generators

Generator is function, based for another generators. If ordinary or recurrent function has normal behaviour with integer arguments, it can use like generator.

- The most simply generator is set

`f = \left\{ 1, 2, 3 \right\}`

In that case `f(0)` is `1` and so on.

- Mapping generator

`g = \left\{ x + 3 \mid x \in f \right\}`

Thats works like `g(x) = f(x + 3)` and so on.

- Filtering generator

`g = \left\{ x \in f \mid x < 3 \right\}`

If `f = \left\{ 1, 4, 2, 5 \right\}`, `g(1) \equiv 1` and `g(2) \equiv 2`. Cuz lazy work it can use with infinite generators

## Function operators

- Down the artity

`g = f(*, 3)`

In that case `g(4) \equiv f(4, 3)` and so on

- Call the expression

For situation like that:

`f(x) = { g(y) = x + y; g }`

We can call it like:

`f(2).(3) \equiv 5`

## Macros

We can use operator `a = \prec(expression)` for use expression as sequence tree in macros. Operator `\succ(a)` expand sequence tree. All `\succ` operators expands on translate time, so if use `\prec(expression)` and constant optimization cannot remove it like in case:

`f(a) = \prec(a + 3)`

So destination code in lang, witch not supported serialized sequence tree, snippet may contains surprized expressions like `f(a) = 0` in upper case.

## Another operators

LaTeX has so much math operators, and only several of them presents in that realization. Some operators like integrals and limits may realize with macros, another (like matrix) suported now but not tested in all cases:

```
m = \begin{pmatrix}
    3 & 4 & 5 \\
    6 & 7 & 8
\end{pmatrix}; \\

m(1, 2)
```
