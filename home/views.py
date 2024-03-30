from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Problem_Statement, Solution
from octoai.client import Client
from django.http import HttpResponseRedirect
import os
from dotenv import load_dotenv


load_dotenv()

# Create your views here.
@login_required
def index(request):
    problem_statements = Problem_Statement.objects.all()
    return render(
        request, "home/index.html", {"problem_statements": problem_statements}
    )

def home(request):
    return render(request, 'home.html')

@login_required
def problem_statement(request, problem_statement_id):
    problem_statement = Problem_Statement.objects.get(pk=problem_statement_id)
    solutions = Solution.objects.all().filter(problem_statement=problem_statement)
    return render(request, "home/problem_statement.html", {"solutions": solutions, 'problem_statement': problem_statement})



@login_required
def detail_solution(request, solution_id):
    solution = Solution.objects.get(pk=solution_id)
    print(solution)
    return render(request, "home/detail_solution.html", {"solution" : solution})


def create_problem_statement(request):
    if request.method == "POST":
        problem_statement = request.POST.get("problem_statement")
        user = request.user
        Problem_Statement.objects.create(
            problem_statement=problem_statement, teacher=user
        )
        messages.success(request, "Problem Statement added successfully!")
        return redirect("app:home")

def submit_solution(request, problem_statement_id):
    if request.method == "POST":
        problem_statement = Problem_Statement.objects.get(pk=problem_statement_id)
        student = request.user
        solution = request.POST.get('solution')
        for p_solution in problem_statement.solution.all():
            if p_solution.student == student:
                p_solution.solution = solution
                p_solution.save()
                messages.success(request, "Solution is updated successfully!")
                return redirect("app:home")
        Solution.objects.create(solution=solution,student=student,problem_statement=problem_statement)
        messages.success(request, "Solution is submitted successfully!")
        return redirect("app:home")
    
def autograde_solution(request, solution_id):
    # prompt = "Given a code snippet, provide constructive remarks with line numbers for the student, suggesting improvements. Also provide rating. Consider some conditions like naming of variables, optimizations, code readability, understandability."
    # response = openai.Completion.create(
    #     model="gpt-3.5-turbo",
    #     prompt = "Given a code snippet, provide constructive remarks with line numbers for the student, suggesting improvements. Also provide rating. Consider some conditions like naming of variables, optimizations, code readability, understandability.",
        # messages= [
        #     {
        #         "role": "user",
        #         "content": "Given a code snippet, provide constructive remarks with line numbers for the student, suggesting improvements. Also provide rating. Consider some conditions like naming of variables, optimizations, code readability, understandability."
        #     },
        #     ],
    # )
    if request.method == "POST":
        if 'autograde_button' in request.POST:
            solution = Solution.objects.get(pk=solution_id)
            client = Client(os.getenv("OCTO_API_KEY"))
            response = client.chat.completions.create(
            messages=[
                         {"role": "user", 
                          "content": f'''Your role is to grade the given code snippet submitted by a student. Given a code snippet, 
                          provide constructive remarks with line numbers for the student, 
                          suggesting improvements. 
                          Also provide overall Rating for the student's code out of 5 at the end in the format (Rating: x/5). Consider some conditions like naming of variables, optimizations, code readability, understandability for the problem statement : '{solution.problem_statement.problem_statement}' and code is {solution.solution}. 
                          Note that Rating should be given only at the end of the entire feedback and only overall rating should be provided. 
                          Check the code submitted by the student against the problem statement and provide feedback. 
                          If the relevant code is not submitted then provide feedback accordingly. 
                          If the code is correct then provide feedback accordingly. 
                          If the code is incorrect then provide feedback accordingly. 
                          If the code is partially correct suggest improvements'''
                    }],
                model="llama-2-70b-chat",
                max_tokens=512,
                presence_penalty=0,
                temperature=0.1,
                top_p=0.9,
            )
            # response = openai.ChatCompletion.create(
            # model='gpt-3.5-turbo',
            # messages=[
            #     {"role": "user", "content": f"Given a code snippet, provide constructive remarks with line numbers for the student, suggesting improvements. Also provide rating. Consider some conditions like naming of variables, optimizations, code readability, understandability. Problem Statement is {problem_statement} and code is{solution_code}"}],
            # max_tokens=193,
            # temperature=0,
            # )
            feedback = response.choices[0].message.content
            print(feedback)
            rating_start = feedback.find("Rating:")
            if rating_start != -1:
                rating_str = feedback[rating_start + len("Rating:"):].strip()
                feedback = feedback.replace("Rating: " + rating_str, "")
                slash_index = rating_str.find("/")
                if slash_index != -1:
                    rating_str = rating_str[:slash_index].strip()
                    try:
                        rating = int(rating_str)
                    except ValueError:
                        rating = None
                else:
                    rating = None
            else:
                rating = None

            solution.feedback = feedback
            solution.rating = rating
            solution.accuracy = calculate_accuracy(solution.teacher_rating, solution.rating)
            solution.save()         
            messages.success(request, "Autograding completed successfully!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
def calculate_accuracy(teacher_rating, autograder_rating):
    if teacher_rating is None or autograder_rating is None:
        return 0 
    if teacher_rating == 0: 
        return 0
    difference = abs(autograder_rating - teacher_rating)
    accuracy = max(0, 100 - difference * 20)  
    return accuracy

def teacher_rating(request, solution_id):
    if request.method == "POST":
        solution = Solution.objects.get(pk=solution_id)
        teacher_rating = request.POST.get('teacher_rating')
        if int(teacher_rating)>5 or int(teacher_rating)<0:
            messages.error(request, "Rating should be in between 0 and 5")
            return redirect("app:home")
        solution.teacher_rating = teacher_rating
        solution.save()
        messages.success(request, "Teacher rating is updated successfully!")
        return redirect("app:home")
    return render(request, "home/teacher_rating.html", {"solution": solution})