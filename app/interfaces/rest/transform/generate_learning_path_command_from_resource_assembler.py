from app.domain.model.commands.generate_learning_path_command import GenerateLearningPathCommand
from app.interfaces.rest.resources.generate_learning_path_resource import GenerateLearningPathResource


class GenerateLearningPathCommandFromResourceAssembler:
    @staticmethod
    def to_command(user_id: int, resource: GenerateLearningPathResource) -> GenerateLearningPathCommand:
        return GenerateLearningPathCommand(user_id=user_id, job_id=resource.job_id)
