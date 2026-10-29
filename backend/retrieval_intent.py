"""Bounded premises-intent expansion, without a model call or invented evidence."""
import re


def expand_retrieval_query(question):
    text = question.lower()
    if re.search(r'\b(sand ?bars?|pressure|steel bars?|bar association|bar exam)\b', text):
        return question
    venue = re.search(r'\b(bar|pub|restaurant|cafe|café|shop|hotel|guesthouse|office|warehouse|factory|school|clinic)\b', text)
    construction = re.search(r'\b(build|building|construct\w*|erect|renovat\w*|convert\w*|rebuild\w*)\b', text)
    opening = re.search(r'\b(open|start|set up|operate)\b', text)
    if not venue or not (construction or opening):
        return question
    return question + ' building construction development permission technical clearance commercial premises land use change of use'
