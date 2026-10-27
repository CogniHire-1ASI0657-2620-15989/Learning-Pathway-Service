from abc import ABC, abstractmethod

from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.commands.generate_learning_path_command import GenerateLearningPathCommand
from app.domain.model.commands.mark_learning_path_item_watched_command import MarkLearningPathItemWatchedCommand


class LearningPathCommandService(ABC):
    @abstractmethod
    async def handle_generate(self, command: GenerateLearningPathCommand) -> LearningPath: ...

    @abstractmethod
    async def handle_mark_item_watched(self, command: MarkLearningPathItemWatchedCommand) -> LearningPath: ...
