"""
Validation tests for the load_data management command.

These tests create minimal CSV directories to trigger friendly
CommandError messages for invalid inputs.
"""

from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def write_csv(path: Path, name: str, content: str) -> None:
    p = path / name
    p.write_text(content)


@pytest.fixture()
def csv_dir(tmp_path: Path) -> Path:
    d = tmp_path / "csv"
    d.mkdir()
    return d


def test_legislators_missing_column(csv_dir: Path):
    # Missing 'name' column in legislators.csv
    write_csv(csv_dir, "legislators.csv", "id\n1\n")
    write_csv(csv_dir, "bills.csv", "id,title,sponsor_id\n10,Bill A,1\n")
    write_csv(csv_dir, "votes.csv", "id,bill_id\n100,10\n")
    write_csv(
        csv_dir,
        "vote_results.csv",
        "id,legislator_id,vote_id,vote_type\n1000,1,100,1\n",
    )

    with pytest.raises(CommandError) as exc:
        call_command("load_data", csv_dir=str(csv_dir))
    assert "Missing required columns in legislators.csv" in str(exc.value)


def test_bills_missing_primary_sponsor(csv_dir: Path):
    write_csv(csv_dir, "legislators.csv", "id,name\n1,Rep A\n")
    # sponsor_id 999 does not exist
    write_csv(csv_dir, "bills.csv", "id,title,sponsor_id\n10,Bill A,999\n")
    write_csv(csv_dir, "votes.csv", "id,bill_id\n100,10\n")
    write_csv(
        csv_dir,
        "vote_results.csv",
        "id,legislator_id,vote_id,vote_type\n1000,1,100,1\n",
    )

    with pytest.raises(CommandError) as exc:
        call_command("load_data", csv_dir=str(csv_dir))
    assert "Primary sponsor with id=999 not found" in str(exc.value)


def test_votes_missing_bill(csv_dir: Path):
    write_csv(csv_dir, "legislators.csv", "id,name\n1,Rep A\n")
    write_csv(csv_dir, "bills.csv", "id,title,sponsor_id\n10,Bill A,1\n")
    # bill_id 999 does not exist
    write_csv(csv_dir, "votes.csv", "id,bill_id\n100,999\n")
    write_csv(
        csv_dir,
        "vote_results.csv",
        "id,legislator_id,vote_id,vote_type\n1000,1,100,1\n",
    )

    with pytest.raises(CommandError) as exc:
        call_command("load_data", csv_dir=str(csv_dir))
    assert "Bill with id=999 not found" in str(exc.value)


def test_vote_results_missing_legislator(csv_dir: Path):
    write_csv(csv_dir, "legislators.csv", "id,name\n1,Rep A\n")
    write_csv(csv_dir, "bills.csv", "id,title,sponsor_id\n10,Bill A,1\n")
    write_csv(csv_dir, "votes.csv", "id,bill_id\n100,10\n")
    # legislator_id 999 does not exist
    write_csv(
        csv_dir,
        "vote_results.csv",
        "id,legislator_id,vote_id,vote_type\n1000,999,100,1\n",
    )

    with pytest.raises(CommandError) as exc:
        call_command("load_data", csv_dir=str(csv_dir))
    assert "Legislator with id=999 not found" in str(exc.value)


def test_vote_results_invalid_vote_type(csv_dir: Path):
    write_csv(csv_dir, "legislators.csv", "id,name\n1,Rep A\n")
    write_csv(csv_dir, "bills.csv", "id,title,sponsor_id\n10,Bill A,1\n")
    write_csv(csv_dir, "votes.csv", "id,bill_id\n100,10\n")
    # invalid vote_type 3
    write_csv(
        csv_dir,
        "vote_results.csv",
        "id,legislator_id,vote_id,vote_type\n1000,1,100,3\n",
    )

    with pytest.raises(CommandError) as exc:
        call_command("load_data", csv_dir=str(csv_dir))
    assert "Invalid vote_type" in str(exc.value)
