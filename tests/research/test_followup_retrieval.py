from backend.chat import ChatRequest, retrieval_query


def test_eight_word_referential_followup_retains_actual_user_subject():
    question = 'How does that differ during the dry season?'
    previous = "How does Goa's monsoon change salinity in the Mandovi and Zuari estuaries?"
    request = ChatRequest(question=question, history=[{'role':'user','content':previous}, {'role':'assistant','content':'Unverified assistant text is not retrieval context.'}])
    assert len(question.split()) == 8
    assert retrieval_query(request) == question + ' ' + previous


def test_independent_detailed_question_does_not_inherit_unrelated_topic():
    question = 'Which forms are needed to apply for a building licence?'
    request = ChatRequest(question=question, history=[{'role':'user','content':'How do estuaries change?'}])
    assert retrieval_query(request) == question


def test_followup_context_is_bounded_and_uses_only_user_history():
    question = 'Can they continue under the conditions already discussed here?'
    request = ChatRequest(question=question, history=[{'role':'user','content':'x'*900}, {'role':'assistant','content':'Do not insert this as source evidence.'}])
    assert retrieval_query(request) == question + ' ' + 'x'*500
    assert retrieval_query(ChatRequest(question=question,history=[{'role':'assistant','content':'No user context.'}])) == question
