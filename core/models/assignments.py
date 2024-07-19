import enum
from core import db
from core.apis.decorators import AuthPrincipal
from core.libs import helpers, assertions
from core.models.teachers import Teacher
from core.models.students import Student
from sqlalchemy.types import Enum as BaseEnum
from core.models.principals import Principal # added this import

class GradeEnum(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class AssignmentStateEnum(str, enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    GRADED = 'GRADED'


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, db.Sequence('assignments_id_seq'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=True)
    content = db.Column(db.Text, nullable=False) # made nullable as false
    grade = db.Column(BaseEnum(GradeEnum))
    state = db.Column(BaseEnum(AssignmentStateEnum), default=AssignmentStateEnum.DRAFT, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)

    def __repr__(self):
        return '<Assignment %r>' % self.id

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, _id):
        return cls.filter(cls.id == _id).first()

    @classmethod
    def upsert(cls, assignment_new: 'Assignment'):
        if assignment_new.id is not None:
            assignment = Assignment.get_by_id(assignment_new.id)
            assertions.assert_found(assignment, 'No assignment with this id was found')
            assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,
                                    'only assignment in draft state can be edited')
            assertions.assert_valid(assignment.content is not None, 'assignment with empty content cannot be submitted') # added assertion   
            assignment.content = assignment_new.content
        else:
            assignment = assignment_new
            db.session.add(assignment_new)

        db.session.flush()
        return assignment

    @classmethod
    def submit(cls, _id, teacher_id, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_valid(assignment.state==AssignmentStateEnum.DRAFT or assignment.state==AssignmentStateEnum.GRADED ,'Only a draft assignment can be submitted') #makes sure that the assignment is draft 
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(assignment.student_id == auth_principal.student_id, 'This assignment belongs to some other student')
        assertions.assert_valid(assignment.content is not None, 'assignment with empty content cannot be submitted')
        assignment.state = AssignmentStateEnum.SUBMITTED
        assignment.teacher_id = teacher_id
        db.session.flush()

        return assignment

    @classmethod
    def mark_grade(cls, _id, grade, auth_principal: AuthPrincipal):
        """
        Marks an assignment with a grade.

        :param _id: ID of the assignment to be graded.
        :param grade: The grade to assign to the assignment.
        :param auth_principal: The authenticated principal performing the grading.
        :return: The updated assignment object.
        """
        # Retrieve the assignment by its ID
        assignment = Assignment.get_by_id(_id)
        
        # Assert that the assignment exists
        assertions.assert_found(assignment, 'No assignment with this id was found')
        print(f"Assignment found: {assignment}")
        
        # Assert that the assignment is not in the DRAFT state
        assertions.assert_valid(assignment.state != AssignmentStateEnum.DRAFT, 'Assignments in draft state cannot be graded')
        
        # Determine if the user is either the teacher of the assignment or a principal
        is_teacher = assignment.teacher_id == auth_principal.user_id
        is_principal = auth_principal.principal_id is not None

        # Assert that only the teacher of the assignment or a principal can change grades
        assertions.assert_valid(
            is_teacher or is_principal,
            'Only the teacher of the assignment or a principal can change grades'
        )

        print(f"AuthPrincipal: {auth_principal}")
        print(f"Setting grade: {grade}")
        
        # Update the assignment's grade and state
        assignment.grade = grade
        assignment.state = AssignmentStateEnum.GRADED
        
        # Flush the changes to the database
        db.session.flush()

        return assignment


    @classmethod
    def get_assignments_by_student(cls, student_id):
        return cls.filter(cls.student_id == student_id).all()

    @classmethod
    def get_assignments_by_teacher(cls, teacher_id):
        """
        Retrieves all assignments for a specific teacher that are either submitted or graded.

        :param teacher_id: ID of the teacher whose assignments are to be retrieved.
        :return: List of assignments that match the criteria.
        """
        # Filter assignments by the teacher's ID and state (either SUBMITTED or GRADED)
        return cls.filter(
            cls.teacher_id == teacher_id,
            cls.state.in_([AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])
        ).all()

    @classmethod
    def get_all_assignments(cls):
        """
        Retrieves all assignments that are not in the DRAFT state.

        :return: List of assignments that are not in the DRAFT state.
        """
        # Filter assignments by state (excluding DRAFT)
        return cls.filter(cls.state != AssignmentStateEnum.DRAFT).all()

    @classmethod
    def list_assignments(cls):
        """
        Retrieves all assignments that are either submitted or graded.

        :return: List of assignments that are either SUBMITTED or GRADED.
        """
        # Filter assignments by state (either SUBMITTED or GRADED)
        return cls.filter(
            cls.state.in_([AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])
        ).all()
