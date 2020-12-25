from tree import E
from importlib import util
from os import path


class PbError(Exception):
    pass


class PbTranslatorError(PbError):
    pass


class PbCodeHelper(PbError):
    def __init__(self, cd):
        cds = cd.split('\n')
        self.cd = '<generated file\n%s\n>' % '\n'.join(
                '%4d | %s' % (i+1, cds[i])
                for i in range(len(cds))
        )

    def __str__(self):
        return self.cd


def cody(e, t, f, n=None):
    cache = {}

    def load(t, p):
        p = path.sep.join(p)
        if p in cache:
            return cache[p]
        if t == 'py':
            g = loadPy(p)
        elif t == 'gn':
            g = loadGn(p)
        else:
            raise PbTranslatorError('Unknown gen type <%s>' % t)
        cache[p] = g
        return g

    def loadPy(p):
        s = util.spec_from_file_location("some_case", p)
        if s is None:
            raise PbTranslatorError('Wrong gen file <%s>' % p)
        m = util.module_from_spec(s)
        try:
            s.loader.exec_module(m)
        except Exception:
            raise PbTranslatorError('Exception while load gen file <%s>' % p)
        if 'case' not in m.__dict__:
            raise PbTranslatorError(
                'Gen file do not contains function `case(el, cody, gen)` <%s>'
                % p
            )
        return m.case

    def loadGn(p):
        if not path.isfile(p):
            raise PbTranslatorError('No gen file <%s>' % p)
        try:
            with open(p, 'r', encoding='utf8') as f:
                s = f.readlines()
        except Exception:
            raise PbTranslatorError(
                'Cannot read gen file <%s> (utf8 required)'
                % p
            )
        i = -1
        parts = []
        while True:
            i += 1
            if i == len(s):
                break
            if s[i][0:3] == '# \\':
                continue
            if s[i][0:5] == '# > \\' or s[i][0:5] == '# < \\':
                cd = []
                for j in s[i+1:]:
                    if j[0:3] == '# \\':
                        break
                    cd.append(j[:-1])
                parts.append((s[i][2], i, '\n'.join(cd)))
                i += len(cd) + 1
            if s[i][0:3] == '# >' or s[i][0:3] == '# <':
                parts.append((s[i][2], i, s[i][3:-1]))
        cd = []
        for i in range(0, len(parts), 2):
            (si, ni, cdi) = parts[i]
            if len(parts) == i+1:
                raise PbTranslatorError(
                    'Unexpected end of gen file <%s>' % p
                )
            (so, no, cdo) = parts[i+1]
            if si != '>':
                raise PbTranslatorError(
                    'Part on <%s:%d> must be contidion'
                    % (p, ni + 1)
                )
            if so != '<':
                raise PbTranslatorError(
                    'Part on <%s:%d> must be template'
                    % (p, no + 1)
                )
            cdo = cdo.strip().replace('\\', '\\\\').split('#%')
            for j in range(1, len(cdo), 2):
                if j == len(cdo) - 1:
                    raise PbTranslatorError(
                        'Template on <%s:%d> has unclosed inserts'
                        % (p, no + 1)
                    )
                cdo[j] = '""" + (%s) + """' % cdo[j]
            cd += [
                'if (%s):' % cdi,
                '\treturn """%s"""' % ''.join(cdo)
            ]
        cd = 'def case(e, r, g):\n%s\n' % '\n'.join('\t' + s for s in cd)
        return loadPyCode(p, cd)

    class PbGen(PbError):
        def __init__(self, r):
            self.r = r

    def loadPyCode(p, cd):
        m = {}
        try:
            exec(cd, m)
        except Exception:
            try:
                raise PbTranslatorError('Error in compiled template <%s>' % p)
            except Exception:
                raise PbCodeHelper(cd)

        def wrap(e, r, g):
            try:
                return m['case'](e, r, g)
            except PbError as e:
                raise e
            except Exception:
                raise PbCodeHelper(cd)
        return wrap

    def gen(ps, e, t, f):
        ps = ps + f.split('/')[:-1]
        f = f.split('/')[-1]
        m = load(t, ps + [f])
        try:
            r = m(e, rec, lambda t, f: gen(ps, e, t, f))
        except PbError as e:
            raise e
        except Exception:
            raise PbTranslatorError(
                'Error while apply gen file <%s>'
                % '/'.join(ps + [f])
            )
        if r is not None:
            raise PbGen(r)

    def wrap(e, r, g):
        if type(e) != E:
            raise PbTranslatorError('Tree error: unknown %s' % str(e))
        g(t, f)
        raise PbTranslatorError('Tree error: unmathed %s' % str(e))

    def rec(e):
        try:
            r = wrap(e, rec, lambda t, f: gen([], e, t, f))
        except PbGen as e:
            return e.r
        return r

    if n is None:
        n = '_main'
    e = E.func('`codywrap', [e, n])
    return rec(e)


