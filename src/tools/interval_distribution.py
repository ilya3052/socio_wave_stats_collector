import math
import random

from icecream import ic


def get_aggregated_post_data(posts_stats, max_likes, max_reposts, max_comments):
    aggregated_reposts_counts = {}
    aggregated_likes_counts = {}
    aggregated_comments_counts = {}
    if max_reposts > 0:
        repost_intervals = _split_into_intervals(max_reposts)
        repost_data = ((posts_stats[item].get('reposts'), item) for item in posts_stats)
        aggregated_reposts_counts = _count_numbers_in_intervals(repost_intervals, repost_data)
    if max_likes > 0:
        likes_intervals = _split_into_intervals(max_likes)
        likes_data = ((posts_stats[item].get('likes'), item) for item in posts_stats)
        aggregated_likes_counts = _count_numbers_in_intervals(likes_intervals, likes_data)

    if max_comments > 0:
        comments_intervals = _split_into_intervals(max_comments)
        comments_data = ((posts_stats[item].get('comments'), item) for item in posts_stats)
        aggregated_comments_counts = _count_numbers_in_intervals(comments_intervals, comments_data)

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


def _count_numbers_in_intervals(intervals, post_data):
    out_posts_data = [[0, []] for _ in range(len(intervals))]
    numbers = sorted(post_data, key=lambda x: x[0])
    posts_per_interval = [[] for _ in range(len(intervals))]

    idx = 0
    for num in numbers:
        while idx < len(intervals) and num[0] > intervals[idx][1]:
            idx += 1
        if idx < len(intervals) and intervals[idx][0] <= num[0] <= intervals[idx][1]:
            out_posts_data[idx][0] += 1
            posts_per_interval[idx].append(num[1])

    for i in range(len(intervals)):
        if posts_per_interval[i]:
            sample_size = out_posts_data[i][0] if out_posts_data[i][0] < 20 else 20
            out_posts_data[i][1] = random.sample(posts_per_interval[i], sample_size)

    return {interval[1]: {"count": out_posts_data[i][0], "post_ids": out_posts_data[i][1]} for i, interval in
            enumerate(intervals)}


def update_intervals(additional_data, post_data):
    likes_data = post_data['aggregated_likes_counts']
    comms_data = post_data['aggregated_comments_counts']
    repost_data = post_data['aggregated_reposts_counts']

    likes_items = [(int(k), k) for k in likes_data]
    comms_items = [(int(k), k) for k in comms_data]
    repost_items = [(int(k), k) for k in repost_data]

    for post in additional_data.values():
        likes = post.get('likes_count', 0)
        comms = post.get('comms_count', 0)
        reposts = post.get('repost_count', 0)

        for int_k, k in likes_items:
            if likes < int_k:
                continue
            likes_data[k]['count'] += 1
            break


        for int_k, k in comms_items:
            if comms < int_k:
                continue
            comms_data[k]['count'] += 1
            break

        for int_k, k in repost_items:
            if reposts < int_k:
                continue
            repost_data[k]['count'] += 1
            break

    return post_data