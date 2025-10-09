"""
Load legislative data from CSV files with friendly validation errors.
"""

import os

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from legislative.models import Bill, Legislator, Vote, VoteResult


class Command(BaseCommand):
    help = "Load legislative data from CSV files"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_path = getattr(settings, "CSV_DATA_PATH", "csv_data/")

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-dir",
            dest="csv_dir",
            help="Directory containing CSV files (defaults to settings.CSV_DATA_PATH)",
        )

    def handle(self, *args, **options):
        csv_path = options.get("csv_dir") or self.csv_path
        try:
            with transaction.atomic():
                self._clear_data()

                self._load_legislators(csv_path)
                self._load_bills(csv_path)
                self._load_votes(csv_path)
                self._load_vote_results(csv_path)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Loaded: {Legislator.objects.count()} legislators, "
                        f"{Bill.objects.count()} bills, {Vote.objects.count()} votes, "
                        f"{VoteResult.objects.count()} vote results"
                    )
                )
        except FileNotFoundError as e:
            raise CommandError(f"CSV file not found: {e}") from e
        except pd.errors.EmptyDataError as e:
            raise CommandError("One of the CSV files is empty or invalid.") from e

    def _clear_data(self):
        VoteResult.objects.all().delete()
        Vote.objects.all().delete()
        Bill.objects.all().delete()
        Legislator.objects.all().delete()

    def _require_columns(self, df: pd.DataFrame, required: list[str], filename: str):
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise CommandError(
                f"Missing required columns in {filename}: {', '.join(missing)}"
            )

    def _load_legislators(self, csv_path: str):
        filename = "legislators.csv"
        df = pd.read_csv(os.path.join(csv_path, filename))
        self._require_columns(df, ["id", "name"], filename)
        legislators = [
            Legislator(id=row["id"], name=row["name"]) for _, row in df.iterrows()
        ]
        Legislator.objects.bulk_create(legislators)

    def _load_bills(self, csv_path: str):
        filename = "bills.csv"
        df = pd.read_csv(os.path.join(csv_path, filename))
        self._require_columns(df, ["id", "title", "sponsor_id"], filename)
        bills = []
        for _, row in df.iterrows():
            try:
                primary_sponsor = Legislator.objects.get(id=row["sponsor_id"])
            except Legislator.DoesNotExist as e:
                raise CommandError(
                    f"Primary sponsor with id={row['sponsor_id']} not found (from {filename})."
                ) from e
            bills.append(
                Bill(id=row["id"], title=row["title"], primary_sponsor=primary_sponsor)
            )
        Bill.objects.bulk_create(bills)

    def _load_votes(self, csv_path: str):
        filename = "votes.csv"
        df = pd.read_csv(os.path.join(csv_path, filename))
        self._require_columns(df, ["id", "bill_id"], filename)
        votes = []
        for _, row in df.iterrows():
            try:
                bill = Bill.objects.get(id=row["bill_id"])
            except Bill.DoesNotExist as e:
                raise CommandError(
                    f"Bill with id={row['bill_id']} not found (from {filename})."
                ) from e
            votes.append(Vote(id=row["id"], bill=bill))
        Vote.objects.bulk_create(votes)

    def _load_vote_results(self, csv_path: str):
        filename = "vote_results.csv"
        df = pd.read_csv(os.path.join(csv_path, filename))
        self._require_columns(
            df, ["id", "legislator_id", "vote_id", "vote_type"], filename
        )
        vote_results = []
        for _, row in df.iterrows():
            try:
                legislator = Legislator.objects.get(id=row["legislator_id"])
            except Legislator.DoesNotExist as e:
                raise CommandError(
                    f"Legislator with id={row['legislator_id']} not found (from {filename})."
                ) from e
            try:
                vote = Vote.objects.get(id=row["vote_id"])
            except Vote.DoesNotExist as e:
                raise CommandError(
                    f"Vote with id={row['vote_id']} not found (from {filename})."
                ) from e
            vt = str(row["vote_type"]).strip()
            if vt not in {"1", "2"}:
                raise CommandError(
                    f"Invalid vote_type '{row['vote_type']}' for vote_result id={row['id']} (expected 1 or 2)."
                )
            vote_results.append(
                VoteResult(
                    id=row["id"],
                    legislator=legislator,
                    vote=vote,
                    vote_type=vt,
                )
            )
        VoteResult.objects.bulk_create(vote_results)
