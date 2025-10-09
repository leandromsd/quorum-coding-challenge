"""
Tests for legislative models.
"""

import pytest

from legislative.models import Bill, Legislator, Vote, VoteResult


@pytest.fixture
def sample_legislator():
    """Create a sample legislator for tests."""
    return Legislator.objects.create(id=123, name="Test Rep (D-CA-01)")


@pytest.fixture
def sample_sponsor():
    """Create a sample sponsor for tests."""
    return Legislator.objects.create(id=456, name="Bill Sponsor (R-TX-02)")


@pytest.fixture
def sample_bill(sample_sponsor):
    """Create a sample bill for tests."""
    return Bill.objects.create(
        id=789, title="Test Bill Title", primary_sponsor=sample_sponsor
    )


@pytest.fixture
def sample_vote(sample_bill):
    """Create a sample vote for tests."""
    return Vote.objects.create(id=300, bill=sample_bill)


@pytest.fixture
def sample_vote_result(sample_legislator, sample_vote):
    """Create a sample vote result for tests."""
    return VoteResult.objects.create(
        id=555,
        legislator=sample_legislator,
        vote=sample_vote,
        vote_type=VoteResult.VoteType.YEA,
    )


class TestLegislatorModel:
    """Test Legislator model."""

    def test_legislator_creation(self, sample_legislator):
        """Test legislator is created correctly."""
        assert sample_legislator.id == 123
        assert sample_legislator.name == "Test Rep (D-CA-01)"
        assert str(sample_legislator) == "Test Rep (D-CA-01)"

    def test_supported_bills_count_empty(self, sample_legislator):
        """Test supported bills count when no votes."""
        assert sample_legislator.supported_bills_count == 0

    def test_opposed_bills_count_empty(self, sample_legislator):
        """Test opposed bills count when no votes."""
        assert sample_legislator.opposed_bills_count == 0


class TestBillModel:
    """Test Bill model."""

    def test_bill_creation(self, sample_bill, sample_sponsor):
        """Test bill is created correctly."""
        assert sample_bill.id == 789
        assert sample_bill.title == "Test Bill Title"
        assert sample_bill.primary_sponsor == sample_sponsor
        assert str(sample_bill) == "Test Bill Title"

    def test_supporters_count_empty(self, sample_bill):
        """Test supporters count when no votes."""
        assert sample_bill.supporters_count == 0

    def test_opposers_count_empty(self, sample_bill):
        """Test opposers count when no votes."""
        assert sample_bill.opposers_count == 0


class TestVoteModel:
    """Test Vote model."""

    def test_vote_creation(self, sample_vote, sample_bill):
        """Test vote is created correctly."""
        assert sample_vote.id == 300
        assert sample_vote.bill == sample_bill
        assert str(sample_vote) == f"Vote #{sample_vote.id} on {sample_bill.title}"


class TestVoteResultModel:
    """Test VoteResult model."""

    def test_vote_result_yea(self, sample_vote_result):
        """Test vote result with Yea vote."""
        assert sample_vote_result.vote_type == VoteResult.VoteType.YEA
        assert sample_vote_result.is_support is True
        assert sample_vote_result.is_oppose is False

    def test_vote_result_nay(self, sample_legislator, sample_vote):
        """Test vote result with Nay vote."""
        vote_result = VoteResult.objects.create(
            id=666,
            legislator=sample_legislator,
            vote=sample_vote,
            vote_type=VoteResult.VoteType.NAY,
        )

        assert vote_result.vote_type == VoteResult.VoteType.NAY
        assert vote_result.is_support is False
        assert vote_result.is_oppose is True

    def test_vote_result_str(self, sample_vote_result):
        """Test vote result string representation."""
        expected = f"{sample_vote_result.legislator.name} voted {sample_vote_result.get_vote_type_display()} on {sample_vote_result.vote.bill.title}"
        assert str(sample_vote_result) == expected


class TestVotingStatistics:
    """Test voting statistics calculations."""

    @pytest.fixture
    def voting_setup(self):
        """Set up test data with votes."""
        # Create legislators
        legislator1 = Legislator.objects.create(id=1001, name="Rep A")
        legislator2 = Legislator.objects.create(id=1002, name="Rep B")
        legislator3 = Legislator.objects.create(id=1003, name="Rep C")

        # Create bill
        bill = Bill.objects.create(
            id=2001, title="Test Statistics Bill", primary_sponsor=legislator1
        )

        # Create vote
        vote = Vote.objects.create(id=3001, bill=bill)

        # Create vote results
        VoteResult.objects.create(
            id=4001,
            legislator=legislator1,
            vote=vote,
            vote_type=VoteResult.VoteType.YEA,
        )
        VoteResult.objects.create(
            id=4002,
            legislator=legislator2,
            vote=vote,
            vote_type=VoteResult.VoteType.YEA,
        )
        VoteResult.objects.create(
            id=4003,
            legislator=legislator3,
            vote=vote,
            vote_type=VoteResult.VoteType.NAY,
        )

        return {
            "legislator1": legislator1,
            "legislator2": legislator2,
            "legislator3": legislator3,
            "bill": bill,
            "vote": vote,
        }

    def test_bill_vote_counts(self, voting_setup):
        """Test bill supporters and opposers counts."""
        bill = voting_setup["bill"]
        assert bill.supporters_count == 2
        assert bill.opposers_count == 1

    def test_legislator_vote_counts(self, voting_setup):
        """Test legislator supported and opposed bills counts."""
        legislator1 = voting_setup["legislator1"]
        legislator3 = voting_setup["legislator3"]

        # Legislator 1 voted YEA
        assert legislator1.supported_bills_count == 1
        assert legislator1.opposed_bills_count == 0

        # Legislator 3 voted NAY
        assert legislator3.supported_bills_count == 0
        assert legislator3.opposed_bills_count == 1
