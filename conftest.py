from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import Client
from rest_framework.test import APIClient

from legislative.models import Bill, Legislator, Vote, VoteResult


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def django_client():
    return Client()


@pytest.fixture(scope="function")
def real_csv_data(db):
    """Load the small real CSV dataset for this test and return baseline data.

    Function scope avoids polluting other tests (e.g., model unit tests) with
    preloaded IDs that could collide with hardcoded test IDs.
    """
    fixtures_dir = Path(__file__).parent / "tests" / "fixtures"
    call_command("load_data", csv_dir=str(fixtures_dir))
    john_yarmuth_id = Legislator.objects.get(name="Rep. John Yarmuth (D-KY-3)").id
    jamaal_bowman_id = Legislator.objects.get(name="Rep. Jamaal Bowman (D-NY-16)").id
    build_back_better_id = Bill.objects.get(title="H.R. 5376: Build Back Better Act").id
    infrastructure_bill_id = Bill.objects.get(
        title="H.R. 3684: Infrastructure Investment and Jobs Act"
    ).id

    return {
        "expected_legislators": Legislator.objects.count(),
        "expected_bills": Bill.objects.count(),
        "expected_votes": Vote.objects.count(),
        "expected_vote_results": VoteResult.objects.count(),
        "build_back_better_id": build_back_better_id,
        "infrastructure_bill_id": infrastructure_bill_id,
        "john_yarmuth_id": john_yarmuth_id,
        "jamaal_bowman_id": jamaal_bowman_id,
    }
