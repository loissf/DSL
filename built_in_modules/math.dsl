function pi():
    return 3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481
end

function compt_pi(n):
    var k = 1
    var s = 0
    var sign = 1
    for i, n:
        s = s + ( sign * (4/k) )
        sign = sign * -1
        k = k + 2
    end
    return s
end

function fibonacci(n):
    var s = 0
    var s1 = 0
    var s2 = 1
    for i, n:
        s = s1 + s2
        s2 = s1
        s1 = s
    end
    return s
end

function pow(base, exponent):
    result = base
    for i, exponent-1:
        result = result * base
    end
    return result
end

function factorial(n):
    var result = 1
    for i, n+1:
        if(i != 0):
            result = result * i
        end
    end
    return result
end

function rad(angle):
    return angle / 180 * pi()
end

function sin(angle):
    var n = 5
    var x = angle / 180 * pi()

    var k = 1
    var s = 0
    var sign = 1
    for i, n:
        s = s + ( sign * ( pow(x, k) / factorial(k) ) )
        sign = sign * -1
        k = k + 2
    end
    return s
end

function cos(angle):
    var n = 5
    var rad = angle / 180 * pi()
    var x = ( pi() / 2 ) - rad

    var k = 1
    var s = 0
    var sign = 1
    for i, n:
        s = s + ( sign * ( pow(x, k) / factorial(k) ) )
        sign = sign * -1
        k = k + 2
    end
    return s
end

function sqrt(value):
    var n = 10
    var guess = value/2
    for i, n:
        guess = (guess + (value/guess)) / 2
    end
    return guess
end
