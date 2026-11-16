Feature: Certificate Upload
    As a candidate
    I want to upload a photo or PDF of my course diploma
    So that I can prove that I acquired the skill

    # US16 - Subir diploma o certificado (Sprint 2)

    Background:
        Given candidate 101 has an active learning pathway 7 for job 50 that includes the skill "Docker"
        And the OCR reads the text "Certificado de finalización otorgado a Ana Perez por el curso de Docker" from the diploma

    Scenario: Successfully upload a valid PDF diploma for OCR analysis
        When the candidate uploads a valid PDF diploma for skill "Docker" to "/api/v1/certificates"
        Then the response status is 201 Created
        And the certificate is registered for skill "Docker" in learning pathway 7

    Scenario: Attempt to upload an oversized certificate file
        When the candidate uploads a PDF diploma larger than 5 MB for skill "Docker"
        Then the response status is 422 Unprocessable Entity
        And the response body contains the message "El archivo del certificado no puede superar 5 MB."

    Scenario: Attempt to upload a file with an unsupported format
        When the candidate uploads a "text/plain" file for skill "Docker"
        Then the response status is 422 Unprocessable Entity
        And the response body contains the message "Solo se aceptan certificados PDF, JPG o PNG."

    Scenario: Attempt to upload a diploma for a skill outside the learning pathway
        When the candidate uploads a valid PDF diploma for skill "Kubernetes" to "/api/v1/certificates"
        Then the response status is 404 Not Found
        And the response body contains the message "The certificate skill is not part of the learning path."
