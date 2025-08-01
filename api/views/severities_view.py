from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status as drf_status
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes, OpenApiExample
)
from django.shortcuts import get_object_or_404

from issues.models import Severities, Issue
from ..serializers import SeveritiesSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Listar severidades",
        description="Devuelve una lista de severidades con filtrado por nombre.",
        tags=['Severities'],
        parameters=[
            OpenApiParameter(
                name='nombre',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtra las severidades cuyo nombre contenga el valor dado",
                required=False
            ),
        ],
        responses=SeveritiesSerializer(many=True),
        examples=[
            OpenApiExample(
                'SeverityListExample',
                summary="Listado de severidades",
                description="Respuesta con todas las severidades",
                value=[
                    {"id": 1, "nombre": "Critical", "slug": "critical", "color": "#FF0000"},
                    {"id": 2, "nombre": "High",     "slug": "high",     "color": "#FFA500"},
                    {"id": 3, "nombre": "Medium",   "slug": "medium",   "color": "#FFFF00"},
                    {"id": 4, "nombre": "Low",      "slug": "low",      "color": "#00FF00"},
                ],
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        tags=['Severities'],
        request=SeveritiesSerializer,
        responses=SeveritiesSerializer,
        summary="Crear una nueva severidad",
        description="Crea una nueva severidad a partir de un nombre y un color.",
        examples=[
            OpenApiExample(
                'CreateSeverityRequest',
                summary="Payload para crear",
                request_only=True,
                value={"nombre": "Blocker", "color": "#8B0000"}
            ),
            OpenApiExample(
                'CreateSeverityResponse',
                summary="Respuesta al crear",
                response_only=True,
                value={"id": 5, "nombre": "Blocker", "slug": "blocker", "color": "#8B0000"}
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=['Severities'],
        responses=SeveritiesSerializer,
        summary="Obtener una severidad dado su id",
        description="Devuelve una severidad dado su id.",
        examples=[
            OpenApiExample(
                'RetrieveSeverityExample',
                summary="Obtener una única severidad",
                response_only=True,
                value={"id": 1, "nombre": "Critical", "slug": "critical", "color": "#FF0000"}
            ),
        ],
    ),
    update=extend_schema(
        tags=['Severities'],
        request=SeveritiesSerializer,
        responses=SeveritiesSerializer,
        summary="Actualizar una severidad",
        description="Actualiza campos de una severidad existente.",
        examples=[
            OpenApiExample(
                'UpdateSeverityRequest',
                summary="Payload para actualizar",
                request_only=True,
                value={"nombre": "Major", "color": "#FF4500"}
            ),
            OpenApiExample(
                'UpdateSeverityResponse',
                summary="Respuesta al actualizar",
                response_only=True,
                value={"id": 2, "nombre": "Major", "slug": "major", "color": "#FF4500"}
            ),
        ],
    ),
    destroy=extend_schema(
        tags=['Severities'],
        responses={204: None},
        summary="Eliminar una severidad",
        description="Elimina una severidad dado su id, reasignando sus issues a 'Normal'.",
        examples=[
            OpenApiExample(
                'DeleteSeverityExample',
                summary="Eliminar una severidad",
                description="Respuesta vacía con código 204",
                response_only=True,
                value=None
            ),
        ],
    ),
)
class SeverityViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Severities.objects.all()
    serializer_class = SeveritiesSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nombre']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='nombre',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtra las severidades cuyo nombre contenga el valor dado",
                required=False
            ),
        ],
        responses=SeveritiesSerializer(many=True)
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.nombre == "Normal":
            return Response(
                {"detail": "La severidad 'Normal' no se puede editar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.nombre == "Normal":
            return Response(
                {"detail": "La severidad 'Normal' no se puede eliminar."},
                status=drf_status.HTTP_403_FORBIDDEN
            )
        normal = get_object_or_404(Severities, nombre="Normal")
        Issue.objects.filter(severity=instance).update(severity=normal)
        return super().destroy(request, *args, **kwargs)
