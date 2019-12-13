ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:’"/|_#$%ˆ&*˜‘+=<>()[]{} '

print(list(ALPHABET))

print(list(ALPHABET.upper()))

with open(r"D:\top_onegrams_6702746.txt", encoding='utf-8') as rf:
    top_chars = []

    for line in rf:

        word = line.strip()

        if len(word) == 1 and word not in ALPHABET:
            top_chars.append(word)

    with open(r'D:\Data\Linkage\FL\FL18\lexicons\top_unicodes.txt', 'w', encoding='utf-8') as wf:
        wf.write(",".join(top_chars))
