from editdistance import distance


def relativedistance(wrd1: str, wrd2: str) -> float:
    dist = distance(wrd1, wrd2)
    maxl = max(len(wrd1), len(wrd2))
    result = dist/maxl
    return result