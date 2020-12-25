from tree import E, create
from translator import cody, execute, Unclosure

CONST = 2
DIFFCONST = 1
NOCONST = 0


def _isConst(el):
    if el.t in ['string', 'number', 'zero']:
        return (CONST, el)
    if el.v == '≺':
        return (CONST, el)


def _include(fn):
    import os
    with open(os.path.join('pbstl', fn + '.pb'), 'r', encoding='utf8') as f:
        s = f.read()
    s = create(s)
    s = _walk(s, [])
    print('-' * 50)
    return s


def _res2E(res):
    if type(res) in [int, float]:
        el = E()
        el.t = 'number'
        el.v = str(res)
        return el
    if type(res) in [str]:
        el = E()
        el.t = 'string'
        el.v = res
        return el
    if type(res) == E:
        if res.isFunc('≺'):
            return res
        return E.func('≺', [res])
    return None


def _gorun(el, repls):
    s = E.func(
        ';',
        repls + [el]
    )
    s = Unclosure.bind(s)
    MACRO.clear()
    s = cody(s, 'py', 'generators/py.py')
    s = execute(s)
    s = s()
    s = _res2E(s)
    return s


def _insert(el, uncert):
    if type(el) in [list, tuple]:
        if len(el) == 0:
            return (False, el)
        res = [_insert(e, uncert) for e in el]
        if not max(e[0] for e in res):
            return (False, el)
        res = [e[1] for e in res]
        if type(el) == tuple:
            res = tuple(res)
        return (True, res)
    if not isinstance(el, E):
        return (False, el)
    if el.t != 'f':
        return (False, el)
    if el.v == '≻' and el[0] == uncert.obj[0]:
        return (True, uncert.args[0])
    if len(el.args) == 0:
        return (False, el)
    args = [_insert(e, uncert) for e in el.args]
    if not max(e[0] for e in args):
        return (False, el)
    nel = E.func(el.v, [e[1] for e in args])
    return (True, nel)


def _insert_full(el, repls, uncert):
    (isChange, nel) = _insert(el, uncert)
    if isChange:
        return nel
    ri = None
    for i in range(len(repls)):
        ii = len(repls) - i - 1
        if repls[ii][2] is None:
            continue
        (isChange, nel) = _insert(repls[ii], uncert)
        if not isChange:
            continue
        if ri is not None:
            raise Exception('Multi nodes find by uncert')
        ri = ii
        break
    if ri is None:
        raise Exception('Cannot find uncert node')
    return E.func(';', [nel] + repls[ri+1:] + [el])


def _run(pr, repls):
    (c, el) = pr
    if _isConst(el):
        return (c, el)
    if el.isFunc('`pipely') and el[0].isFunc('`apply') and el[0][0].v == '⏞':
        if len(el.args) != 2:
            return (NOCONST, el)
        if el[1].t != 'string':
            return (NOCONST, el)
        return _include(el[1].v)
    if el.isFunc('`inject'):
        return (NOCONST, el)
    repls = [e[1] for e in repls if e[1][2] is not None]
    iter = 0
    while True:
        iter += 1
        print('Iter =>', iter)
        try:
            res = _gorun(el, repls)
        except Exception as e:
            res = MACRO.find_throwed_uncert(e)
            if res is None:
                raise
        if isinstance(res, MACRO.Uncert):
            print('Uncert =>', res)
            if len(res.args) != 1 or not isinstance(res.args[0], E):
                try:
                    raise res
                except Exception:
                    raise Exception('Unsupported')
            el = _insert_full(el, repls, res)
            continue
        print('Res =>', res)
        if res is None:
            return (NOCONST, el)
        else:
            return (CONST, res)


def _find_repl(n, repls):
    res = None
    for i in range(len(repls)):
        if repls[len(repls)-i-1][1][0] == n:
            res = repls[len(repls)-i-1]
            break
    return res


