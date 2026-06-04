import math


def get_aggregated_post_data(posts_stats, max_likes, max_reposts, max_comments):
    aggregated_reposts_counts = {}
    aggregated_likes_counts = {}
    aggregated_comments_counts = {}
    if max_reposts > 0:
        repost_intervals = _split_into_intervals(max_reposts)
        repost_counts = (posts_stats[item].get('reposts') for item in posts_stats)
        aggregated_reposts_counts = _count_numbers_in_intervals(repost_intervals, repost_counts)
    if max_likes > 0:
        likes_intervals = _split_into_intervals(max_likes)
        likes_counts = (posts_stats[item].get('likes') for item in posts_stats)
        aggregated_likes_counts = _count_numbers_in_intervals(likes_intervals, likes_counts)

    if max_comments > 0:
        comments_intervals = _split_into_intervals(max_comments)
        comments_counts = (posts_stats[item].get('comments') for item in posts_stats)
        aggregated_comments_counts = _count_numbers_in_intervals(comments_intervals, comments_counts)

    return {
        'aggregated_reposts_counts': aggregated_reposts_counts,
        'aggregated_likes_counts': aggregated_likes_counts,
        'aggregated_comments_counts': aggregated_comments_counts,
    }


def _split_into_intervals(number):
    number = math.ceil(number / 10) * 10
    step = math.ceil(number * 0.05)

    intervals = []
    for start in range(0, number, step):
        end = min(start + step, number)
        intervals.append((start, end))

    return intervals


def _count_numbers_in_intervals(intervals, metrics):
    counts = [0] * len(intervals)
    numbers = sorted(metrics)

    idx = 0
    for num in numbers:
        while idx < len(intervals) and num > intervals[idx][1]:
            idx += 1

        if idx < len(intervals) and intervals[idx][0] <= num <= intervals[idx][1]:
            counts[idx] += 1

    return {interval[1]: counts[i] for i, interval in enumerate(intervals)}
