def get_maif_age_label(age):
    if age <= 18:
        return '<=18'
    elif age >= 19 and age <= 22:
        return '19-22'
    elif age >= 23 and age <= 33:
        return '23-33'
    elif age >= 34 and age <= 45:
        return '34-45'
    else:
        return '>=46'


def get_race_label(race_code):
    if race_code == 1:
        return 'AI'
    elif race_code == 2:
        return 'AP'
    elif race_code == 3:
        return 'BL'
    elif race_code == 4:
        return 'HI'
    elif race_code == 5:
        return 'WH'
    elif race_code == 6:
        return 'OT'
    elif race_code == 7:
        return 'MU'
    elif race_code == 9:
        return 'UN'
    else:
        print('unknown race code: {}'.format(race_code))


def is_link(text):
    return text.startswith('http://') or text.startswith('https://')


def is_handle(text):
    return text.startswith('@')


UPPERCASE_ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                      'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                      'Y', 'Z']

EXTENDED_ALPHABET = open(r'D:\Data\Linkage\FL\FL18\lexicons\top_unicodes.txt', 'r', encoding='utf-8').readline().split()
