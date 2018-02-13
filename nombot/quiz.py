from nombot import telegram
import nuqui
    
def handle_quiz_request(user_id):
    #get a question
    question_dict = nuqui.get_predefined_question_dict_with_random_answers(user_id)
    message = "*Question*: \n" + question_dict['question'] + "\n*Value*:\n " + str(question_dict['value']) +  "\n\n*Answers*:\n" + "A: "+question_dict['answer'][0] + "\nB: "+question_dict['answer'][1] + "\nC: "+question_dict['answer'][2] + "\nD: "+question_dict['answer'][3]
    #send it to telegram
    telegram.send_quiz(user_id, message)
