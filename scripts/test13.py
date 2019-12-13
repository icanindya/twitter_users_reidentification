dic = {1: ['A', 'B', 'C'],
       2: ['D', 'E', 'F'],
       3: ['G', 'H', 'I'],
       4: ['J', 'K', 'L'],
       5: ['M', 'N', 'O'],
       6: ['P', 'Q', 'R'],
       7: ['S', 'T'],
       8: ['U', 'V', 'W'],
       9: ['X', 'Y'],
       0: ['Z']}

extended_dic = {}


def parse_sequence(initial, length):
    tokens = []
    solutions = []

    def find_summation(remainder, nums, curr):

        if remainder == 0:
            solutions.append(curr)

        for num in nums:
            if num <= remainder:
                new_curr = curr + [num]
                find_summation(remainder - num, nums, new_curr)

    nums = [(x + 1) for x in range(len(dic[initial]))]

    find_summation(length, nums, [])

    for solution in solutions:
        letters = []
        for num in solution:
            key = str(initial) * num
            letters.append(extended_dic[key])
        tokens.append(''.join(letters))

    return tokens


def program(arr):
    for k, v in dic.items():
        for i in range(len(v)):
            key = str(k) * (i + 1)
            extended_dic[key] = v[i]

    curr_tokens = ['']

    i = 0
    j = 0

    while i < len(arr):
        initial = arr[i]

        while j < len(arr) and arr[j] == initial:
            j += 1

        next_tokens = parse_sequence(initial, j - i)

        joined = []

        for curr_token in curr_tokens:
            for next_token in next_tokens:
                joined.append(curr_token + next_token)

        curr_tokens = joined
        i = j

    return curr_tokens


if __name__ == "__main__":
    arr = [1, 1, 2]
    # Output: ["AAD" , "BD"]
    print(program(arr))

    arr = [1, 1, 1, 1]
    # Output: ["AAAD", "ABD", "CD", "BAD"]
    print(program(arr))
