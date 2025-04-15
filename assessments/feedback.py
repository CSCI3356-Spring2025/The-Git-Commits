from .models import Assessment, StudentAssessmentResponse
from oauth.models import User
import logging

logger = logging.getLogger(__name__)

def get_all_responses_for_evaluated_user(evaluated_user, assessment=None):
    responses = StudentAssessmentResponse.objects.filter(
        evaluated_user=evaluated_user
    )
    # optionally specify an assessment to filter
    if assessment:
        responses = responses.filter(assessment=assessment)
    
    logger.debug(f"Found {responses.count()} responses for user {evaluated_user.email}")
    return responses


def alphabetize_free_responses(evaluated_user, assessment=None):
    responses = get_all_responses_for_evaluated_user(evaluated_user, assessment)
    
    # dictionary to store answers by question
    question_answers = {}
    
    for response in responses:
        answers = response.answers.all()
        logger.debug(f"Processing {answers.count()} answers for response {response.id}")
        
        for answer in answers:
            if answer.question.question_type == 'free':
                question_text = answer.question.question
                if question_text not in question_answers:
                    question_answers[question_text] = []
                
                if answer.answer_text and answer.answer_text.strip():
                    question_answers[question_text].append(answer.answer_text)
                    logger.debug(f"Added free response for question '{question_text}': {answer.answer_text[:50]}...")
    
    # alphabetical list
    for question, answers_list in question_answers.items():
        question_answers[question] = sorted(answers_list)
    logger.debug(f"Processed {len(question_answers)} free response questions")
    return question_answers


def average_likert_responses(evaluated_user, assessment=None):
    responses = get_all_responses_for_evaluated_user(evaluated_user, assessment)
    
    question_ratings = {}  # {question_text: [sum, count]}
    
    for response in responses:
        answers = response.answers.all()
        logger.debug(f"Processing {answers.count()} answers for response {response.id}")
        
        for answer in answers:
            if answer.question.question_type == 'likert':
                question_text = answer.question.question
                
                if question_text not in question_ratings:
                    question_ratings[question_text] = [0, 0]  # [sum, count]
                
                # convert to integer and add to running sum
                try:
                    if answer.answer_text and answer.answer_text.strip():
                        rating = int(answer.answer_text)
                        question_ratings[question_text][0] += rating
                        question_ratings[question_text][1] += 1
                        logger.debug(f"Added Likert rating {rating} for question '{question_text}'")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid Likert response for question '{question_text}': {answer.answer_text}")
                    continue
    
    averages = {}
    for question, (total, count) in question_ratings.items():
        if count > 0:
            averages[question] = total / count
            logger.debug(f"Question '{question}' average: {averages[question]}")
        else:
            averages[question] = 0  # default for no responses
    logger.debug(f"Processed {len(averages)} Likert questions")
    return averages


def get_feedback_summary(evaluated_user, assessment=None):
    response_count = get_all_responses_for_evaluated_user(evaluated_user, assessment).count()
    likert_averages = average_likert_responses(evaluated_user, assessment)
    free_responses = alphabetize_free_responses(evaluated_user, assessment)
    
    logger.debug(f"Feedback summary for {evaluated_user.email}:")
    logger.debug(f"- Response count: {response_count}")
    logger.debug(f"- Likert questions: {len(likert_averages)}")
    logger.debug(f"- Free response questions: {len(free_responses)}")
    
    # combine into a summary dictionary
    summary = {
        'evaluated_user': evaluated_user,
        'assessment': assessment,
        'response_count': response_count,
        'likert_averages': likert_averages,
        'free_responses': free_responses
    }
    
    return summary


def alphabetize_free_responses_student(evaluated_user, assessment=None):
    responses = get_all_responses_for_evaluated_user(evaluated_user, assessment)
    
    # dictionary to store answers by question
    question_answers = {}
    
    for response in responses:
        answers = response.answers.all()
        logger.debug(f"Processing {answers.count()} answers for response {response.id}")
        
        for answer in answers:
            if answer.question.question_type == 'free':
                question_text = answer.question.question
                if question_text not in question_answers:
                    question_answers[question_text] = []
                
                if answer.answer_text and answer.answer_text.strip():
                    question_answers[question_text].append(answer.answer_text)
                    logger.debug(f"Added free response for question '{question_text}': {answer.answer_text[:50]}...")
    
    # alphabetical list
    for question, answers_list in question_answers.items():
        question_answers[question] = sorted(answers_list)
    logger.debug(f"Processed {len(question_answers)} free response questions")
    return question_answers

def get_feedback_summary_student(evaluated_user, assessment=None):
    response_count = get_all_responses_for_evaluated_user(evaluated_user, assessment).count()
    likert_averages = average_likert_responses(evaluated_user, assessment)
    free_responses = alphabetize_free_responses(evaluated_user, assessment)
    
    logger.debug(f"Feedback summary for {evaluated_user.email}:")
    logger.debug(f"- Response count: {response_count}")
    logger.debug(f"- Likert questions: {len(likert_averages)}")
    logger.debug(f"- Free response questions: {len(free_responses)}")
    
    # combine into a summary dictionary
    summary = {
        'evaluated_user': evaluated_user,
        'assessment': assessment,
        'response_count': response_count,
        'likert_averages': likert_averages,
        'free_responses': free_responses
    }
    
    return summary
