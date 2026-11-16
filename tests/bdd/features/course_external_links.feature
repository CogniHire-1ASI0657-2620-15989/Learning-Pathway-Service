Feature: Course External Links
    As a candidate
    I want to open the suggested courses of my learning pathway
    So that I can go directly to the educational platform

    # US15 - Acceder a enlaces de cursos externos (Sprint 2)

    Scenario: Every suggested course exposes an external link
        Given candidate 101 has an identified skill gap in "Docker" for job 50
        And candidate 101 already generated the pathway for job 50
        When a GET request is sent to "/api/v1/learning-paths/50" as candidate 101
        Then the response status is 200 OK
        And every course in the pathway has an external "https://www.youtube.com/watch?v=" link

    Scenario: Attempt to open the courses of a pathway that does not exist
        When a GET request is sent to "/api/v1/learning-paths/999" as candidate 101
        Then the response status is 404 Not Found
        And the response body contains the message "Learning path not found."
