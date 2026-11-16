Feature: Learning Pathway Progress Tracking
    As a candidate
    I want to view a general progress bar of my learning pathway
    So that I can maintain motivation during my study plan

    # US19 - Ver barra de progreso general (Sprint 3)

    Scenario: View progress percentage of a partially completed pathway
        Given pathway 7 of candidate 101 has 4 courses and 2 of them are completed
        When a GET request is sent to "/api/v1/learning-paths/7/progress" as candidate 101
        Then the response status is 200 OK
        And the progress shows 2 of 4 courses completed with 50%
        And the pathway status is "active"

    Scenario: View progress of a pathway that has not started
        Given pathway 8 of candidate 102 has 2 courses and 0 of them are completed
        When a GET request is sent to "/api/v1/learning-paths/8/progress" as candidate 102
        Then the response status is 200 OK
        And the progress shows 0 of 2 courses completed with 0%

    Scenario: Completing the last course finishes the pathway
        Given pathway 9 of candidate 101 has 2 courses and 1 of them are completed
        When the candidate marks course 2 of pathway 9 as completed as candidate 101
        Then the response status is 200 OK
        And the response progress is 100%
        And the pathway status is "completed"

    Scenario: A candidate cannot see the progress of another candidate's pathway
        Given pathway 7 of candidate 101 has 4 courses and 2 of them are completed
        When a GET request is sent to "/api/v1/learning-paths/7/progress" as candidate 999
        Then the response status is 404 Not Found
        And the response body contains the message "Learning path not found."
