"""
Django REST Framework serializers for legislative data.

These serializers handle the conversion between Django model instances
and JSON representations for the API endpoints.
"""

from rest_framework import serializers

from .models import Bill, Legislator, VoteResult


class LegislatorSerializer(serializers.ModelSerializer):
    """Serializer for basic legislator information."""

    class Meta:
        model = Legislator
        fields = ["id", "name"]


class LegislatorStatsSerializer(serializers.ModelSerializer):
    """Serializer for legislator with voting statistics.

    Falls back to model properties if annotated fields are not present,
    keeping it robust outside annotated querysets.
    """

    supported_bills_count = serializers.SerializerMethodField()
    opposed_bills_count = serializers.SerializerMethodField()

    class Meta:
        model = Legislator
        fields = ["id", "name", "supported_bills_count", "opposed_bills_count"]

    def get_supported_bills_count(self, obj):
        annotated = getattr(obj, "supported_bills_count_annotated", None)
        return int(annotated) if annotated is not None else obj.supported_bills_count

    def get_opposed_bills_count(self, obj):
        annotated = getattr(obj, "opposed_bills_count_annotated", None)
        return int(annotated) if annotated is not None else obj.opposed_bills_count


class BillSerializer(serializers.ModelSerializer):
    """Serializer for basic bill information."""

    primary_sponsor_name = serializers.CharField(
        source="primary_sponsor.name", read_only=True
    )

    class Meta:
        model = Bill
        fields = ["id", "title", "primary_sponsor", "primary_sponsor_name"]


class BillStatsSerializer(serializers.ModelSerializer):
    """Serializer for bill with voting statistics.

    Count fields gracefully fall back to model properties when annotations
    are not available.
    """

    primary_sponsor = serializers.CharField(
        source="primary_sponsor.name", read_only=True
    )
    primary_sponsor_id = serializers.IntegerField(
        source="primary_sponsor.id", read_only=True
    )
    supporters_count = serializers.SerializerMethodField()
    opposers_count = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            "id",
            "title",
            "primary_sponsor",
            "primary_sponsor_id",
            "supporters_count",
            "opposers_count",
        ]

    def get_supporters_count(self, obj):
        annotated = getattr(obj, "supporters_count_annotated", None)
        return int(annotated) if annotated is not None else obj.supporters_count

    def get_opposers_count(self, obj):
        annotated = getattr(obj, "opposers_count_annotated", None)
        return int(annotated) if annotated is not None else obj.opposers_count


class VoteDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed vote information."""

    legislator_name = serializers.CharField(source="legislator.name", read_only=True)
    bill_id = serializers.IntegerField(source="vote.bill.id", read_only=True)
    bill_title = serializers.CharField(source="vote.bill.title", read_only=True)
    vote_type_display = serializers.CharField(
        source="get_vote_type_display", read_only=True
    )

    class Meta:
        model = VoteResult
        fields = [
            "id",
            "legislator",
            "legislator_name",
            "bill_id",
            "bill_title",
            "vote_type",
            "vote_type_display",
            "is_support",
            "is_oppose",
        ]


class LegislatorDetailSerializer(LegislatorStatsSerializer):
    """Serializer for detailed legislator information with vote history."""

    vote_results = serializers.SerializerMethodField()

    class Meta:
        model = Legislator
        fields = [
            "id",
            "name",
            "supported_bills_count",
            "opposed_bills_count",
            "vote_results",
        ]

    def get_vote_results(self, obj):
        """Get voting history for this legislator.

        Uses prefetched results from the view when available to avoid
        extra queries.
        """
        vote_results = obj.vote_results.all()
        return [
            {
                "bill": {
                    "id": vr.vote.bill.id,
                    "title": vr.vote.bill.title,
                },
                "is_support": vr.is_support,
                "legislator": {
                    "id": obj.id,
                    "name": obj.name,
                },
            }
            for vr in vote_results
        ]


class BillDetailSerializer(BillStatsSerializer):
    """Serializer for detailed bill information with vote breakdown."""

    vote_results = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            "id",
            "title",
            "primary_sponsor",
            "primary_sponsor_id",
            "supporters_count",
            "opposers_count",
            "vote_results",
        ]

    def get_vote_results(self, obj):
        """Get all vote results for this bill."""
        vote_results = (
            VoteResult.objects.filter(vote__bill=obj)
            .select_related("legislator")
            .order_by("legislator__name")
        )
        return [
            {
                "legislator": {
                    "id": vr.legislator.id,
                    "name": vr.legislator.name,
                },
                "is_support": vr.is_support,
            }
            for vr in vote_results
        ]
