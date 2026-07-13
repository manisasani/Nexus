import pytest
from apps.projects.serializers import ProjectCreateSerializer


@pytest.mark.django_db
class TestProjectSerializerValidation:
    def test_negative_budget_rejected(self):
        serializer = ProjectCreateSerializer(data={
            "title": "Test",
            "description": "desc",
            "budget": "-10.00",
            "deadline": "2027-01-01",
        })
        assert not serializer.is_valid()
        assert "budget" in serializer.errors

    def test_zero_budget_rejected(self):
        serializer = ProjectCreateSerializer(data={
            "title": "Test",
            "description": "desc",
            "budget": "0.00",
            "deadline": "2027-01-01",
        })
        assert not serializer.is_valid()
        assert "budget" in serializer.errors

    def test_past_deadline_rejected(self):
        serializer = ProjectCreateSerializer(data={
            "title": "Test",
            "description": "desc",
            "budget": "100.00",
            "deadline": "2020-01-01",
        })
        assert not serializer.is_valid()
        assert "deadline" in serializer.errors

    def test_valid_data_accepted(self):
        serializer = ProjectCreateSerializer(data={
            "title": "Test",
            "description": "desc",
            "budget": "100.00",
            "deadline": "2027-01-01",
        })
        assert serializer.is_valid(), serializer.errors