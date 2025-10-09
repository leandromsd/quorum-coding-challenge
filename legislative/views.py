from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets

from .models import Bill, Legislator, VoteResult
from .serializers import (
    BillDetailSerializer,
    BillStatsSerializer,
    LegislatorDetailSerializer,
    LegislatorStatsSerializer,
)


class LegislatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Legislator.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LegislatorDetailSerializer
        return LegislatorStatsSerializer

    def get_queryset(self):
        base_qs = Legislator.objects.all()
        if self.action == "retrieve":
            return base_qs.prefetch_related(
                Prefetch(
                    "vote_results",
                    queryset=VoteResult.objects.select_related(
                        "vote__bill", "legislator"
                    ).order_by("-id"),
                )
            ).annotate(
                supported_bills_count_annotated=Count(
                    "vote_results",
                    filter=Q(vote_results__vote_type=VoteResult.VoteType.YEA),
                ),
                opposed_bills_count_annotated=Count(
                    "vote_results",
                    filter=Q(vote_results__vote_type=VoteResult.VoteType.NAY),
                ),
            )
        else:
            return base_qs.annotate(
                supported_bills_count_annotated=Count(
                    "vote_results",
                    filter=Q(vote_results__vote_type=VoteResult.VoteType.YEA),
                ),
                opposed_bills_count_annotated=Count(
                    "vote_results",
                    filter=Q(vote_results__vote_type=VoteResult.VoteType.NAY),
                ),
            ).order_by("name")


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bill.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BillDetailSerializer
        return BillStatsSerializer

    def get_queryset(self):
        base_qs = Bill.objects.select_related("primary_sponsor")
        if self.action == "retrieve":
            return base_qs.annotate(
                supporters_count_annotated=Count(
                    "votes__results",
                    filter=Q(votes__results__vote_type=VoteResult.VoteType.YEA),
                ),
                opposers_count_annotated=Count(
                    "votes__results",
                    filter=Q(votes__results__vote_type=VoteResult.VoteType.NAY),
                ),
            )
        else:
            return base_qs.annotate(
                supporters_count_annotated=Count(
                    "votes__results",
                    filter=Q(votes__results__vote_type=VoteResult.VoteType.YEA),
                ),
                opposers_count_annotated=Count(
                    "votes__results",
                    filter=Q(votes__results__vote_type=VoteResult.VoteType.NAY),
                ),
            ).order_by("title")


def home_view(request):
    stats = {
        "legislators": Legislator.objects.count(),
        "bills": Bill.objects.count(),
        "vote_results": VoteResult.objects.count(),
    }
    return render(request, "legislative/home.html", {"stats": stats})


def legislators_view(request):
    legislators = Legislator.objects.annotate(
        supported_bills_count_annotated=Count(
            "vote_results",
            filter=Q(vote_results__vote_type=VoteResult.VoteType.YEA),
        ),
        opposed_bills_count_annotated=Count(
            "vote_results",
            filter=Q(vote_results__vote_type=VoteResult.VoteType.NAY),
        ),
    ).order_by("name")
    return render(request, "legislative/legislators.html", {"legislators": legislators})


def legislator_detail_view(request, legislator_id):
    legislator = get_object_or_404(Legislator, id=legislator_id)
    return render(
        request, "legislative/legislator_detail.html", {"legislator": legislator}
    )


def bills_view(request):
    bills = (
        Bill.objects.select_related("primary_sponsor")
        .annotate(
            supporters_count_annotated=Count(
                "votes__results",
                filter=Q(votes__results__vote_type=VoteResult.VoteType.YEA),
            ),
            opposers_count_annotated=Count(
                "votes__results",
                filter=Q(votes__results__vote_type=VoteResult.VoteType.NAY),
            ),
        )
        .order_by("title")
    )
    return render(request, "legislative/bills.html", {"bills": bills})


def bill_detail_view(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    vote_results = (
        VoteResult.objects.filter(vote__bill=bill)
        .select_related("legislator")
        .order_by("legislator__name")
    )
    return render(
        request,
        "legislative/bill_detail.html",
        {
            "bill": bill,
            "vote_results": vote_results,
        },
    )


def stats_api_view(request):
    stats = {
        "legislators": Legislator.objects.count(),
        "bills": Bill.objects.count(),
        "vote_results": VoteResult.objects.count(),
    }
    return JsonResponse(stats)
