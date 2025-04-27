from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class Category(SQLModel, table=True):
    category_id: int = Field(default=None, primary_key=True, nullable=False, sa_column_kwargs={'name': 'CategoryID'})
    name: str = Field(max_length=16, nullable=False, sa_column_kwargs={'name': 'Name'})
    background_image: str | None = Field(default=None, max_length=256, sa_column_kwargs={'name': 'BackgroundImage'})

    subjects: List["Subject"] = Relationship(back_populates="category")
    questions: List["Question"] = Relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(CategoryID={self.category_id}, Name={self.name})>"


class Subject(SQLModel, table=True):
    subject_id: int = Field(default=None, primary_key=True, nullable=False, sa_column_kwargs={'name': 'SubjectID'})
    category_id: int = Field(foreign_key="category.CategoryID", nullable=False, sa_column_kwargs={'name': 'CategoryID'})
    name: str = Field(max_length=16, nullable=False, sa_column_kwargs={'name': 'Name'})
    description: str = Field(max_length=32, nullable=False, sa_column_kwargs={'name': 'Description'})
    background_image: Optional[str] = Field(default=None, max_length=256, sa_column_kwargs={'name': 'BackgroundImage'})

    category: "Category" = Relationship(back_populates="subjects")
    questions: List["Question"] = Relationship(back_populates="subject")

    def __repr__(self):
        return f"<Subject(CategoryID={self.category_id}, SubjectID={self.subject_id}, Name={self.name})>"


class Question(SQLModel, table=True):
    question_id: int = Field(default=None, primary_key=True, nullable=False, sa_column_kwargs={'name': 'QuestionID'})
    category_id: int = Field(foreign_key="category.CategoryID", nullable=False, sa_column_kwargs={'name': 'CategoryID'})
    subject_id: int = Field(foreign_key="subject.SubjectID", nullable=False, sa_column_kwargs={'name': 'SubjectID'})
    content: str = Field(max_length=256, nullable=False, sa_column_kwargs={'name': 'Content'})

    category: "Category" = Relationship(back_populates="questions")
    subject: "Subject" = Relationship(back_populates="questions")
    options: List["QuestionOption"] = Relationship(back_populates="question")
    answer: List["QuestionAnswer"] = Relationship(back_populates="question")
    variables: List["QuestionVariable"] = Relationship(back_populates="question")

    def __repr__(self):
        return f"<Question(CategoryID={self.category_id}, SubjectID={self.subject_id}, QuestionID={self.question_id}, Content={self.content[:10]})>"


class QuestionOption(SQLModel, table=True):
    option_id: int = Field(default=None, primary_key=True, sa_column_kwargs={'name': 'OptionID'})
    question_id: int = Field(foreign_key="question.QuestionID", primary_key=True, nullable=False, sa_column_kwargs={'name': 'QuestionID'})
    content: str = Field(max_length=256, nullable=False, sa_column_kwargs={'name': 'Content'})

    question: "Question" = Relationship(back_populates="options")

    def __repr__(self):
        return f"<QuestionOption(QuestionID={self.question_id}, OptionID={self.option_id}, Content={self.content})>"


class QuestionAnswer(SQLModel, table=True):
    question_id: int = Field(foreign_key="question.QuestionID", primary_key=True, nullable=False, sa_column_kwargs={'name': 'QuestionID'})
    option_id: int = Field(foreign_key="questionoption.OptionID", primary_key=True, nullable=False, sa_column_kwargs={'name': 'OptionID'})

    question: "Question" = Relationship(back_populates="answer")

    def __repr__(self):
        return f"<QuestionAnswer(QuestionID={self.question_id}, OptionID={self.option_id})>"


class QuestionVariable(SQLModel, table=True):
    question_id: int = Field(foreign_key="question.QuestionID", primary_key=True, nullable=False, sa_column_kwargs={'name': 'QuestionID'})
    variable_name: str = Field(max_length=16, primary_key=True, nullable=False, sa_column_kwargs={'name': 'VariableName'})
    variable_value: str = Field(max_length=64, nullable=False, sa_column_kwargs={'name': 'VariableValue'})

    question: "Question" = Relationship(back_populates="variables")

    def __repr__(self):
        return f"<QuestionVariable(QuestionID={self.question_id}, VariableName={self.variable_name}, VariableValue={self.variable_value})>"
