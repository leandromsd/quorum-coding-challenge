"""
Django models for legislative data structures.

Models for legislators, bills, votes, and vote results with optimized queries.
"""

from django.db import models


class Legislator(models.Model):
    """Represents an individual legislator elected to government."""

    name = models.CharField(max_length=200, help_text="Full name of the legislator")

    class Meta:
        db_table = "legislative_legislator"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def supported_bills_count(self):
        """Count of bills this legislator has supported."""
        return self.vote_results.filter(vote_type=VoteResult.VoteType.YEA).count()

    @property
    def opposed_bills_count(self):
        """Count of bills this legislator has opposed."""
        return self.vote_results.filter(vote_type=VoteResult.VoteType.NAY).count()


class Bill(models.Model):
    """Represents a piece of legislation introduced in Congress."""

    title = models.CharField(max_length=500, help_text="Title of the bill")
    primary_sponsor = models.ForeignKey(
        Legislator,
        on_delete=models.CASCADE,
        related_name="sponsored_bills",
        help_text="Primary sponsor of this bill",
    )

    class Meta:
        db_table = "legislative_bill"
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def supporters_count(self):
        """Count of legislators who supported this bill."""
        return VoteResult.objects.filter(
            vote__bill=self, vote_type=VoteResult.VoteType.YEA
        ).count()

    @property
    def opposers_count(self):
        """Count of legislators who opposed this bill."""
        return VoteResult.objects.filter(
            vote__bill=self, vote_type=VoteResult.VoteType.NAY
        ).count()


class Vote(models.Model):
    """Represents a voting session on a particular bill."""

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="votes",
        help_text="Bill being voted on",
    )

    class Meta:
        db_table = "legislative_vote"

    def __str__(self):
        return f"Vote #{self.id} on {self.bill.title}"


class VoteResult(models.Model):
    """Represents an individual vote cast by a legislator."""

    class VoteType(models.TextChoices):
        YEA = "1", "Yea"
        NAY = "2", "Nay"

    legislator = models.ForeignKey(
        Legislator,
        on_delete=models.CASCADE,
        related_name="vote_results",
        help_text="Legislator who cast this vote",
    )
    vote = models.ForeignKey(
        Vote,
        on_delete=models.CASCADE,
        related_name="results",
        help_text="Vote session this result belongs to",
    )
    vote_type = models.CharField(
        max_length=1,
        choices=VoteType.choices,
        help_text="Vote type: Yea (support) or Nay (oppose)",
    )

    class Meta:
        db_table = "legislative_vote_result"
        indexes = [
            models.Index(fields=["vote_type"]),
            models.Index(fields=["vote", "vote_type"]),
            models.Index(fields=["legislator", "vote_type"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["legislator", "vote"], name="unique_legislator_vote"
            )
        ]

    def __str__(self):
        return f"{self.legislator.name} voted {self.get_vote_type_display()} on {self.vote.bill.title}"

    @property
    def is_support(self):
        """Check if this is a supporting vote."""
        return self.vote_type == self.VoteType.YEA

    @property
    def is_oppose(self):
        """Check if this is an opposing vote."""
        return self.vote_type == self.VoteType.NAY
