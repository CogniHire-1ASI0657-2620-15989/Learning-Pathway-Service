Feature: Learning Pathway Generation
    As a candidate
    I want to receive a personalized learning pathway based on my skill gaps
    So that I can study only the topics required for my target job position

    # US14 - Generación de ruta de aprendizaje (Sprint 2)

    Scenario: Successfully generate a learning pathway for a valid gap analysis
        Given candidate 101 has an identified skill gap in "Docker" for job 50
        When a POST request is sent to "/api/v1/learning-paths" with job_id 50 as candidate 101
        Then the response status is 201 Created
        And the response body contains 3 recommended courses targeting "Docker"
        And the learning pathway progress is 0%

    Scenario: Generate a pathway when no skill gaps are identified
        Given candidate 102 has 100% match with job 50
        When a POST request is sent to "/api/v1/learning-paths" with job_id 50 as candidate 102
        Then the response status is 201 Created
        And the response body contains no recommended courses

    Scenario: Attempt pathway generation for a job without a gap report
        Given candidate 103 has no gap report for job 77
        When a POST request is sent to "/api/v1/learning-paths" with job_id 77 as candidate 103
        Then the response status is 404 Not Found
        And the response body contains the message "Gap report not found."

    Scenario: Requesting the pathway again returns the existing one without searching new courses
        Given candidate 101 has an identified skill gap in "Docker" for job 50
        And candidate 101 already generated the pathway for job 50
        When a POST request is sent to "/api/v1/learning-paths" with job_id 50 as candidate 101
        Then the response status is 201 Created
        And the course catalog was searched only once
