"""
Tests for API endpoints using real CSV data.
"""

from django.urls import reverse
from rest_framework import status

from legislative.models import Bill, Legislator, Vote, VoteResult


class TestStatsAPI:
    """Test statistics API endpoint with real data."""

    def test_stats_endpoint(self, api_client, real_csv_data):
        """Test stats API returns correct counts from real CSV data."""
        url = reverse("stats_api")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["legislators"] == real_csv_data["expected_legislators"]
        assert data["bills"] == real_csv_data["expected_bills"]
        assert data["vote_results"] == real_csv_data["expected_vote_results"]


class TestLegislatorAPI:
    """Test legislator API endpoints with real data."""

    def test_legislators_list(self, api_client, real_csv_data):
        """Test legislators list API with real data."""
        url = "/api/legislators/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Support both paginated and non-paginated responses
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
            count = data["count"]
        else:
            results = data
            count = len(results)

        assert count == real_csv_data["expected_legislators"]
        assert len(results) == real_csv_data["expected_legislators"]

        # Check one specific legislator (John Yarmuth - sponsor of Build Back Better)
        yarmuth = next(
            (r for r in results if r["id"] == real_csv_data["john_yarmuth_id"]),
            None,
        )
        assert yarmuth is not None
        assert yarmuth["name"] == "Rep. John Yarmuth (D-KY-3)"
        # John Yarmuth sponsored Build Back Better but his vote record should be calculated
        assert yarmuth["supported_bills_count"] >= 0
        assert yarmuth["opposed_bills_count"] >= 0

    def test_legislator_detail(self, api_client, real_csv_data):
        """Test legislator detail API with real data."""
        # Test John Yarmuth (sponsor of Build Back Better)
        url = f"/api/legislators/{real_csv_data['john_yarmuth_id']}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == real_csv_data["john_yarmuth_id"]
        assert data["name"] == "Rep. John Yarmuth (D-KY-3)"
        assert "supported_bills_count" in data
        assert "opposed_bills_count" in data
        assert "vote_results" in data

    def test_legislator_not_found(self, api_client):
        """Test legislator detail API with invalid ID."""
        url = "/api/legislators/999999/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestBillAPI:
    """Test bill API endpoints with real data."""

    def test_bills_list(self, api_client, real_csv_data):
        """Test bills list API with real data."""
        url = "/api/bills/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if isinstance(data, dict) and "results" in data:
            results = data["results"]
            count = data["count"]
        else:
            results = data
            count = len(results)

        assert count == real_csv_data["expected_bills"]
        assert len(results) == real_csv_data["expected_bills"]

        # Check specific bills
        bill_ids = [r["id"] for r in results]
        assert real_csv_data["build_back_better_id"] in bill_ids
        assert real_csv_data["infrastructure_bill_id"] in bill_ids

        # Check Build Back Better Act
        bbb_bill = next(
            (r for r in results if r["id"] == real_csv_data["build_back_better_id"]),
            None,
        )
        assert bbb_bill is not None
        assert bbb_bill["title"] == "H.R. 5376: Build Back Better Act"
        assert bbb_bill["primary_sponsor"] == "Rep. John Yarmuth (D-KY-3)"
        assert bbb_bill["supporters_count"] >= 0
        assert bbb_bill["opposers_count"] >= 0

    def test_bill_detail(self, api_client, real_csv_data):
        """Test bill detail API with real data."""
        # Test Build Back Better Act
        url = f"/api/bills/{real_csv_data['build_back_better_id']}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == real_csv_data["build_back_better_id"]
        assert data["title"] == "H.R. 5376: Build Back Better Act"
        assert data["primary_sponsor"] == "Rep. John Yarmuth (D-KY-3)"
        assert "supporters_count" in data
        assert "opposers_count" in data
        assert "vote_results" in data

        # The vote results should contain actual voting data
        vote_results = data["vote_results"]
        assert len(vote_results) > 0

        # Check that all vote results have required fields
        for vote_result in vote_results:
            assert "legislator" in vote_result
            assert "is_support" in vote_result
            assert vote_result["legislator"]["id"] is not None
            assert vote_result["legislator"]["name"] is not None

    def test_infrastructure_bill_detail(self, api_client, real_csv_data):
        """Test Infrastructure Investment and Jobs Act detail."""
        url = f"/api/bills/{real_csv_data['infrastructure_bill_id']}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == real_csv_data["infrastructure_bill_id"]
        assert data["title"] == "H.R. 3684: Infrastructure Investment and Jobs Act"
        assert data["primary_sponsor"] == "Rep. Jamaal Bowman (D-NY-16)"

    def test_bill_not_found(self, api_client):
        """Test bill detail API with invalid ID."""
        url = "/api/bills/999999/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestWebInterface:
    """Test web interface views with real data."""

    def test_home_page(self, django_client, real_csv_data):
        """Test home page loads correctly with real stats."""
        response = django_client.get("/")
        assert response.status_code == 200
        content = response.content.decode()

        assert "Quorum Legislative Data" in content
        # Check that real statistics are displayed
        assert str(real_csv_data["expected_legislators"]) in content
        assert str(real_csv_data["expected_bills"]) in content

    def test_legislators_page(self, django_client, real_csv_data):
        """Test legislators page loads correctly."""
        response = django_client.get("/legislators/")
        assert response.status_code == 200
        content = response.content.decode()

        assert "Legislators" in content
        # Should contain some of the real legislator names
        assert "Rep. John Yarmuth" in content or "Rep. Jamaal Bowman" in content

    def test_bills_page(self, django_client, real_csv_data):
        """Test bills page loads correctly."""
        response = django_client.get("/bills/")
        assert response.status_code == 200
        content = response.content.decode()

        assert "Bills" in content
        # Should contain the real bill titles
        assert (
            "Build Back Better Act" in content or "Infrastructure Investment" in content
        )

    def test_legislator_detail_page(self, django_client, real_csv_data):
        """Test legislator detail page loads correctly."""
        response = django_client.get(
            f"/legislators/{real_csv_data['john_yarmuth_id']}/"
        )
        assert response.status_code == 200
        content = response.content.decode()

        assert "Rep. John Yarmuth" in content
        assert "Voting History" in content

    def test_bill_detail_page(self, django_client, real_csv_data):
        """Test bill detail page loads correctly."""
        response = django_client.get(f"/bills/{real_csv_data['build_back_better_id']}/")
        assert response.status_code == 200
        content = response.content.decode()

        assert "Build Back Better Act" in content
        assert "How Legislators Voted" in content


