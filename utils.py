# Helper function I found to convert the higher follower counts to decimal numbers
# I think it was on StackOverflow but a search points me to https://gist.github.com/gajeshbhat/67a3db79a6aecd1db42343190f9a2f17
def convert_str_to_number(x):
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)


