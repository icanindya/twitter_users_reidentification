import math

import google_credentials as gcred

TW_ACCOUNTS_GRANULAR_DIR = r"D:\Data\Linkage\FL\FL18\tw_accounts_granular_fresh"

num_accounts = len(gcred.accounts)

begin_file_index = 0
end_file_index = 7

for account_index in range(len(gcred.accounts)):
    start = begin_file_index + account_index * int(math.ceil((end_file_index - begin_file_index + 1) / num_accounts))
    stop = min(end_file_index + 1, begin_file_index + (account_index + 1) * int(
        math.ceil((end_file_index - begin_file_index + 1) / num_accounts)))

    file_indexes = list(range(start, stop))

    print(file_indexes)
