# variables created for docs precisions
from enum import Enum

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter


class DocsTypingParameters(Enum):
    user_id = OpenApiParameter(
        name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="User id"
    )

    contributor_id = OpenApiParameter(
        name="contributor_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="Contributor id"
    )

    project_id = OpenApiParameter(
        name="project_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="Project id"
    )

    issue_id = OpenApiParameter(
        name="issue_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="Issue id"
    )

    comment_id = OpenApiParameter(
        name="comment_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="Comment id"
    )
