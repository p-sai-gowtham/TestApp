from django.db import models
from user.models import User

# Create your models here.

class Problem_Statement(models.Model):
    problem_statement = models.TextField()
    teacher = models.ForeignKey(User, on_delete = models.CASCADE, related_name='problem_statement')
    created_at = models.DateTimeField(auto_now_add = True)

class Solution(models.Model):
    problem_statement = models.ForeignKey(Problem_Statement, on_delete=models.CASCADE, related_name='solution')
    solution = models.TextField()
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solution")
    created_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    teacher_rating = models.IntegerField(blank=True, null=True)
    accuracy = models.IntegerField(blank=True, null=True)