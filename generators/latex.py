def case(el, cody, gen):
    def cd(e):
        try: return cody(e)
        except: return '<compile error: %s>' % str(e)
    if el.t == 'string':
        return '\\text{%s}' % el.v
    if el.t != 'f':
        return gen('py', './all.py')
    v = {
        '→': ' \\to ',
        '≤': ' \\leq ',
        '≥': ' \\geq ',
        '`in': ' \\in ',
        '|': ' \\mid '
    }.get(el.v)
    if v is None and el.v in ['^', ';', ',']:
        v = el.v
    if v is not None:
        return '(%s)' % v.join(cd(e) for e in el.args)
    gen('py', './all.py')
    e = type(el)()
    e.t = 'const'
    e.v = el.v
    return cd(type(el).func('`apply', [e] + el.args))
