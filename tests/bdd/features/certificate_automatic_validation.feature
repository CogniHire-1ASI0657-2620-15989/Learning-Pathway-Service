Feature: Certificate Automatic Validation
    As a candidate
    I want my diploma to be validated automatically through computer vision
    So that my progress is updated without waiting for a human review

    # US17 - Validación automática por OCR (Sprint 2)

    Background:
        Given candidate 101 has an active learning pathway 7 for job 50 that includes the skill "Docker"

    Scenario: Skill is verified after a legible diploma matches the profile name
        Given the OCR reads the text "Certificado de finalización otorgado a Ana Perez por el curso de Docker" from the diploma
        When the candidate uploads a valid PDF diploma for skill "Docker" to "/api/v1/certificates"
        Then the response status is 201 Created
        And the certificate status is "approved"
        And the skill "Docker" is registered as verified in the candidate profile
        And the gap report of job 50 is recalculated

    Scenario: Diploma issued to a different person is not approved
        Given the OCR reads the text "Certificado de finalización otorgado a Luis Torres por el curso de Docker" from the diploma
        When the candidate uploads a valid PDF diploma for skill "Docker" to "/api/v1/certificates"
        Then the response status is 201 Created
        And the certificate status is "name_mismatch"
        And the certificate validation detail is "El nombre del certificado no coincide con el perfil del usuario."
        And no skill is registered as verified in the candidate profile

    Scenario: Diploma that does not mention the pathway skill is not approved
        Given the OCR reads the text "Certificado de finalización otorgado a Ana Perez por el curso de Excel" from the diploma
        When the candidate uploads a valid PDF diploma for skill "Docker" to "/api/v1/certificates"
        Then the response status is 201 Created
        And the certificate status is "course_mismatch"
        And no skill is registered as verified in the candidate profile
