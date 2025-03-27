import random
import re
import math
import os
import traceback
import hashlib

from types import TracebackType
from typing import Any, List, Union, overload, Optional, Type
from copy import deepcopy

from question_bank.models import (
    Category,
    Subject,
    Question,
    QuestionOption,
    QuestionAnswer,
    QuestionVariable
)

from question_bank.exception import CategoryNotFoundError, SubjectNotFoundError, QuestionNotFoundError, OptionNotFoundError

from sqlmodel import SQLModel, create_engine, select, Sequence, Session as SQLModelSession
from sqlalchemy import ScalarResult, Select
from sqlalchemy.orm import subqueryload
from sqlalchemy.exc import OperationalError
from tenacity import retry, wait_fixed, retry_if_exception_type, stop_after_attempt, TryAgain, wait_exponential
from dotenv import load_dotenv

__all__ = ["QuestionBank", "QuestionRandomizer"]

load_dotenv()

# 資料庫連接字串
DATABASE_URL = os.environ.get("SQL_CONNECT_STRING") or ''

# 建立引擎
engine = create_engine(DATABASE_URL)

@retry(reraise=True, retry=retry_if_exception_type(OperationalError), wait=wait_fixed(5), stop=stop_after_attempt(5))
def connect_database():
    # 建立模型
    SQLModel.metadata.create_all(engine)

connect_database()


class QuestionBank:

    def __enter__(self):
        self.session = SQLModelSession(engine)
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        self.session.close()

        if exc_type or exc_value or traceback:
            return False
    
    @retry(reraise=True, wait=wait_exponential(multiplier=1, max=60), stop=stop_after_attempt(5))
    def _execute(self, statement: Select) -> ScalarResult:
        try:
            result = self.session.exec(statement)
        except OperationalError:
            self.session.rollback()
            raise TryAgain
        else:
            return result

    @overload
    def get_category(self) -> Sequence[Category]:
        ...

    @overload
    def get_category(self, *, category_id: int) -> Category:
        ...

    def get_category(self, *, category_id: Optional[int]=None) -> Union[Sequence[Category], Category]:
        statement = select(Category) if category_id is None else select(Category).filter_by(category_id=category_id)
        categorys = self._execute(statement).all()
        if category_id is not None:
            if not categorys:
                raise CategoryNotFoundError()
            return categorys[0]
        else:
            return categorys
    
    @overload
    def get_subject(self, *, category_id: int) -> Sequence[Subject]:
        ...
        
    @overload
    def get_subject(self, *, category_id: int, subject_id: int) -> Subject:
        ...
    
    def get_subject(self, *, category_id: int, subject_id: Optional[int]=None) -> Union[Sequence[Subject], Subject]:
        if subject_id is None:
            statement = select(Subject).filter_by(category_id=category_id)
            result = self._execute(statement).all()
        else:
            statement = select(Subject).filter_by(category_id=category_id, subject_id=subject_id)
            result = self._execute(statement).first()

        if result is None:
            raise SubjectNotFoundError()
        else:
            return result
        
    @overload
    def get_questions(self, *, category_id: int, subject_id: int) -> Sequence[Question]:
        ...
    
    @overload
    def get_questions(self, *, category_id: int, subject_id: int, question_id: int) -> Question:
        ...
        
    def get_questions(self, *, category_id: int, subject_id: int, question_id: Optional[int]=None) -> Union[Sequence[Question], Question]:
        statement = (
            select(Question).options(
                subqueryload(Question.category),
                subqueryload(Question.subject).subqueryload(Subject.questions),
                subqueryload(Question.options),
                subqueryload(Question.answer),
                subqueryload(Question.variables)
            )
            .filter_by(category_id=category_id)
            .filter_by(subject_id=subject_id))
        
        if question_id is not None:
            statement = statement.filter_by(question_id=question_id)
            result = self._execute(statement).first()
        else:
            result = self._execute(statement).all()
                    
        return result
    
    @overload
    def get_option(self, *, category_id: int, subject_id: int, question_id: int) -> Sequence[QuestionOption]:
        ...
    
    @overload
    def get_option(self, *, category_id: int, subject_id: int, question_id: int, option_id: int) -> QuestionOption:
        ...
    
    def get_option(self, *, category_id: int, subject_id: int, question_id: int, option_id: Optional[int]=None) -> Union[Sequence[QuestionOption], QuestionOption]:
        statement = (select(Question)
                     .where(Question.category_id==category_id, Question.subject_id==subject_id, Question.question_id==question_id))
        question = self._execute(statement).first()

        if question is None:
            raise QuestionNotFoundError()
        
        if option_id is not None:
            option = next((opt for opt in question.options if opt.option_id == option_id), None)
            if option is None:
                raise OptionNotFoundError()
            return option
        else:
            return question.options

    def get_answer(self, *, category_id: int, subject_id: int, question_id: int) -> List[QuestionAnswer]:
        statement = (select(Question)
                     .where(Question.category_id==category_id, Question.subject_id==subject_id, Question.question_id==question_id))
        question = self._execute(statement).first()
        if question is None:
            raise QuestionNotFoundError()
        else:
            return question.answer
        
    def get_variable(self, *, category_id: int, subject_id: int, question_id: int) -> List[QuestionVariable]:
        statement = (select(Question)
                     .where(Question.category_id==category_id, Question.subject_id==subject_id, Question.question_id==question_id))
        question = self._execute(statement).first()
        if question is None:
            raise QuestionNotFoundError()
        else:
            return question.variables
    

