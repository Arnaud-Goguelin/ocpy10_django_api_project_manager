# variables created for docs precisions
from enum import Enum

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter


class DocsTypingParameters(Enum):
    project_id = OpenApiParameter(
                    name='id',
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description='Project ID'
                )

    issue_id = OpenApiParameter(
                    name='id',
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description='Issue ID'
                )

    comment_id = OpenApiParameter(
                    name='id',
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description='Comment ID'
                )
