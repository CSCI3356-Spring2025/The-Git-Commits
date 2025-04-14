from .models import Assessment, StudentAssessmentResponse
from oauth.models import User

def get_all_responses_for_evaluated_user(evaluated_user, assessment=None):
    responses = StudentAssessmentResponse.objects.filter(
        evaluated_user=evaluated_user
    )
    # optionally specify an assessment to filter
    if assessment:
        responses = responses.filter(assessment=assessment)
        
    return responses


def alphabetize_free_responses(evaluated_user, assessment=None):
    responses = get_all_responses_for_evaluated_user(evaluated_user, assessment)
    
    # dictionary to store answers by question
    question_answers = {}
    
    for response in responses:
        answers = response.answers.all()
        
        for answer in answers:
            if answer.question.question_type == 'Free Response':
                question_text = answer.question.text
                if question_text not in question_answers:
                    question_answers[question_text] = []
                
                if answer.answer_text and answer.answer_text.strip():
                    question_answers[question_text].append(answer.answer_text)
    
    # alphabetical list
    for question, answers_list in question_answers.items():
        question_answers[question] = sorted(answers_list)
    # returns dictionary with question text as keys and sorted lists of answers as value
    return question_answers


def average_likert_responses(evaluated_user, assessment=None):
    responses = get_all_responses_for_evaluated_user(evaluated_user, assessment)
    
    question_ratings = {}  # {question_text: [sum, count]}
    
    for response in responses:
        answers = response.answers.all()
        
        for answer in answers:
            if answer.question.question_type == 'Likert':
                question_text = answer.question.text
                
                if question_text not in question_ratings:
                    question_ratings[question_text] = [0, 0]  # [sum, count]
                
                # convert to integer and add to running sum
                try:
                    if answer.answer_text and answer.answer_text.strip():
                        rating = int(answer.answer_text)
                        question_ratings[question_text][0] += rating
                        question_ratings[question_text][1] += 1
                except (ValueError, TypeError):
                    continue
    
    averages = {}
    for question, (total, count) in question_ratings.items():
        if count > 0:
            averages[question] = total / count
        else:
            averages[question] = 0  # default for no responses
    return averages


def get_feedback_summary(evaluated_user, assessment=None):
    response_count = get_all_responses_for_evaluated_user(evaluated_user, assessment).count()
    likert_averages = average_likert_responses(evaluated_user, assessment)
    free_responses = alphabetize_free_responses(evaluated_user, assessment)
    
    # combine into a summary dictionary
    summary = {
        'evaluated_user': evaluated_user,
        'assessment': assessment,
        'response_count': response_count,
        'likert_averages': likert_averages,
        'free_responses': free_responses
    }
    
    return summary