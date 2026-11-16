Feature: Certificate Validation Error Handling
    As a candidate
    I want to be notified when my diploma could not be read or is invalid
    So that I can try uploading it again

    # US18 - Manejo de error en validación de diploma (Sprint 2)

    Background:
        Given candidate 101 has an active learning pathway 7 for job 50 that includes the skill "Docker"

    Scenario: Unreadable diploma is reported to the candidate
        Given the OCR reads the text "" from the diploma
        When the candidate uploads a valid PDF diploma for skill "Docker" to "/api/v1/certificates"
        Then the response status is 201 Created
        And the certificate status is "unreadable"
        And the certificate validation detail is "No se pudo extraer texto suficiente del certificado."

    Scenario: The candidate can check the result of an unreadable diploma later
        Given the OCR reads the text "" from the diploma
        And the candidate uploaded a diploma for skill "Docker"
        When the candidate requests the uploaded certificate from "/api/v1/certificates/{id}"
        Then the response status is 200 OK
        And the certificate status is "unreadable"

    Scenario: Profile synchronization failure can be retried
        Given the OCR reads the text "Certificado de finalización otorgado a Ana Perez por el curso de Docker" from the diploma
        And the Identity Service is unavailable
        And the candidate uploaded a diploma for skill "Docker"
        And the Identity Service becomes available again
        When the candidate retries the synchronization at "/api/v1/certificates/{id}/synchronization"
        Then the response status is 200 OK
        And the certificate status is "approved"
        And the certificate profile synchronization status is "synchronized"
