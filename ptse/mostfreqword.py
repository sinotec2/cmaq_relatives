
def compareItems(wc1,wc2):
    (w1,c1), (w2,c2)=wc1,wc2
    if c1 > c2:
        return - 1
    elif c1 == c2:
        return cmp(w1, w2)
    else:
        return 1
def mostfreqword(list_of_w):
    counts = {}
    for w in list_of_w:
        counts[w] = counts.get(w,0) + 1
    it=sorted(counts.items(),reverse=False)
    return it[0][0]
def mostfreq10word(list_of_w):
    if len(list_of_w)<10: 
        return []
    counts = {}
    for w in list_of_w:
        counts[w] = counts.get(w,0) + 1
    it=sorted(counts.items(),reverse=True)
#p2    it=compareItems(it)
#p2    it=counts.items()
#p2    it.sort(compareItems)
    return [(it[x][0],it[x][1]) for x in xrange(10)]
