from datetime import datetime, timedelta


def get_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %z %Y')


def date_difference_days(datetime1, datetime2):
    return (datetime1 - datetime2).days


def date_difference_years(datetime1, datetime2):
    return int((datetime1 - datetime2).days // 365.2425)


def get_age(tweet_obj_list, begin_index, end_index, dob):
    begin_datetime = get_datetime('Thu May 02 10:40:50 +0000 2019')
    end_datetime = get_datetime('Mon May 20 10:18:48 +0000 2019')
    days_in_window = date_difference_days(end_datetime, begin_datetime)
    middle_datetime = begin_datetime + timedelta(days=days_in_window // 2)
    dob_datetime = datetime.strptime('12/16/1990' + ' -0500', '%m/%d/%Y %z')
    age = date_difference_years(middle_datetime, dob_datetime)
    return age


print(get_age([], 0, 1, ''))
