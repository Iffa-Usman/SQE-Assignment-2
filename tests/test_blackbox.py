"""
Expected values are derived from REQUIREMENTS.md.
"""
import pytest

from registration import (
    Student, Course,
    check_credit_limit,
    prerequisites_satisfied,
    registration_decision,
    register_course,
    withdraw_course
)


# Helper function to create a student
def mk_s(**kwargs):
    student = {
        "student_id": "S001",
        "completed_courses": set(),
        "current_credits": 0,
        "outstanding_dues": 0,
        "registered_courses": set()
    }

    student.update(kwargs)
    return Student(**student)


# Helper function to create a course
def mk_c(**kwargs):
    course = {
        "code": "CS201",
        "credit_hours": 3,
        "capacity": 30,
        "enrolled": 0,
        "prerequisites": set(),
        "waitlist": []
    }

    course.update(kwargs)
    return Course(**course)


# ================= ECP TESTING =================

def test_ECP01_dues_zero():
    assert registration_decision(mk_s(), mk_c()) == "REGISTERED"


def test_ECP02_dues_positive():
    assert registration_decision(mk_s(outstanding_dues=500), mk_c()) == "DUES_BLOCK"


def test_ECP03_dues_negative():
    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(mk_s(outstanding_dues=-1), mk_c())


def test_ECP04_no_prerequisites():
    assert registration_decision(mk_s(), mk_c()) == "REGISTERED"


def test_ECP05_all_prerequisites_done():
    s = mk_s(completed_courses={"CS101", "MATH101"})
    c = mk_c(prerequisites={"CS101", "MATH101"})

    assert registration_decision(s, c) == "REGISTERED"


def test_ECP06_some_prerequisites_missing():
    s = mk_s(completed_courses={"CS101"})
    c = mk_c(prerequisites={"CS101", "MATH101"})

    assert registration_decision(s, c) == "PREREQUISITES_MISSING"


def test_ECP07_no_prerequisites_completed():
    c = mk_c(prerequisites={"CS101"})

    assert registration_decision(mk_s(), c) == "PREREQUISITES_MISSING"


def test_ECP08_already_registered():
    s = mk_s(registered_courses={"CS201"}, current_credits=3)

    assert registration_decision(s, mk_c()) == "ALREADY_REGISTERED"


def test_ECP09_seat_available():
    assert registration_decision(mk_s(), mk_c(enrolled=10)) == "REGISTERED"

    # ECP10, BVA14 and DT05 share identical inputs:
    # enrolled=30, capacity=30, and an eligible student.
    # All preconditions and input values are identical,
    # so these IDs map to one executed test case.

def test_ECP10_course_full():
    assert registration_decision(mk_s(), mk_c(enrolled=30)) == "WAITLISTED"


def test_ECP11_invalid_course_credits():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(10, 5)

    # Tests the capacity < 1 rule (FR-15).

def test_ECP12_invalid_capacity():
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk_s(), mk_c(capacity=0))


def test_ECP13_prereq_func_all_present():
    assert prerequisites_satisfied({"A", "B", "C"}, {"A", "B"}) is True


def test_ECP14_prereq_func_partial():
    assert prerequisites_satisfied({"A"}, {"A", "B"}) is False


def test_ECP15_prereq_func_empty_required():
    assert prerequisites_satisfied(set(), set()) is True


def test_ECP16_credit_validation_order_current_first():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(19, 5)


def test_ECP17_dues_validated_before_capacity():
    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(mk_s(outstanding_dues=-1), mk_c(capacity=0))


# ================= BVA TESTING =================

def test_BVA01_current_credits_below_min():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(-1, 3)


def test_BVA02_current_credits_min():
    assert check_credit_limit(0, 3) is True


def test_BVA03_current_credits_min_plus_one():
    assert check_credit_limit(1, 3) is True


def test_BVA04_total_exactly_18():
    assert check_credit_limit(17, 1) is True


def test_BVA05_total_19():
    assert check_credit_limit(18, 1) is False


def test_BVA06_current_credits_above_max():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(19, 1)


def test_BVA07_course_credits_below_min():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(5, 0)


def test_BVA08_course_credits_min():
    assert check_credit_limit(5, 1) is True


def test_BVA09_course_credits_max():
    assert check_credit_limit(5, 4) is True


def test_BVA10_course_credits_above_max():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(5, 5)

# Requirements: FR-01 and FR-07
def test_BVA11_decision_total_18():
    s = mk_s(current_credits=15)

    assert registration_decision(s, mk_c(credit_hours=3)) == "REGISTERED"


def test_BVA12_decision_total_19():
    s = mk_s(current_credits=16)

    assert registration_decision(s, mk_c(credit_hours=3)) == "CREDIT_LIMIT"


def test_BVA13_last_seat():
    assert registration_decision(mk_s(), mk_c(enrolled=29)) == "REGISTERED"


def test_BVA14_seats_full():
    assert registration_decision(mk_s(), mk_c(enrolled=30)) == "WAITLISTED"


def test_BVA15_dues_zero():
    assert registration_decision(mk_s(outstanding_dues=0), mk_c()) == "REGISTERED"


def test_BVA16_dues_one():
    assert registration_decision(mk_s(outstanding_dues=1), mk_c()) == "DUES_BLOCK"


def test_BVA17_enrolled_above_capacity():
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk_s(), mk_c(enrolled=31))


def test_BVA18_enrolled_negative():
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(mk_s(), mk_c(enrolled=-1))


def test_BVA19_capacity_min_valid():
    assert registration_decision(mk_s(), mk_c(capacity=1)) == "REGISTERED"


def test_BVA20_student_at_18_credits():
    s = mk_s(current_credits=18)

    assert registration_decision(s, mk_c(credit_hours=1)) == "CREDIT_LIMIT"


