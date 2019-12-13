file_paths = [r"D:\Data\Linkage\FL\FL18\tweets\maif_all_tweets_tokens.csv.dist.txt",
              r"D:\Data\Linkage\FL\FL18\tweets\yearly_long_tweets_tokens.csv.dist.txt"]
for file_path in file_paths:
    with open(file_path, 'r') as rf:
        sum_x_tweets = 0
        count_x_tweets = 0
        sum_tweets = less_100 = less_300 = less_500 = less_700 = less_1000 = 0
        num_lines = 0
        for line in rf:
            num_lines += 1
            tokens = line.strip().split()
            num_tweets = int(tokens[1])
            sum_tweets += num_tweets
            if num_tweets < 100:
                less_100 += 1
            elif num_tweets < 300:
                less_300 += 1
            elif num_tweets < 500:
                less_500 += 1
            elif num_tweets < 700:
                less_700 += 1
            elif num_tweets < 1000:
                less_1000 += 1

            if num_tweets > 500:
                sum_x_tweets += num_tweets
                count_x_tweets += 1

        print(file_path)
        print('{:0.2f}, {:0.2f}, {:0.2f}, {:0.2f}, {:0.2f}, {:0.2f}'.format(
            sum_tweets/num_lines, less_100/num_lines, less_300/num_lines,
            less_500/num_lines, less_700/num_lines, less_1000/num_lines))

        print(sum_x_tweets/count_x_tweets)
