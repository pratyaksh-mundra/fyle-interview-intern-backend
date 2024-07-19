
# added imports
import pytest
from core.models.assignments import AssignmentStateEnum, GradeEnum, Assignment
from core import db
from flask import current_app


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
     # Ensure assignment with ID 5 is in DRAFT state
    assignment = Assignment.get_by_id(5)  # Retrieve the assignment with ID 5 from the database

    if not assignment:
            # If the assignment does not exist, create a new assignment with ID 5 and set its state to DRAFT
        assignment = Assignment(id=5, student_id=1, content="Test content", state=AssignmentStateEnum.DRAFT)
        db.session.add(assignment)  # Add the new assignment to the session
    else:
        # If the assignment exists, update its state to DRAFT
        assignment.state = AssignmentStateEnum.DRAFT

    db.session.flush()  # Apply changes to the database, but do not commit yet
    db.session.commit()  # Commit the transaction to make the changes permanent
        
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400
    assert response.json['message'] == 'Assignments in draft state cannot be graded' # making sure that proper error message is recieved


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B

# added this test
def test_get_teachers(client, h_principal):
    response = client.get(
        '/principals/teachers',
        headers=h_principal
    )

    assert response.status_code == 200