class Unclosure:
    def bind(el, faker=None):
        if faker is None:
            faker = E.Fake()
        repls = []
        r = Unclosure._bind(el, [], repls, faker)
        if len(repls) > 0:
            return E.func(';', repls + [r])
        else:
            return r

    def _bind(el, vars, repls, faker):
        if type(el) == list:
            return [Unclosure._bind(e, vars, repls, faker) for e in el]
        if type(el) != E or el.t != 'f':
            return el
        if el.v == '≺':
            return el
        if el.v == '`repl':
            subvars = el[1]
            r = Unclosure._bind(el[2], subvars, repls, faker)
            repl = E.func('`repl', [el[0], subvars, r] + el[3:])
            return repl
        if el.v == ';':
            args = el.args[:]
            i = -1
            while True:
                i += 1
                if i == len(args):
                    break
                subrepls = []
                r = Unclosure._bind(args[i], vars, subrepls, faker)
                args = args[:i] + subrepls + [r] + args[i+1:]
                i += len(subrepls)
            repl = E.func('`repl', [
                faker.fake(),
                vars,
                E.func(';', args)
            ])
            repls.append(repl)
            apply = E.func('`apply', [repl[0]] + [
                E.func('`apply', [var])
                for var in vars
            ])
            return apply
        if el.v == '`pipely':
            n = faker.fake()
            return Unclosure._bind(
                E.func(';', [
                    E.func('`repl', [
                        n,
                        [],
                        el[0]
                    ]),
                    E.func('`apply', [
                        n
                    ] + el[1:])
                ]),
                vars, repls, faker
            )
        if el.v in ['`series', '`matrix', '`inject']:
            nf = faker.fake()
            ns = faker.fake()
            subvars = vars[:]
            if el.v == '`series':
                if isinstance(el[2], E):
                    subvars += [el[2]]
                elif type(el[2]) in [list, tuple]:
                    subvars += el[2]
                else:
                    raise Exception('Wrong series vars ' + str(el))
            repl = E.func('`repl', [
                nf,
                vars,
                E.func(';', [
                    E.func('`repl', [
                        ns,
                        [],
                        E.func(el.v, [
                            Unclosure._bind(e, subvars, repls, faker)
                            for e in el.args
                        ])
                    ]),
                    E.func('`apply', [ns])
                ])
            ])
            repls.append(repl)
            apply = E.func('`apply', [nf] + [
                E.func('`apply', [var])
                for var in vars
            ])
            return apply
        return E.func(el.v, [
            Unclosure._bind(e, vars, repls, faker)
            for e in el.args
        ])


def execute(cd):
    m = {}
    try:
        exec(cd, m)
    except Exception:
        raise PbCodeHelper(cd)
    g = m.pop('_main')

    def wrap():
        try:
            r = g()
        except Exception:
            raise PbCodeHelper(cd)
        return r
    return wrap
