def list_to_string(list):
    res = ""
    for x in list:
        res += str(x) + '\n'
    return res

def points_to_string(dict):
    if len(dict) == 0:
        return "No one got any points???? All good (not really)"
    res = ""
    for x in dict.keys():
        res += x + ": " + str(dict[x]) + " points.\n"
    return res