import os
from collections import Counter
from collections import defaultdict

TW_RUNNING_RECORDS_DIR = r'D:\Data\Linkage\FL\FL18\tw_running_records_new'
TW_ACCOUNTS_PARSED_DIR = r'D:\Data\Linkage\FL\FL18\tw_accounts_parsed_new'
TW_ACCOUNTS_GRANULAR_DIR = r"D:\Data\Linkage\FL\FL18\tw_accounts_granular"


def get_modes(numbers):
    modes = []
    counts = Counter(numbers)
    maxcount = max(counts.values())
    for num, count in counts.items():
        if count == maxcount:
            modes.append(num)
    return modes


if __name__ == '__main__':

    gt = defaultdict(None)
    predictions = defaultdict(None)

    file_indices = list(range(74))
    file_indices.extend(list(range(1975, 2000)))

    print(file_indices)

    for file_index in file_indices:

        print(file_index)

        gt_lines = []
        vt_lines = []

        gt_path = os.path.join(TW_ACCOUNTS_GRANULAR_DIR, 'tw_acc_granular_{}.txt'.format(file_index))

        vt_path = os.path.join(r'D:\Data\Linkage\FL\FL18\tw_running_records',
                               'tw_running_rec_{}.txt'.format(file_index))

        with open(gt_path, 'r') as rf:
            gt_lines = rf.readlines()
        with open(vt_path, 'r') as rf:
            vt_lines = rf.readlines()

        for gt_line in gt_lines:
            vt_index = int(gt_line[:gt_line.index(':\t')]) - 1
            twitter_info = gt_line[gt_line.index(':\t') + 2:].strip()
            if twitter_info:
                attributes = twitter_info.split('\t')
                twitter_id = attributes[2]
                vt_email = vt_lines[vt_index].split('\t')[1]
                gt[twitter_id] = vt_email

        #        print(gt)

        fname_dict = defaultdict(lambda: defaultdict(list))
        mname_dict = defaultdict(lambda: defaultdict(list))
        lname_dict = defaultdict(lambda: defaultdict(list))
        uname_dict = defaultdict(lambda: defaultdict(list))

        voter_lines = []
        voter_file = os.path.join(TW_RUNNING_RECORDS_DIR, 'tw_running_rec_{}.txt'.format(file_index))

        with open(voter_file, 'r') as rf:
            for line in rf:
                tokens = list(map(lambda x: x.strip().lower(), line.split('\t')))
                fname = tokens[2]
                mname = tokens[3]
                lname = tokens[4]
                email = tokens[1]
                uname = email[:tokens[1].index('@')]
                voter_lines.append({'fname': fname, 'mname': mname, 'lname': lname, 'uname': uname, 'email': email})

        for line_num, voter_line in enumerate(voter_lines):
            fname = voter_line['fname']
            mname = voter_line['mname']
            lname = voter_line['lname']
            uname = voter_line['uname']

            if fname:
                fname_dict[fname[0]][fname].append(line_num)

            if mname:
                mname_dict[mname[0]][mname].append(line_num)

            if lname:
                lname_dict[lname[0]][lname].append(line_num)

            uname_dict[uname[0]][uname].append(line_num)

        mapping = defaultdict(list)

        twitter_lines = []
        twitter_file = os.path.join(TW_ACCOUNTS_PARSED_DIR, 'acc_parsed_{}.txt'.format(file_index))

        with open(twitter_file, 'r') as rf:
            for line in rf:
                tokens = list(map(lambda x: x.strip().lower(), line.split('\t')))
                name = tokens[0]
                name_parts = [x.strip() for x in name.split(' ') if x]
                uname = tokens[1]
                tid = tokens[2]
                twitter_lines.append({'name_parts': name_parts, 'uname': uname, 'tid': tid})

        for line_num, twitter_line in enumerate(twitter_lines):
            name_parts = twitter_line['name_parts']
            uname = twitter_line['uname']

            for name_part in name_parts:
                #                print(line_num, name_part)
                mapping[line_num].extend(fname_dict.get(name_part[0], {}).get(name_part, []))
                mapping[line_num].extend(mname_dict.get(name_part[0], {}).get(name_part, []))
                mapping[line_num].extend(lname_dict.get(name_part[0], {}).get(name_part, []))

            mapping[line_num].extend(uname_dict.get(uname[0], {}).get(uname, []))

        for k in mapping:
            if mapping[k]:
                mapping[k] = get_modes(mapping[k])

        mapped_voter_lines = set()
        nonmapped_voter_lines = set(range(len(voter_lines))) - mapped_voter_lines

        for val in mapping.values():
            if len(val) == 1:
                mapped_voter_lines.add(val[0])
        for k, v in mapping.items():
            if len(v) > 1:
                mapping[k] = list(set(v) - mapped_voter_lines)

        for k, v in mapping.items():

            twitter_line = twitter_lines[k]
            name_parts = twitter_line['name_parts']
            t_uname = twitter_line['uname']

            if len(v) != 1:

                for line_num in nonmapped_voter_lines:

                    voter_line = voter_lines[line_num]
                    fname = voter_line['fname']
                    mname = voter_line['mname']
                    lname = voter_line['lname']
                    v_uname = voter_line['uname']

                    if len(fname) > 2:
                        if fname in t_uname:
                            mapping[k].append(line_num)
                    #                            print(fname, t_uname)
                    #                    if len(mname) > 5:
                    #                        if mname in t_uname:
                    #                            mapping[k].append(line_num)
                    #                            print(mname, t_uname)
                    if len(lname) > 2:
                        if lname in t_uname:
                            mapping[k].append(line_num)
            #                            print(lname, t_uname)

            if len(v) > 1:

                for line_num in set(mapping[k]):
                    voter_line = voter_lines[line_num]
                    fname = voter_line['fname']
                    mname = voter_line['mname']
                    lname = voter_line['lname']
                    v_uname = voter_line['uname']

                    name_parts_intials = list(map(lambda x: x[0], name_parts))

                    if fname:
                        if fname[0] in name_parts_intials:
                            mapping[k].append(line_num)
                    #                            print(k, mapping[k])

                    if mname:
                        if mname[0] in name_parts_intials:
                            mapping[k].append(line_num)
                    #                            print(k, mapping[k])
                    if lname:
                        if lname[0] in name_parts_intials:
                            mapping[k].append(line_num)
        #                            print(k, mapping[k])

        for k in mapping:
            if mapping[k]:
                mapping[k] = get_modes(mapping[k])

            #        for item in mapping.items():
        #            print(item)

        for k, v in mapping.items():
            if len(v) == 1:
                twitter_id = twitter_lines[k]['tid']
                email = voter_lines[v[0]]['email']
                predictions[twitter_id] = email

    T = 0
    F = 0
    U = 0

    for k, v in gt.items():
        if k in predictions:
            if predictions[k] == v:
                T += 1
            else:
                F += 1
        else:
            U += 1

    print(len(gt), T, F, U)
