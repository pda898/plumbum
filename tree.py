from latex2mathml.converter import convert as latex2xml
from xml.etree import ElementTree as XML


class E:
    OPERATORS = ['∂', '∞', '⊧', '←', '⊗', '≺', '⏞', '?', '⊤', '⊥', '≻']

    class Fake:
        def __init__(s):
            s.n = 0

        def fake(s):
            e = E()
            e.t = 'fake'
            e.v = s.n
            s.n += 1
            return e

    def func(v, args=None):
        args = [] if args is None else args
        e = E()
        e.t = 'f'
        e.v = v
        e.args = args
        return e

    def isFunc(el, v):
        return type(el) == E and el.t == 'f' and el.v == v

    def err(msg):
        e = E()
        e.t = 'string'
        e.v = str(msg)
        return E.func('`err', [e])

    def isErr(el):
        return el.t == 'f' and el.v == '`err'

    def zero():
        e = E()
        e.t = 'zero'
        return e

    def __parseXMLmrow(els):
        ia = 0
        ib = -1
        while True:
            ia = [
                i
                for i in range(len(els))
                if i > ib and type(els[i]) != E and els[i] == '('
            ]
            if len(ia) == 0:
                break
            ia = ia[0]
            k = 0
            ib = None
            for i in range(len(els)):
                if i <= ia:
                    continue
                if type(els[i]) == E:
                    continue
                if els[i] == '(':
                    k += 1
                if els[i] == ')':
                    if k > 0:
                        k -= 1
                    else:
                        ib = i
                        break
            if ib is None:
                ib = len(els)
            e = E.func('(', [E.__parseXMLmrow(els[ia+1:ib])])
            els = els[:ia] + [e] + els[ib+1:]
            ib = ia
        ia = 0
        ib = -1
        while True:
            ia = [i for i in range(len(els)) if type(els[i]) == E and i > ib]
            if len(ia) == 0:
                break
            ia = ia[0]
            ib = [i for i in range(len(els)) if type(els[i]) != E and i > ia]
            if len(ib) == 0:
                ib = len(els)
            else:
                ib = ib[0]
            e = E.func('`join', els[ia:ib])
            els = els[:ia] + [e] + els[ib:]
            ib = ia
        for o in [
            ['^', '.'], ['*', '/'], ['+', '-'],
            ['→', '<', '>', '≤', '≥', '≡'],
            ['`in'], ['='],
            ['∨', '∧'],
            ['⊢'], [':'],
            [';'], [','], ['|']
                ]:
            i = -1
            while True:
                i += 1
                if i >= len(els):
                    break
                if type(els[i]) == E:
                    continue
                if els[i] not in o:
                    continue
                if i-1 > 0:
                    nels = els[:i-1]
                else:
                    nels = []
                if i-1 < 0 or type(els[i-1]) != E:
                    e1 = E.err('no left')
                    nels += els[i-1:i]
                    di = False
                else:
                    e1 = els[i-1]
                    di = True
                ii = len(nels)
                nels += [None]
                if i+1 >= len(els) or type(els[i+1]) != E:
                    e2 = E.err('no right')
                    nels += els[i+1:i+2]
                else:
                    e2 = els[i+1]
                nels += els[i+2:]
                nels[ii] = E.func(els[i], [e1, e2])
                els = nels
                if di:
                    i -= 1
                continue
        if len(els) == 0:
            return E.err('empty line')
        if (
            [type(e) for e in els] in [[str, str], [str, E, str]]
            and els[0] in ['{', '`None', '‖', '[']
            and els[-1] in ['}', '`None', '‖', ']']
        ):
            e = E()
            e.t = 'string'
            e.v = '+'.join([els[0], els[-1]])
            els = [E.func(
                '`raml',
                [e, els[1]] if len(els) == 3 else [e]
            )]
        if len(els) > 1:
            return E.err('many %s' % '\n'.join('<%s>' % str(e) for e in els))
        return els[0]

    def __fixLaTeXcases(s):

        def mfinder(s, p, d):
            [ss, sf, m] = p
            a = s.rfind(ss)
            if a < 0:
                return None
            b = s.find(sf, a + 1)
            if b < 0:
                raise Exception('unclosed cases %s %s' % (ss, sf))
            if b < a:
                raise Exception('%s before %s' % (sf, ss))
            return s[:a] + bfinder(s[a+len(ss):b], d, m) + s[b+len(sf):]

        def bfinder(s, d, m=None):
            for p in d:
                while True:
                    sn = mfinder(s, p, d)
                    if sn is None:
                        break
                    s = sn
            if m is not None:
                s = m(s)
            return s

        def hr_cases(s):
            s = s.replace('&', '').replace('\\\\', '),(')
            s = '\\cases((%s))' % s
            return s

        def hr_text(s):
            s = ''.join('%03d' % e for e in s.encode('utf8'))
            return '\\text(%s)' % s

        def hr_matrix(s):
            s = s.replace('&', '),(').replace('\\\\', '),\\mtxl,(')
            s = '\\mtx((%s))' % s
            return s

        def hr_overbrace(s):
            return '\\overbrace(%s)' % s

        s = bfinder(s, [
            ['\\text{', '}', hr_text],
            ['\\overbrace{', '}', hr_overbrace],
            ['\\begin{cases}', '\\end{cases}', hr_cases],
            ['\\begin{pmatrix}', '\\end{pmatrix}', hr_matrix]
        ])
        s = s.replace('^', ' \\fixmsup ').replace('\\\\', ' ')
        return s

    def fromXML(el):
        t = el.tag.split('}')[1]
        if t == 'math':
            return [E.fromXML(e) for e in el][0]
        if t == 'mi':
            r = {
                ',': ',',
                ';': ';',
                '⩽': '≤',  # \leqslant
                '⩾': '≥',  # \geqslant
                '\\fixmsup': '^',
                '|': '|',
                ':': ':',
                '.': '.'
            }.get(el.text, None)
            if r is not None:
                return r
            e = E()
            e.t = 'const'
            e.v = el.text
            return e
        if t == 'mn':
            e = E()
            e.t = 'number'
            e.v = el.text
            return e
        if t == 'mo':
            r = {
                '−': '-',  # thats two different symbols :)
                '∈': '`in',  # э inverted :0
                '∣': '|',
                '⋅': '*',  # \cdot
                None: '`None'
            }.get(el.text)
            if r is not None:
                return r
            if el.text in E.OPERATORS:
                e = E()
                e.t = 'const'
                e.v = el.text
                return e
            return el.text
        if t == 'mrow':
            els = list(el)
            els = [E.fromXML(e) for e in el]
            return E.__parseXMLmrow(els)
        return E.func(t, [E.fromXML(e) for e in el])

    def squeeze(el):
        if type(el) != E:
            # return E.err('unknown type <%s>' % str(el))
            return el
        if el.t != 'f':
            return el
        args = el.args
        if el.v in ['+', '-', '*', '/', ',', ';']:
            while True:
                commas = [e for e in args if e.t == 'f' and e.v == el.v]
                if len(commas) == 0:
                    break
                comma = commas[0]
                ci = args.index(comma)
                args = args[:ci] + comma.args + args[ci+1:]
        args = [E.squeeze(e) for e in args]
        if el.v == '-':
            if E.isErr(args[0]) and args[0][0].v == 'no left':
                args[0] = E.zero()
            if E.isErr(args[1]):
                return args[0]
        if el.v == '(':
            if (
                len(args) == 1
                and E.isErr(args[0])
                and args[0][0].v == 'empty line'
            ):
                el.args = []
                return el
        if (
            el.v == '*'
            and len(el) == 2
            and E.isErr(el[0])
            and E.isErr(el[1])
            and el[0][0].v == 'no left'
            and el[1][0].v == 'no right'
        ):
            el.t = 'const'
            el.__dict__.pop('args')
            return el
        if el.v == '`join':
            if len(args) == 1:
                return args[0]

            def crit(i):
                if args[i].t == 'number':
                    return True
                if args[i].t != 'f':
                    return False
                if args[i].v == '(' and i == 0:
                    return True
                if args[i].v == '`apply':
                    return True

            i = [i for i in range(len(args)) if crit(i)]
            if len(i) != 0:
                i = i[0]
                em = E.func('*')
                e = E.func('`join', args[:i])
                if len(e.args) > 0:
                    em.args.append(e)
                if args[i].t == 'f' and args[i].v == '(':
                    em.args.append(args[i][0])
                else:
                    em.args.append(args[i])
                e = E.func('`join', args[i+1:])
                if len(e.args) > 0:
                    em.args.append(e)
                return E.squeeze(em)
        else:
            for i in range(len(args)):
                if E.isFunc(args[i], '('):
                    if len(args[i].args) == 0:
                        args[i] = None
                    elif len(args[i].args) == 1:
                        args[i] = args[i][0]
                    else:
                        args[i] = E.err('many <%s>' % str(args[i]))
            args = [e for e in args if e is not None]
        el.args = args
        return el

    def appfunc(el, fname):
        if type(fname) in [type([]), type(())]:
            for f in fname:
                el = E.appfunc(el, f)
            return el
        if fname.__dict__.get('isQ') is None:
            def crit():
                if fname.t != 'f':
                    return False
                if fname.v != '`join':
                    return False
                if fname[-1].t != 'f':
                    return False
                if fname[-1].v != '(':
                    return False
                return len(fname[-1].args) == 0
            fname.isQ = crit()
            if fname.isQ:
                fname.args = fname[:-1]
            el = E.appfunc(el, fname)
            return E.squeeze(el)
        if el == fname:
            return E.func('`apply', [el])
        if el.t != 'f':
            return el
        if el.v != '`join':
            el.args = [E.appfunc(e, fname) for e in el.args]
            return el
        ii = []
        for i in range(len(el.args)):
            if i >= len(el.args):
                break
            if el[i] == fname:
                ii.append(i)
                continue
            if fname.t != 'f' or fname.v != '`join':
                continue
            if el[i:i+len(fname.args)] == fname.args:
                e = E.func('`join', fname.args)
                el.args = el[:i] + [e] + el[i+len(fname.args):]
                ii.append(i)
                continue
        for i in range(len(el.args)):
            if i in ii:
                continue
            el[i] = E.appfunc(el[i], fname)
        for i in ii:
            if (
                not fname.isQ
                or i+1 >= len(el.args)
                or el[i+1].t != 'f'
                or el[i+1].v != '('
            ):
                el[i] = E.appfunc(el[i], fname)
                continue
            while (
                el[i+1].t == 'f'
                and el[i+1].v in ['(', ',']
                and len(el[i+1].args) == 1
            ):
                el[i+1] = el[i+1][0]
            e = E.func('`apply', [el[i]])
            if el[i+1].t == 'f' and el[i+1].v == ',':
                e.args += el[i+1].args
            else:
                e.args += [el[i+1]]
            el[i] = e
            el[i+1] = None
        el.args = [e for e in el.args if e is not None]
        return el

    def __varfunc(el):
        if type(el) != E:
            return (False, [])
        if el.t == 'number':
            return (True, [])
        if el.t == 'const':
            return (True, [el])
        if el.t != 'f':
            return (False, [])
        args = [E.__varfunc(e) for e in el.args]
        if el.v in ['`join', 'msub']:
            if min([e[0] for e in args]):
                return (True, [el])

        def join(arr):
            res = []
            [[res.append(e) for e in r[1] if e not in res] for r in arr]
            return res

        if el.v == '`apply':
            args = args[1:]
        if el.v != '`join':
            return (False, join(args))
        j = -1
        parts = []
        while True:
            i = [i for i in range(len(el.args)) if i > j and args[i][0]]
            if len(i) == 0:
                break
            i = i[0]
            j = [j for j in range(len(el.args)) if j > i and not args[j][0]]
            if len(j) == 0:
                j = len(el.args)
            else:
                j = j[0]
            e = E.func('`join', el[i:j])
            e = E.squeeze(e)
            parts.append(e)
        args = [e for e in args if not e[0]]
        args.append((True, parts))
        return (False, join(args))

    def varfunc(el, fnames=None):
        fnames = [] if fnames is None else fnames
        el = E.appfunc(el, fnames)
        finded = []
        while True:
            _, els = E.__varfunc(el)
            if len(els) == 0:
                break
            res = []
            for e in els:
                nods = [e.nod(a) for a in els if a != e]
                # TODO handle multi nods?
                nods = [a[0] for a in nods if len(a) > 0]
                nods = [a for a in nods if len([
                    b for b in nods if b != a and b in a
                ]) == 0]
                if len(nods) == 0:
                    res.append(e)
                    continue
                [res.append(a) for a in nods if a not in res]
            els = res
            for a in els:
                a.isQ = True
            el = E.appfunc(el, els)
            el = E.squeeze(el)
            finded += els
        return (el, finded)

    def handle_righted(el):
        if type(el) != E:
            return el
        if el.t != 'f':
            return el
        if el.__dict__.get('wantR'):
            return el
        if el.v in ['msubsup', 'munder']:
            if len(el.args) < 1:
                return E.err('args %s' % str(el.args))
            fn = el[0]
            if type(fn) == E:
                if fn.t == 'const':
                    fn = fn.v
                else:
                    return E.err('func <%s>' % str(fn))
            else:
                fn = str(fn)
            if fn not in ['∫', '∑', '∏', 'lim']:
                return E.err('func <%s>' % fn)
            e = E.func(fn, [E.handle_righted(e) for e in el[1:]])
            e.wantR = True
            return e
        el.args = [E.handle_righted(e) for e in el.args]
        if el.v == '`join':
            while True:
                i = [
                    len(el.args)-i-1
                    for i in range(len(el.args))
                    if el[len(el.args)-i-1].__dict__.get('wantR')
                ]
                if len(i) == 0:
                    break
                i = i[0]
                el[i].__dict__.pop('wantR')
                le = 4 if el[i].v in ['∫'] else 2
                args = el[i:i+le]
                if len(args) != le:
                    el[i] = E.err('wrong <%s>' % str(el[i]))
                    continue
                if le == 4:
                    dd = args[2]
                    if type(dd) == E:
                        if dd.t == 'const':
                            dd = dd.v
                        else:
                            el[i] = E.err('wrong dd <%s> for <%s>' % (
                                str(dd), str(args[0]))
                            )
                            continue
                    else:
                        dd = str(dd)
                    if dd not in ['d']:
                        el[i] = E.err('wrong dd <%s> for <%s>' % (
                            dd, str(args[0])
                        ))
                    args[0].args.append(args[3])
                args[0].args.append(args[1])
                el.args = el[:i+1] + el[i+le:]
        return el

    def freed(el, repls=None):
        repls = [] if repls is None else repls
        if type(el) != E:
            return []
        if el.t == 'const':
            if el.v in E.OPERATORS:
                return []
            elif el in [e[0] for e in repls]:
                return []
            else:
                return [el]
        if el.t == 'number':
            return []
        if el.t != 'f':
            return []
        if el.v == 'mfrac':
            el.v = '/'
            return E.freed(el, repls)
        if el.v == '`join':
            if (
                len(el) == 2
                and E.isFunc(el[1], '(')
            ):
                el.v = '`apply'
                if E.isFunc(el[1][0], ','):
                    el[1].args = el[1][0].args
                el.args = el[:1] + el[1].args
            elif el in [e[0] for e in repls]:
                return []
            else:
                return [el]
        args = el.args

        def gerr(el, msg):
            repls.append(E.func('`repl', [None, [], el, E.err(msg)]))

        if el.v == '=':
            expl = []
            subvars = [E.freed(e, repls) for e in args]
            for i in range(len(args)):
                if args[i].t != 'f':
                    continue
                if args[i].v != '`apply':
                    continue
                if args[i][0].v != '*' and args[i][0] in [e[0] for e in repls]:
                    continue
                if len([
                    e for e in args[i][1:]
                    if e.t != 'f' or e.v != '`apply' or len(e.args) != 1
                ]) > 0:
                    continue
                expl.append(i)
            impl = [i for i in range(len(args)) if i not in expl]
            expl = [
                i for i in expl
                if len([
                    j for j in impl
                    if args[i][0] in subvars[j]
                ]) == 0
            ]
            if len(expl) > 1:
                expl = expl[:1]
                # gerr(el, 'many explicit')
                # return []
            if len(expl) > 0:
                if len(args) > 2:
                    gerr(el, 'many explicit')
                    return []
                i = expl[0]
                expl = args[i]
                impl = args[1 - i]
                subvars = subvars[1 - i]
                vars = [e[0] for e in expl[1:]]
                subvars = [e for e in subvars if e not in vars]
                repls.append(E.func('`repl', [expl[0], vars, impl]))
                return subvars
            res = []
            [
                [res.append(e) for e in subvar if e not in res]
                for subvar in subvars
            ]
            if len(res) == 0:
                gerr(el, 'malformed')
                return []
            repls.append(E.func('`repl', [res[0], [], el]))
            return res[1:]
        if el.v == ';':
            subrepls = repls[:]
            res = []
            lr = len(subrepls)
            vars = []
            for i in range(len(el.args)):
                subvars = E.freed(el[i], subrepls)
                if len(subrepls) > lr:
                    res += subrepls[lr:]
                    lr = len(subrepls)
                    if i+1 == len(el.args):
                        res.append(E.err('no return'))
                else:
                    if i+1 == len(el.args):
                        res.append(el[i])
                    else:
                        res.append(E.err('unused <%s>' % el[i]))
                [vars.append(e) for e in subvars if e not in vars]
            el.args = res
            return vars
        if el.v == '`apply' and el[0].v == '\\cases':
            el.v = '`cases'
            el.args = el[1:]
            subs = []  # rec items (a = b)
            cases = []  # case items (a, b)
            for i in range(len(el.args)):
                if el[i].t != 'f':
                    continue
                if el[i].v == ',':
                    if len(el[i].args) != 2:
                        continue
                    cases.append(i)
                    continue
                if el[i].v == '=':  # a = b = c
                    if len(el[i].args) != 2:  # a = b
                        continue
                    res = []
                    for j in range(len(el[i].args)):
                        if not E.isFunc(el[i][j], 'msub'):
                            continue
                        if not E.isFunc(el[i][j][0], '`apply'):
                            continue
                        if not E.isFunc(el[i][j][1], ','):
                            el[i][j][1] = E.func(',', [el[i][j][1]])
                        E.freed(el[i][j][1], repls)  # TODO should we use that?
                        sucs = True
                        for e in el[i][j][1].args:
                            if E.isFunc(e, '`apply') and len(e.args) == 1:
                                continue
                            if e.t in ['number', 'string']:
                                continue
                            sucs = False
                            break
                        if sucs:
                            res.append(j)
                    if len(res) == 0:
                        continue
                    res = res[0]
                    el[i].args = [el[i][res]] + el[i][:res] + el[i][res+1:]
                    E.freed(el[i][0][1], [])
                    subs.append(i)
            if len(subs) > 0 and len(cases) > 0:
                gerr(el, 'Cases or rec?')
                return []
            oth = [i for i in range(len(el.args)) if i not in subs + cases]
            if len(oth) > 1 or (len(oth) == 1 and oth[0] != len(el.args) - 1):
                gerr(el, 'unexpected <%s>' % str(el[oth[0]]))
                return []
            if len(cases) > 0 and cases[-1] == len(el.args) - 1:
                el[-1] = el[-1][0]
            if len(subs) > 0 and subs[-1] == len(el.args) - 1:
                el.args.append(E.err('use return from rec creator'))
            if len(subs) > 0:
                res = {}
                for e in el[:-1]:
                    fn = e[0][0][0]  # rec name
                    if fn not in res:
                        res[fn] = {'name': fn, 'one': [], 'rec': []}
                    f = res[fn]
                    recargs = [
                        a[0] for a in e[0][1].args
                        if E.isFunc(a, '`apply') and len(a.args) == 1
                    ]
                    bindargs = [
                        a for a in e[0][1].args
                        if a.t in ['number', 'string']
                    ]
                    if len(recargs) != 0 and len(bindargs) != 0:
                        gerr(el, 'use cases for half-binded args')
                        return []
                    if len(recargs) > 0:
                        f['rec'].append((
                            recargs, e[1]
                        ))
                    if len(bindargs) > 0:
                        f['one'].append((
                            bindargs, e[1]
                        ))
                for f in res:
                    if len(res[f]['rec']) == 0:
                        gerr(el, 'no definition for <%s>' % str(f))
                        return []
                    if len(res[f]['rec']) > 1:
                        gerr(el, 'multi definition for <%s>' % str(f))
                        return []
                    res[f]['rec'] = res[f]['rec'][0]
                    if len(res[f]['one']) == 0:
                        pass
                        # TODO thats need?
                        # gerr(el, 'no start point for <%s>' % str(f))
                        # return []
                    res[f]['obj'] = E.func('`series', [
                        'recN',
                        res[f]['one'],
                        res[f]['rec'][0],
                        E.err('some error'), None
                    ])
                    repl = E.func('`repl', [
                        f,
                        [],
                        res[f]['obj']
                    ])
                    if repl[0] in [e[0] for e in repls]:
                        gerr(el, 'redefinition <%s>' % str(repl[0]))
                        return []
                    repls.append(repl)
                vars = []
                for f in res:
                    for (_, e) in res[f]['one']:
                        subvars = E.freed(e, repls)
                        [vars.append(e) for e in subvars if e not in vars]
                    fnb = res[f]['rec'][1]
                    subvars = E.freed(fnb, repls)
                    [
                        vars.append(e)
                        for e in subvars
                        if e not in vars + res[f]['rec'][0]
                    ]
                    res[f]['obj'][3] = fnb
                el.args = el[-1:]
                return vars
            args = el.args
        if el.v == '`apply' and el[0].v == '\\text':
            if (
                len(el) == 1
                or el[1].t != 'number'
                or (len(el[1].v) % 3) != 0
            ):
                gerr(el, 'use like \\text{...} please')
                return []
            s = el[1].v
            s = bytes(
                int(s[i:i+3]) for i in range(0, len(s), 3)
            ).decode('utf8')
            el.t = 'string'
            el.v = s
            el.__dict__.pop('args')
            return []
        if el.v == '`apply' and el[0].v == '\\inject':
            [E.freed(e, repls) for e in el.args]
            if (
                len(el) != 2
                or el[1].t != 'string'
            ):
                gerr(el, 'use like \\inject(\\text{...}) please')
                return []
            el.v = '`inject'
            el.args = [el[1]]
            return []
        if el.v == '`apply' and el[0].v == '\\mtx':
            rs = 1
            cs = -1
            cp = 0
            el.args = [
                None if (
                    E.isFunc(e, '`apply')
                    and e[0].t == 'const'
                    and e[0].v == '\\mtxl'
                ) else e for e in el.args
            ]
            el.args.append(None)
            for i in range(1, len(el.args)):
                if el[i] is None:
                    lcs = i - cp - 1
                    if cs == -1:
                        cs = lcs
                    else:
                        if cs != lcs:
                            gerr(el, 'unexpected row with %d els' % lcs)
                            return []
                    rs += 1
                    cp = i
                    continue
            if cs == -1:
                cs = len(el.args) - 1
            rs -= 1
            el.v = '`matrix'
            el.args = [[cs, rs]] + [e for e in el[1:] if e is not None]
            args = el.args
        if el.v == '`apply' and el[0].v == '≺':
            el.v = el[0].v
            el.args = el.args[1:]
            subrepls = repls[:]
            subvars = [E.freed(e, subrepls) for e in el.args]
            el.args = [subvars, subrepls[len(repls):]] + el.args
            return []
        if el.v == '`apply' and el[0].v == '≻':
            el.v = el[0].v
            el.args[0] = str(id(el))  # TODO unique?
        if el.v == '|':
            if len(el) != 2:
                gerr(el, 'syntax series')
                return []
            if E.isFunc(el[1], '`in'):
                el[1] = E.func(',', [el[1]])
            if E.isFunc(el[1], ','):
                if len([e for e in el[1].args if not E.isFunc(e, '`in')]) > 0:
                    gerr(el, 'expected a \\in b')
                    return []
                ser = [e[1] for e in el[1].args]
                var = [e[0] for e in el[1].args]
                pred = el[0]
                tp = 'mapN'
            else:
                pred = el[1]
                tp = 'genN'
                if E.isFunc(el[0], '`in'):
                    ser = [el[0][1]]
                    var = [el[0][0]]
                else:
                    var = [el[0]]
                    ser = [None]
            if len([
                e for e in var
                if not E.isFunc(e, '`apply') or len(e) > 1
            ]) > 0:
                gerr(el, 'wrong var in series')
                return []
            # TODO handle shuffle like a_{j,i} = a_{i,j}
            var = [e[0] for e in var]
            vars = [e for e in E.freed(pred, repls) if e not in var]
            [
                [
                    vars.append(a)
                    for a in E.freed(e, repls)
                    if a not in vars
                ]
                for e in ser
                if e is not None
            ]
            if len([e for e in var if e in vars]) > 0:
                gerr(el, 'var in base series term')
                return []
            el.v = '`series'
            if tp == 'genN':
                ser = ser[0]
                var = var[0]
            el.args = [tp, [], E.err('series not in {}'), var, pred, ser]
            return vars
        if el.v == 'msub':
            if (
                len([
                    e for e in repls
                    if el == e[0]
                ]) > 0
            ):
                return []
            elif (
                E.isFunc(el[0], '`apply')
                and len(el[0].args) == 1
                and (el[0][0].v == '←' or el[0][0] in [e[0] for e in repls])
            ):
                if E.isFunc(el[1], ','):
                    el.args = el[:1] + el[1][:]
                el.v = '`apply'
                el[0] = el[0][0]
            else:
                cp = E.func('msub', el.args)
                el.v = '`apply'
                el.args = [cp]
                return [cp]
        if el.v == '.' and len(el) == 2:
            el.v = '`pipely'
            if E.isFunc(el[1], ','):
                el.args = el[:1] + el[1].args
            args = el.args
        if el.v == '`raml' and el[0].v == '‖+‖':
            el.args = el[1:]
            el.v = '‖'
            return E.freed(el, repls)
        if el.v == '`raml' and el[0].v == '[+]' and len(el.args) == 2:
            el.v = el[1].v
            el.args = el[1].args
            return E.freed(el, repls)
        subvars = [E.freed(e, repls) for e in args]
        if el.v == '`apply':
            if E.isFunc(el[0], '`apply'):
                el.args[0] = el[0][0]
            if len(subvars[0]) == 0:
                args = args[1:]
                subvars = subvars[1:]
            else:
                return subvars[0]  # TODO ignore arguments if func name unknown
        if el.v == '`raml' and el[0].v == '{+}':
            el.args = el[1:]
            if len(el.args) == 0:
                el.args = [E.func(',', [])]
            if E.isFunc(el[0], ','):
                el.args = el[0].args
            for i in range(len(el)):
                if E.isFunc(el[i], '`series'):
                    if E.isErr(el[i][2]):
                        el[i].args = el[i][:2] + el[i][3:]
                        if i != 0 or len(el) != 1:
                            gerr(el, 'multi series in set')
                            return []
                        el.v = el[i].v
                        el.args = el[i].args
                        break
                    else:
                        el[i] = E.func('(', [el[i]])
                    continue
            if el.v == '`raml':
                el.v = '`series'
                el.args = ['arrN', [], [], el.args]
        res = []
        [[res.append(e) for e in subvar if e not in res] for subvar in subvars]
        ast = [
            i for i in range(len(el))
            if (
                E.isFunc(el[i], '`apply')
                and len(el[i]) == 1
                and el[i][0].v == '*'
            )
        ]
        if (
            el.v == '`apply'
            and len(ast) > 0
        ):
            el.v = '`args'
            aste = el[ast[0]]
            el.args = [
                None if e == aste else e
                for e in el.args
            ]
            aste = aste[0]
            res = [e for e in res if e != aste]
        return res

    def tailRec(el, recf=None):
        if recf is None:
            recf = []
        if not isinstance(el, E):
            return
        elif el.t != 'f':
            return
        elif E.isFunc(el, '`series') and el[0] == 'recN':
            return E.tailRec(el[3], [el])
        elif E.isFunc(el, ';'):
            recf.append(el)
        elif E.isFunc(el, '`repl'):
            recf = []
        elif E.isFunc(el, '`apply') and el[0].v == '←':
            el.v = el[0].v
            if (
                len(recf) == 0
                or not E.isFunc(recf[0], '`series')
                or recf[0][0] != 'recN'
                # or len(recf) > 1  # TODO no usage in ';'
            ):
                el.args[0] = E.err('Unexpected tail rec')
                return
            # el.tailRec = recf  # TODO save it?
            recf = []
            el.args = el[1:]
        [E.tailRec(e, recf) for e in el.args]

    def __getStr(self, tabs):
        if self.t == 'f':
            if tabs and len(self.args) > 1:
                return '%s(\n%s\n)' % (
                    self.v,
                    ',\n'.join(['\n'.join([
                        '\t' + l
                        for l in (
                            e.__getStr(tabs)
                            if type(e) == E
                            else str(e)
                        ).split('\n')])
                        for e in self.args
                    ])
                )
            else:
                return '%s(%s)' % (self.v, ', '.join([
                    e.__getStr(tabs) if type(e) == E else str(e)
                    for e in self.args
                ]))
        if self.t == 'const':
            return '[%s]' % self.v
        if self.t == 'number':
            return str(self.v)
        if self.t == 'string':
            return '"%s"' % self.v
        if self.t == 'zero':
            return '⓿'
        if self.t == 'fake':
            return '~%d' % self.v
        raise Exception('unknown E object')

    def __str__(self):
        return self.__getStr(True)

    def __repr__(self):
        return '<%s>' % self.__getStr(False)

    def __eq__(self, el):
        if type(el) != E:
            return False
        if el.t != self.t or el.v != self.v:
            return False
        if el.t != 'f':
            return True
        return el.args == self.args

    def __contains__(self, el):
        if type(el) != E:
            return False
        if el.t == 'number':
            return False
        if self == el:
            return True
        if self.t != 'f':
            return False
        return max([el in e for e in self.args])

    def nod(self, el):
        if type(el) != E:
            return []
        if el in self:
            return [el]
        if self in el:
            return [self]
        if self.t != 'f':
            return []
        res = []
        for e in self.args:
            res += e.nod(el)
        return res

    def __hash__(self):
        if self.t == 'f':
            return hash((self.t, self.v, tuple(hash(e) for e in self.args)))
        return hash((self.t, self.v))

    def __getitem__(self, i):
        if self.t != 'f':
            return E.err('no itemly')
        try:
            e = self.args[i]
        except IndexError:
            return E.err('no item')
        return e

    def __setitem__(self, i, el):
        self.args[i] = el

    def __len__(self):
        if self.t != 'f':
            return 0
        return len(self.args)

    def fromLaTeX(s):
        s = E.__fixLaTeXcases(s)
        s = latex2xml(s)
        # from lxml import etree
        # print(etree.tostring(
        #   etree.fromstring(s),
        #   pretty_print=True
        # ).decode('utf8'))
        s = XML.fromstring(s)
        s = E.fromXML(s)
        s = E.handle_righted(s)
        s = E.squeeze(s)
        return s

    def __call__(self, *args):
        if len(args) == 1 and isinstance(args[0], int) and self.t == 'f':
            return self.args[args[0]]
        raise Exception('Unsupported operation at tree\n%s on %s' % (
            repr(args),
            str(self)
        ))


def create(s, funcs=None):
    funcs = [] if funcs is None else funcs
    print('func >', s)
    print('-' * 20)
    s = E.fromLaTeX(s)  # latex => tree
    funcs = [E.fromLaTeX(e) for e in funcs]
    print('Needed >', funcs)  # adding vars
    s, finded = E.varfunc(s, funcs)  # add vars
    print('With vars >', s)
    if not E.isFunc(s, ';'):
        s = E.func(';', [s])
    repls = []
    res = E.freed(s, repls)
    if len(repls) > 0:
        print('--- REPLS ---')
        [print(e) for e in repls]
        raise Exception('Repls!')
    res = [
        E.func('`repl', [e, [], None, E.err('%s not found' % repr(e))])
        for e in res
        if len([f for f in funcs if e in f]) == 0
    ]
    if len(res) > 0:
        s = E.func(';', res + [s])
    E.tailRec(s)
    print('-' * 20)
    print('Afrer freed & tail >', s)
    return s
