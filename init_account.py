import uuid
from random import shuffle

from database.database import db
from database.db_models import User, Question

QUESTIONS = [
    'Что получают программисты?',
    "'Вот твой первый серьезный документ', — сказали родители ребенку. О чем идет речь?",
    'От чего можно умереть?',
    'Что можно посчитать?',
    'На какой вопрос мы отвечаем каждый день?',
    'Как не пойти в армию?',
    'Кем бы мог работать Карлсон?',
    'Какой выбор самый трудный?',
    'Кому можно не работать?',
    'Что можно назвать бесконечным?',
    'Взрослый человек плачет. Что с ним случилось?',
    'Что может быть на носу?',  # дедлайн
    'Что нельзя делать?',
    'На что бывает аллергия?',
    'Какие кнопки на клавиатуре стираются быстрее всего?'
]


def add_questions(user_id: str) -> None:
    user = db.session.query(User).filter(User.id == user_id).one()
    shuffle(QUESTIONS)
    for q in QUESTIONS[:7]:
        question = Question(id=str(uuid.uuid4()), question=q, user_id=user_id)
        db.session.add(question)
        user.questions.append(question)
    db.session.commit()
