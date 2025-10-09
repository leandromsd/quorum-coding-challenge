"""
Tests for management commands using real CSV data.
"""

from django.core.management import call_command

from legislative.models import Bill, Legislator, Vote, VoteResult


class TestLoadDataCommand:
    """Test load_data management command with real CSV files."""

    def test_load_data_success(self):
        """Test successful CSV loading with real data."""
        # Ensure database is clean first
        VoteResult.objects.all().delete()
        Vote.objects.all().delete()
        Bill.objects.all().delete()
        Legislator.objects.all().delete()

        # Load data
        call_command("load_data")

        # Verify expected counts from real CSV files
        assert Legislator.objects.count() == 20  # legislators.csv has 20 entries
        assert Bill.objects.count() == 2  # bills.csv has 2 entries
        assert Vote.objects.count() == 2  # votes.csv has 2 entries
        assert VoteResult.objects.count() == 38  # vote_results.csv has 38 entries

        # Verify specific data integrity
        # John Yarmuth should be the sponsor of Build Back Better Act
        yarmuth = Legislator.objects.get(id=412211)
        assert yarmuth.name == "Rep. John Yarmuth (D-KY-3)"

        bbb_bill = Bill.objects.get(id=2952375)
        assert bbb_bill.title == "H.R. 5376: Build Back Better Act"
        assert bbb_bill.primary_sponsor == yarmuth

        # Jamaal Bowman should be the sponsor of Infrastructure Investment and Jobs Act
        bowman = Legislator.objects.get(id=1603850)
        assert bowman.name == "Rep. Jamaal Bowman (D-NY-16)"

        infra_bill = Bill.objects.get(id=2900994)
        assert infra_bill.title == "H.R. 3684: Infrastructure Investment and Jobs Act"
        assert infra_bill.primary_sponsor == bowman

    def test_load_data_idempotent(self):
        """Test that running load_data multiple times produces same result."""
        # First load
        call_command("load_data")
        first_legislators = Legislator.objects.count()
        first_bills = Bill.objects.count()
        first_votes = Vote.objects.count()
        first_vote_results = VoteResult.objects.count()

        # Second load (should clear and reload)
        call_command("load_data")
        second_legislators = Legislator.objects.count()
        second_bills = Bill.objects.count()
        second_votes = Vote.objects.count()
        second_vote_results = VoteResult.objects.count()

        # Counts should be identical
        assert first_legislators == second_legislators == 20
        assert first_bills == second_bills == 2
        assert first_votes == second_votes == 2
        assert first_vote_results == second_vote_results == 38