def _walk(el, repls):
    if type(el) in [list, tuple]:
        if len(el) == 0:
            return (NOCONST, el)
        res = []
        for e in el:
            (c, e) = _walk(e, repls)
            if c == CONST:
                (c, e) = _run((c, e), repls)
                assert c == CONST
            res.append(e)
        if type(el) == tuple:
            res = tuple(res)
        return (NOCONST, res)
    if not isinstance(el, E):
        return (NOCONST, el)
    if _isConst(el):
        return (CONST, el)
    if el.t != 'f':
        return (NOCONST, el)
    if el.v == '`apply':
        if len(el.args) > 1:
            return _walk(E.func(
                '`pipely',
                [E.func('`apply', el[:1])] + el[1:]
            ), repls)
        res = _find_repl(el[0], repls)
        if res is None:
            return (DIFFCONST, el)
        if res[0] == CONST and len(res[1][1]) == 0:
            return (CONST, res[1][2])
        return (res[0], el)
    if el.v == 'msub':
        return _walk(E.func('`apply', [el]), repls)
    if el.v == '`repl':
        subrepls = repls + [(DIFFCONST, E.func(
            '`repl',
            [e, [], None]
        )) for e in el[1]]
        (resC, resE) = _walk(el[2], subrepls)
        if resC == CONST:
            (resC, resE) = _run((CONST, resE), subrepls)
        return (resC, E.func(
            '`repl',
            el[:2] + [resE] + el[3:]
        ))
    if el.v == ';':
        subrepls = repls[:]
        for e in el[:-1]:
            subrepls.append(_walk(e, subrepls))
        res = _walk(el[-1], subrepls)
        return (res[0], E.func(
            ';',
            [e[1] for e in subrepls[len(repls):]] + [res[1]]
        ))
    res = [_walk(e, repls) for e in el.args]
    resE = E.func(el.v, [])
    if el.v == '`pipely':
        resF = res[0]
        res = res[1:]
        resE.args.append(resF[1])
    resC = min(e[0] for e in res)
    for (c, e) in res:
        if c == resC:
            resE.args.append(e)
            continue
        if c == CONST:
            (c, e) = _run((CONST, e), repls)
            assert c == CONST
            resE.args.append(e)
            continue
        resE.args.append(e)
    if el.v == '`pipely':
        # t2(t1), t3 is type of t2
        t1 = resC
        t2 = resF[0]
        ARG_t2 = 0
        REPL_t2 = 1
        TREE_t2 = 2
        t3 = TREE_t2
        if resF[1].isFunc('`apply'):
            replF = _find_repl(resF[1][0], repls)
            if replF is None:
                t3 = REPL_t2
            elif replF[1][2] is None:
                t3 = ARG_t2
            else:
                t3 = REPL_t2
        if t2 == DIFFCONST:
            if t3 == REPL_t2:
                if t1 == CONST:
                    return _run((DIFFCONST, resE), repls)
                if t1 == NOCONST:
                    return (NOCONST, resE)
            return (DIFFCONST, resE)
        if t3 == ARG_t2:
            raise Exception('Inpossible')
        if t2 == CONST and t3 == REPL_t2:
            return (CONST, replF[1][2])
        if t1 == CONST:
            return _run((t2, resE), repls)
        return (t1, resE)
    return (resC, resE)


# TODO one thread!
class MACRO:
    data = {}

    class Uncert(Exception):
        def __str__(self):
            return '%s AS %s' % (
                repr(self.args),
                str(self.obj)
            )

    def insert(obj):
        id = 0 if len(MACRO.data) == 0 else max(MACRO.data) + 1
        MACRO.data[id] = obj
        return id

    def get(id):
        obj = MACRO.data.get(id)
        if obj is None:
            raise Exception('Wrong id given')
        return obj

    def clear():
        MACRO.data = {}

    def uncert(id, args):
        e = MACRO.Uncert()
        e.obj = MACRO.get(id)
        e.args = args[1:]
        raise e

    def find_throwed_uncert(e):
        while True:
            if e is None:
                break
            if isinstance(e, MACRO.Uncert):
                break
            e = e.__context__
        return e


def _gc(el, repls):
    if type(el) in [list, tuple]:
        if len(el) == 0:
            return (False, el)
        res = [_gc(e, repls) for e in el]
        if not max(e[0] for e in res):
            return (False, el)
        res = [e[1] for e in res]
        if type(el) == tuple:
            res = tuple(res)
        return (True, res)
    if not isinstance(el, E):
        return (False, el)
    if el.t != 'f':
        return (False, el)
    if len(el.args) == 0:
        return (False, el)
    if el.v == '`apply':
        for e in repls:
            if e[2][0] == el[0]:
                e[0] = True
                print('Use =>', el)
        return (False, el)
    if el.v == ';':
        # [use? gced? repl]
        isChange = False
        subrepls = [[False, False, e] for e in el[:-1]]
        (c, resE) = _gc(el[-1], repls + subrepls)
        if c:
            isChange = True
        isDo = True
        while isDo:
            isDo = False
            for i in range(len(subrepls) - 1, -1, -1):
                if not subrepls[i][0] or subrepls[i][1]:
                    continue
                isDo = True
                (c, res) = _gc(subrepls[i][2][2], repls + subrepls[:i])
                if c:
                    subrepls[i][2] = E.func(
                        '`repl',
                        subrepls[i][2][:2] + [res] + subrepls[i][2][3:]
                    )
                    isChange = True
                subrepls[i][1] = True
        nsubrepls = [e[2] for e in subrepls if e[0]]
        if len(nsubrepls) != len(subrepls):
            isChange = True
        if not isChange:
            return (False, el)
        return (True, E.func(
            ';',
            nsubrepls + [resE]
        ))
    args = [_gc(e, repls) for e in el.args]
    if el.v == '`pipely' and args[0][1].isFunc('`apply'):
        return (True, E.func(
            '`apply',
            [args[0][1][0]] + [e[1] for e in args[1:]]
        ))
    if not max(e[0] for e in args):
        return (False, el)
    return (True, E.func(
        el.v,
        [e[1] for e in args])
    )


def consty(s):
    (c, s) = _walk(s, [])
    if c:
        s = _run((c, s), [])
    (c, s) = _gc(s, [])
    if c:
        print('GCed')
    else:
        print('no GCed')
    return s