# ================= DECISION TABLE TESTING =================

def test_DT01_R1_dues_block():
    assert registration_decision(mk_s(outstanding_dues=100), mk_c()) == "DUES_BLOCK"


def test_DT02_R2_already_registered():
    s = mk_s(registered_courses={"CS201"}, current_credits=3)

    assert registration_decision(s, mk_c()) == "ALREADY_REGISTERED"


def test_DT03_R3_prereq_missing():
    c = mk_c(prerequisites={"X"})

    assert registration_decision(mk_s(), c) == "PREREQUISITES_MISSING"


def test_DT04_R4_credit_limit():
    s = mk_s(current_credits=17)

    assert registration_decision(s, mk_c(credit_hours=3)) == "CREDIT_LIMIT"


def test_DT05_R5_waitlisted():
    assert registration_decision(mk_s(), mk_c(enrolled=30)) == "WAITLISTED"


def test_DT06_R6_registered():
    assert registration_decision(mk_s(), mk_c(enrolled=5)) == "REGISTERED"


def test_DT07_priority_dues_over_all():
    s = mk_s(
        outstanding_dues=1,
        current_credits=18,
        registered_courses={"CS201"}
    )

    c = mk_c(prerequisites={"X"}, enrolled=30)

    assert registration_decision(s, c) == "DUES_BLOCK"


def test_DT08_priority_already_over_prereq():
    s = mk_s(registered_courses={"CS201"}, current_credits=3)
    c = mk_c(prerequisites={"X"})

    assert registration_decision(s, c) == "ALREADY_REGISTERED"


def test_DT09_priority_prereq_over_credit_and_full():
    s = mk_s(current_credits=18)
    c = mk_c(prerequisites={"X"}, enrolled=30)

    assert registration_decision(s, c) == "PREREQUISITES_MISSING"


def test_DT10_priority_credit_over_full():
    s = mk_s(current_credits=18)

    assert registration_decision(s, mk_c(enrolled=30)) == "CREDIT_LIMIT"


# ================= STATE CHANGE TESTING =================

def test_ST01_register_updates_state():
    s = mk_s(current_credits=3)
    c = mk_c(enrolled=5)

    assert register_course(s, c) == "REGISTERED"

    assert "CS201" in s.registered_courses
    assert s.current_credits == 6
    assert c.enrolled == 6


def test_ST02_waitlist_once_no_other_change():
    s = mk_s()
    c = mk_c(enrolled=30)

    assert register_course(s, c) == "WAITLISTED"
    assert register_course(s, c) == "WAITLISTED"

    assert c.waitlist == ["S001"]
    assert s.current_credits == 0
    assert s.registered_courses == set()
    assert c.enrolled == 30


def test_ST03a_dues():
    s = mk_s(outstanding_dues=1)
    c = mk_c()

    old_credits = s.current_credits
    old_courses = set(s.registered_courses)
    old_enrolled = c.enrolled

    assert register_course(s, c) == "DUES_BLOCK"

    assert s.current_credits == old_credits
    assert s.registered_courses == old_courses
    assert c.enrolled == old_enrolled
    assert c.waitlist == []


def test_ST03b_already():
    s = mk_s(current_credits=3, registered_courses={"CS201"})
    c = mk_c()

    old_credits = s.current_credits
    old_courses = set(s.registered_courses)
    old_enrolled = c.enrolled

    assert register_course(s, c) == "ALREADY_REGISTERED"

    assert s.current_credits == old_credits
    assert s.registered_courses == old_courses
    assert c.enrolled == old_enrolled
    assert c.waitlist == []


def test_ST03c_prereq():
    s = mk_s()
    c = mk_c(prerequisites={"X"})

    old_credits = s.current_credits
    old_courses = set(s.registered_courses)
    old_enrolled = c.enrolled

    assert register_course(s, c) == "PREREQUISITES_MISSING"

    assert s.current_credits == old_credits
    assert s.registered_courses == old_courses
    assert c.enrolled == old_enrolled
    assert c.waitlist == []


def test_ST03d_credit():
    s = mk_s(current_credits=17)
    c = mk_c()

    old_credits = s.current_credits
    old_courses = set(s.registered_courses)
    old_enrolled = c.enrolled

    assert register_course(s, c) == "CREDIT_LIMIT"

    assert s.current_credits == old_credits
    assert s.registered_courses == old_courses
    assert c.enrolled == old_enrolled
    assert c.waitlist == []


def test_ST04_withdraw_updates_state():
    s = mk_s(current_credits=6, registered_courses={"CS201"})
    c = mk_c(enrolled=10)

    assert withdraw_course(s, c) is True

    assert s.current_credits == 3
    assert c.enrolled == 9
    assert "CS201" not in s.registered_courses


def test_ST05_withdraw_not_registered():
    s = mk_s(current_credits=3)
    c = mk_c(enrolled=10)

    assert withdraw_course(s, c) is False

    assert s.current_credits == 3
    assert c.enrolled == 10
    assert s.registered_courses == set()


def test_ST06_decision_does_not_mutate():
    s = mk_s()
    c = mk_c(enrolled=5)

    registration_decision(s, c)

    assert s == mk_s()
    assert c == mk_c(enrolled=5)


def test_ST07_register_then_withdraw_roundtrip():
    s = mk_s()
    c = mk_c()

    register_course(s, c)
    withdraw_course(s, c)

    assert s == mk_s()
    assert c == mk_c()


def test_ST08_scenario_15_plus_3_registers():
    s = mk_s(current_credits=15)
    c = mk_c(credit_hours=3)

    assert register_course(s, c) == "REGISTERED"
    assert s.current_credits == 18