class TestDataIntegrity:
    """Test data integrity and relationships with real CSV data."""

    def test_bill_sponsor_relationships(self, real_csv_data):
        """Test that bill sponsors are correctly linked."""
        # Build Back Better Act should be sponsored by John Yarmuth
        bbb_bill = Bill.objects.get(id=real_csv_data["build_back_better_id"])
        assert bbb_bill.primary_sponsor.id == real_csv_data["john_yarmuth_id"]
        assert bbb_bill.primary_sponsor.name == "Rep. John Yarmuth (D-KY-3)"

        # Infrastructure bill should be sponsored by Jamaal Bowman
        infra_bill = Bill.objects.get(id=real_csv_data["infrastructure_bill_id"])
        assert infra_bill.primary_sponsor.id == real_csv_data["jamaal_bowman_id"]
        assert infra_bill.primary_sponsor.name == "Rep. Jamaal Bowman (D-NY-16)"

    def test_vote_counts_consistency(self, real_csv_data):
        """Test that vote counts are consistent across the system."""
        total_legislators = Legislator.objects.count()
        total_bills = Bill.objects.count()
        total_votes = Vote.objects.count()
        total_vote_results = VoteResult.objects.count()

        assert total_legislators == real_csv_data["expected_legislators"]
        assert total_bills == real_csv_data["expected_bills"]
        assert total_votes == real_csv_data["expected_votes"]
        assert total_vote_results == real_csv_data["expected_vote_results"]

    def test_vote_statistics_calculation(self, real_csv_data):
        """Test that vote statistics are calculated correctly."""
        # Test a few legislators' vote counts
        for legislator in Legislator.objects.all()[:3]:
            supported = legislator.supported_bills_count
            opposed = legislator.opposed_bills_count

            # Verify against actual VoteResult records
            actual_supported = VoteResult.objects.filter(
                legislator=legislator, vote_type=VoteResult.VoteType.YEA
            ).count()
            actual_opposed = VoteResult.objects.filter(
                legislator=legislator, vote_type=VoteResult.VoteType.NAY
            ).count()

            assert supported == actual_supported
            assert opposed == actual_opposed
