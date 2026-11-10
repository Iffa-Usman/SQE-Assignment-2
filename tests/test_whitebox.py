import pytest

from registration import Course, Student, register_course, registration_decision


# Functions to create students and courses

def make_student (**student_data):
    
    student_data.setdefault ("student_id", "S001")
    return Student (**student_data)


def make_course (**course_data):
    
    course_data.setdefault ("code", "CS201")
    course_data.setdefault ("credit_hours", 3)
    course_data.setdefault ("capacity", 30)
    return Course (**course_data)


# Path values are documentation only and are not used by the tests
# Node numbers refer to docs/cfg.png

# WB-P01 to WB-P10: Basis Path Testing

BASIS_PATHS = [

    pytest.param ("1-2-18", {"outstanding_dues": -1}, {},
                 ValueError ("Invalid dues"), id="WB-P01"),

    pytest.param ("1-3-6-18", {}, {"enrolled": -1},
                 ValueError ("Invalid capacity or enrollment"), id="WB-P02"),

    pytest.param ("1-3-4-6-18", {}, {"enrolled": 31},
                 ValueError ("Invalid capacity or enrollment"), id="WB-P03"),

    pytest.param ("1-3-4-5-6-18", {}, {"capacity": 0, "enrolled": 0},
                 ValueError ("Invalid capacity or enrollment"), id="WB-P04"),

    pytest.param ("1-3-4-5-7-8-18", {"outstanding_dues": 5000}, {},
                 "DUES_BLOCK", id="WB-P05"),

    pytest.param ("1-3-4-5-7-9-10-18", {"registered_courses": {"CS201"}}, {},
                "ALREADY_REGISTERED", id="WB-P06"),

    pytest.param ("1-3-4-5-7-9-11-12-18", {}, {"prerequisites": {"CS101"}},
                "PREREQUISITES_MISSING", id="WB-P07"),

    pytest.param ("1-3-4-5-7-9-11-13-14-18",
             {"current_credits": 16}, {"credit_hours": 3},
                "CREDIT_LIMIT", id="WB-P08"),

# Expected to fail because of defect #4
# The expected value is derived from FR-08 in the SRS, not from the current implementation

    pytest.param ("1-3-4-5-7-9-11-13-15-16-18", {}, {"enrolled": 30},
                "WAITLISTED", id="WB-P09"),

    pytest.param ("1-3-4-5-7-9-11-13-15-17-18", {}, {},
                "REGISTERED", id="WB-P10"),
]


@pytest.mark.parametrize ("path, student_data, course_data, expected", BASIS_PATHS)

def test_basis_paths (path, student_data, course_data, expected):

    student = make_student (**student_data)
    course = make_course (**course_data)

    if isinstance (expected, ValueError):

        with pytest.raises (ValueError, match=f"^{expected}$"):
            registration_decision (student, course)

    else:
        assert registration_decision (student, course) == expected


# WB-11 to WB-13: Waitlist Decision Testing

# WB-11: Student is waitlisted and not already in waitlist
# register_course line 70 
# Expected to fail because of defect #4
# The expected values come from FR-08 in the SRS, not from the current implementation 

def test_wb11 ():
    
    student = make_student ()
    course = make_course (enrolled=30)

    assert register_course (student, course) == "WAITLISTED"
    assert course.waitlist == ["S001"]


# WB-12: Student is already in waitlist
# register_course line 70
# Expected to fail because of defect #4
# The expected values come from FR-08 in the SRS, not from the current implementation

def test_wb12 ():
    student = make_student ()
    course = make_course (enrolled=30, waitlist=["S001"])

    assert register_course (student, course) == "WAITLISTED"
    assert course.waitlist == ["S001"]


# WB-13: Student is registered, not waitlisted
# register_course line 70: P=False, Q not evaluated (short-circuit)
# P alone flips the outcome (pair with WB-11)

def test_wb13 ():

    student = make_student ()
    course = make_course (enrolled=5, waitlist=["S900"])

    assert register_course (student, course) == "REGISTERED"
    assert course.waitlist == ["S900"]


# WB-14 to WB-17: MC/DC Testing

# WB-14: All conditions are valid
# registration_decision line 48
# A=True, B=True, C=False -> decision=False (no raise)

def test_wb14 ():
    
    student = make_student ()
    course = make_course (enrolled=5, capacity=30)

    assert registration_decision (student, course) == "REGISTERED"


# WB-15: Enrolled student count is negative
# line 48
# A=False (B and C not evaluated) -> decision=True
# Pair WB-14/WB-15 shows A's effect

def test_wb15 ():

    student = make_student ()
    course = make_course (enrolled=-1, capacity=30)

    with pytest.raises (ValueError, match="Invalid capacity or enrollment"):
        registration_decision (student, course)


# WB-16: Enrolled students are greater than capacity
# line 48 
# A=True, B=False (C not evaluated) -> decision=True
# Pair WB-14/WB-16 shows B's effect

def test_wb16 ():
    student = make_student ()
    course = make_course (enrolled=31, capacity=30)

    with pytest.raises (ValueError, match="Invalid capacity or enrollment"):
        registration_decision (student, course)


# WB-17: Course capacity is zero
# line 48 
# A=True, B=True, C=True -> decision=True
# Pair WB-14/WB-17 shows C's effect

def test_wb17 ():

    student = make_student ()
    course = make_course(enrolled=0, capacity=0)

    with pytest.raises (ValueError, match="Invalid capacity or enrollment"):
        registration_decision (student, course)