class QuestionRandomizer:
    def __init__(self, question: Question, random_seed: int):
        self.random_seed: int = random_seed
        self.question: Question = deepcopy(question)
        self.seed_generator = random.Random(self.random_seed + int(hashlib.md5(self.question.content.encode()).hexdigest()[:10], 16)).random
        random.Random(self.seed_generator()).shuffle(self.question.options)

    def process_variables(self) -> None:
    
        def randint(a: int, b: int):
            return random.Random(self.seed_generator()).randint(a, b)

        def uniform(a: float, b: float):
            return random.Random(self.seed_generator()).uniform(a, b)

        def uniform_r(a: float, b: float, ndigits: int):
            return round(uniform(a, b), ndigits)

        def choice(seq: List[Any]):
            return random.Random(self.seed_generator()).choice(seq)

        safe_function = [
            "acos", "asin", "atan", "atan2", "ceil", "cos", "cosh", "degrees",
            "e", "exp", "fabs", "floor", "fmod", "frexp", "hypot", "ldexp",
            "log", "log10", "modf", "pi", "pow", "radians", "sin", "sinh",
            "sqrt", "tan", "tanh"
        ]
        safe_dict = dict([(f, getattr(math, f)) for f in safe_function])
        safe_dict.update(
            abs=abs,
            max=max,
            min=min,
            round=round,
            randint=randint,
            uniform=uniform,
            choice=choice,
            uniform_r=uniform_r
        )

        dangerous_keywords = ['__import__', 'eval', 'exec', 'open', 'os', 'sys', 'subprocess', '__']
        dangerous_chars = [';', '&', '|', '$', '`', '{', '}', '[', ']']
            
        for variable in self.question.variables:
            try:
                # 確認變數名稱符合命名規則 
                if not re.fullmatch(r"^(?!.*__)[a-zA-Z_][a-zA-Z0-9_]*$", variable.variable_name):
                    raise ValueError(f"Invalid variable name: '{variable.variable_name}'. Variable names must start with a letter or underscore, contain only letters, digits, or underscores, and must not contain double underscores '__'.")

                value = variable.variable_value

                # 替換或刪除危險關鍵字
                for keyword in dangerous_keywords:
                    value = re.sub(r'\b' + keyword + r'\b', '', value)
                
                # 刪除危險字符
                for char in dangerous_chars:
                    value = value.replace(char, '')

                # 禁止存取屬性
                value = re.sub(r'(?<!\d)\.(?!\d)', '', value)

                variable.variable_value = eval(value, {"__builtins__": None}, safe_dict)
            except (SyntaxError, NameError, TypeError):
                raise ValueError(f"Invalid variable value: '{variable.variable_value}'.")

        try:
            variable_map = dict((variable.variable_name, variable.variable_value) for variable in self.question.variables)
            
            self.question.content = self.question.content.format(**variable_map)

            for option in self.question.options:
                option.content = option.content.format(**variable_map)

        except (KeyError, ValueError):
            traceback.print_exc()