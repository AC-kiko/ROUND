#!/usr/bin/python3.9.10
# -*- coding: utf-8 -*-
# @Time    : 2025/3/22 9:41
# @File    : job_recommend.py
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "JobRecommend.settings"
import django

django.setup()
from job import models
from math import sqrt, pow
import operator
from django.db.models import Subquery, Q, Count
import random
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np

# 计算相似度
def job_similarity(job1_id, job2_id):
    job1_set = models.SendList.objects.filter(job=job1_id)
    # job1的投递用户数
    job1_sum = job1_set.count()
    # job2的打分用户数
    job2_sum = models.SendList.objects.filter(job=job2_id).count()
    # 两者的交集
    common = models.SendList.objects.filter(user__in=Subquery(job1_set.values('user')), job=job2_id).values(
        'user').count()
    # 没有人投递当前职位
    if job1_sum == 0 or job2_sum == 0:
        return 0
    # 余弦计算原有的职位相似度
    job_similarity = common / sqrt(job1_sum * job2_sum)

    return job_similarity

# 计算文本相似度（基于词频）
def calculate_text_similarity(major1, major2):
    if not major1 or not major2:
        return 0
        # 分词
    words1 = " ".join(jieba.lcut(major1))
    words2 = " ".join(jieba.lcut(major2))
    # 计算 TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([words1, words2])
    # 计算余弦相似度
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

# 基于用户的相似度
def user_similarity(user1_id, user2_id):
    user1 = models.UserList.objects.get(user_id=user1_id)
    user2 = models.UserList.objects.get(user_id=user2_id)

    # 用户属性相似度
    age_similarity = 1 - abs(user1.age - user2.age) / 100 if user1.age and user2.age else 0
    school_similarity = 1 if user1.school == user2.school else 0
    major_similarity = calculate_text_similarity(user1.major, user2.major)
    skill_similarity = calculate_text_similarity(user1.professional_skills, user2.professional_skills)
    comp_similarity = calculate_text_similarity(user1.competition_honors, user2.competition_honors)
    position_similarity = calculate_text_similarity(user1.school_position, user2.school_position)
    gpa_similarity = 1 - abs(user1.gpa - user2.gpa) / 4 if user1.gpa and user2.gpa else 0

    # 投递行为相似度
    user1_jobs = set(models.SendList.objects.filter(user=user1).values_list('job', flat=True))
    user2_jobs = set(models.SendList.objects.filter(user=user2).values_list('job', flat=True))
    intersection = len(user1_jobs.intersection(user2_jobs))
    union = len(user1_jobs.union(user2_jobs))
    behavior_similarity = intersection / union if union > 0 else 0

    # 综合相似度
    attribute_weight = 0.6
    behavior_weight = 0.4
    combined_similarity = attribute_weight * (0.1*age_similarity + 0.2*school_similarity + 0.3*major_similarity +0.3*skill_similarity+0.1*comp_similarity+0.05*position_similarity + 0.05*gpa_similarity) + behavior_weight * behavior_similarity
    return combined_similarity

# 基于物品和用户的综合相似度
def recommend_by_item_user(user_id, k=9):
    # 投递简历最多的前三keyword
    jobs_id = models.SendList.objects.filter(user_id=user_id).values('job_id')  # 先找出用户投过的简历
    key_word_list = []  # 找出用户投递的职位关键字
    for job in jobs_id:
        key_word_list.append(models.JobData.objects.get(job_id=job['job_id']).key_word)
    key_word_list_1 = list(set(key_word_list))
    user_prefer = []
    for key_word in key_word_list_1:
        user_prefer.append([key_word, key_word_list.count(key_word)])
    user_prefer = sorted(user_prefer, key=lambda x: x[1], reverse=True)  # 排序
    user_prefer = [x[0] for x in user_prefer[0:3]]  # 找出最多的3个投递简历的key_word

    current_user = models.UserList.objects.get(user_id=user_id)
    # 如果当前用户没有投递过简历,则看是否选择过意向职位，选过的话，就从意向中找，没选过就随机推荐
    if current_user.sendlist_set.count() == 0:
        if current_user.userexpect_set.count() != 0:
            user_expect = list(models.UserExpect.objects.filter(user=user_id).values("key_word", "place"))[0]
            job_list = list(models.JobData.objects.filter(name__icontains=user_expect['key_word'],
                                                          place__icontains=user_expect['place']).values())  # 从用户设置的意向中选
            try:
                job_list = random.sample(job_list, 9)
            except ValueError:
                job_list = job_list[:]
        else:
            job_list = list(models.JobData.objects.all().values())  # 从全部的职位中选
            try:
                job_list = random.sample(job_list, 9)
            except ValueError:
                job_list = job_list[:]
        return job_list

    # 选用户投递简历最多的职位的标签，再随机选择30个没有投递过的简历的职位
    un_send = list(
        models.JobData.objects.filter(~Q(sendlist__user=user_id), key_word__in=user_prefer).order_by('?').values())[
              :30]  # 没有投过的简历
    send = []  # 找出用户投递的职位关键字
    for job in jobs_id:
        send.append(models.JobData.objects.filter(job_id=job['job_id']).values()[0])

    # 计算物品相似度和用户相似度的加权得分
    distances = []
    names = []
    for un_send_job in un_send:
        total_score = 0
        for send_job in send:
            item_sim = job_similarity(un_send_job['job_id'], send_job['job_id'])
            similar_users = models.SendList.objects.filter(job=send_job['job_id']).exclude(user=user_id).values_list('user', flat=True)
            user_sim_sum = 0
            for similar_user_id in similar_users:
                user_sim = user_similarity(user_id, similar_user_id)
                user_sim_sum += user_sim
            if similar_users:
                avg_user_sim = user_sim_sum / len(similar_users)
            else:
                avg_user_sim = 0

            # 物品相似度权重 0.7，用户相似度权重 0.3
            score = 0.7 * item_sim + 0.3 * avg_user_sim
            if un_send_job not in names:
                names.append(un_send_job)
                distances.append((score * send_job['job_id'], un_send_job))

    distances.sort(key=lambda x: x[0], reverse=True)
    recommend_list = []
    for mark, job in distances:
        if len(recommend_list) >= k:
            break
        if job not in recommend_list:
            recommend_list.append(job)
    return recommend_list


if __name__ == '__main__':
    # similarity(2003, 2008)
    recommend_by_item_user(1)
