from flask_restful import Api

from main import app
from resources import QuestionResource, QuestionListResource

api = Api(app)

api.add_resource(QuestionResource, "/api/questions/<str:question_id>")
api.add_resource(QuestionListResource, "/api/questions")
