from tree import E


class R:
    def create(s):
        e = E()
        e.t = 'string'
        e.v = s
        f = E()
        f.t = 'const'
        f.v = '?'
        return E.func('`apply', [f, e])

    def iff(e):
        return (
            E.isFunc(e, '`apply')
            and e[0].t == 'const'
            and e[0].v == '?'
            and e[1].t == 'string'
        )


def eject(eqn, src, data):
    if R.iff(src):
        if src[1].v in data:
            raise Exception('Multiple template <%s> in src' % src[1].v)
        data[src[1].v] = eqn
        return True
    if (
        type(eqn) != E
        or type(src) != E
        or eqn.t != 'f'
        or src.t != 'f'
    ):
        return eqn == src
    if len(eqn) != len(src) or eqn.v != src.v:
        return False
    return len([
        0 for i in range(len(eqn)) if not eject(eqn[i], src[i], data)
    ]) == 0


def inject(dst, data):
    if R.iff(dst):
        if dst[1].v not in data:
            raise Exception('No template <%s> in dst' % dst[1].v)
        return data[dst[1].v]
    if (type(dst) != E or dst.t != 'f'):
        return dst
    return E.func(dst.v, [inject(e, data) for e in dst.args])


def _apply(eqn, src, dst, isRec):
    data = {}
    r = eject(eqn, src, data)
    if r:
        if isRec:
            for k in data:
                data[k] = _apply(data[k], src, dst, isRec)
        d = dst(data)
        if d is None:
            if not isRec:
                return eqn
        else:
            return d
    if (
        type(eqn) != E
        or eqn.t != 'f'
    ):
        return eqn
    return E.func(eqn.v, [_apply(e, src, dst, isRec) for e in eqn.args])


def apply(eqn, src, dst, isRec=True):
    if isinstance(dst, type(lambda: 0)):
        dstf = dst
    elif isinstance(dst, E):
        def dstf(data): return inject(dst, data)
    else:
        raise Exception('dst must be tree or function')
    eqn = _apply(eqn, src, dstf, isRec)
    return E.squeeze(eqn)
