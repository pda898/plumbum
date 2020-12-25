def case(el, cody, gen):
    if el.t == 'fake':
        return '_f%d' % el.v
    if el.t == 'string':
        return '"%s"' % el.v
    if el.t == 'zero':
        return '0'
    if el.t == 'number':
        return el.v
    if el.t == 'const':
        if el.v[0] == '\\':
            return 'slash_' + el.v[1:]
        if el.v == '*':
            return '_'
        return el.v
    if el.t != 'f':
        return '<is not name %s>' % el
    if el.v == '`join':
        return ''.join([cody(e) for e in el.args])
    if el.v == 'msub':
        return '%s_%s' % (cody(el[0]), cody(el[1]))
    if el.v == '`apply':
        if el[0].v in type(el).OPERATORS:
            return None
        if len(el) == 1:
            return cody(el[0])
        else:
            return '%s(%s)' % (
                cody(el[0]),
                ','.join([cody(e) for e in el[1:]])
            )
    v = {
        '≤': '<=',
        '≥': '>=',
        '=': '=='
    }.get(el.v, el.v)
    if v in ['+', '-', '*', '/', '<', '>', '<=', '>=', '==']:
        return '(%s)' % v.join(cody(e) for e in el.args)
    if el.v == '`repl':
        if len(el.args) == 4:
            raise Exception('<tree error: %s>' % (
                str(el[3])
            ))
