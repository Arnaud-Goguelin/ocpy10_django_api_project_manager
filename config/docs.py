# variables created for docs precisions
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

project_id_parameter = OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Project ID'
            )

issue_id_parameter = OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Issue ID'
            )

comment_id_parameter = OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Comment ID'
            )
