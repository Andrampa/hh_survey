def group(value,group_size):
    all_ranges = []
    for i in range(0,100):
        all_ranges.append(list(range(group_size * i + 1, group_size * (i+1) + 1)))
    counter = 0
    for this_range in all_ranges:
        counter +=1
        if value in this_range:
            break
    identified_range = "%s to %s" % (counter*group_size - group_size + 1, counter*group_size)
    return identified_range



group(3,7)