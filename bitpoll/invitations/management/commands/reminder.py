from datetime import timedelta

from bitpoll.base.models import BitpollUser
from bitpoll.poll.models import Choice, Poll
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

ALLOW_EDIT_HOURS: timedelta = timedelta(days=settings.POLL_ALLOW_EDIT_DAYS + 1)


class Command(BaseCommand):
    help = """Query all active polls that lock voting after the choice
    "date for invited users of the specified group(s) that didn't cast their vote yet.
    "Only choices that will be locked in the next <n-days>-days will be considered.
    "The affected users will receive an email notification. (command fails hard on error)"""

    def add_arguments(self, parser):
        parser.add_argument("user-groups", nargs="+", type=str)
        parser.add_argument("n-days", type=int)

    def handle(self, *args, **options):
        for poll in Poll.objects.filter(
            change_vote_after_event=False, type__in=["datetime", "date"]
        ):
            print(f"Found poll with unchangeable votes: {poll}")
            for expiring_choice in poll.choice_set.filter(
                date__gt=timezone.now(),
                date__lte=timezone.now() + timedelta(days=options["n-days"]),
                deleted=False,
            ):
                print(f"Found expiring option in this poll: {expiring_choice}")
                for invitation in poll.invitation_set.all():
                    if (
                        invitation.user.groups.filter(
                            name__in=options["user-groups"]
                        ).exists()
                        and not invitation.user.vote_set.filter(
                            votechoice__choice=expiring_choice
                        ).exists()
                    ):
                        self.send_reminder(
                            invitation.user,
                            poll,
                            expiring_choice,
                            (expiring_choice.date - timezone.now()),
                            poll.type == "date",
                        )

    # TODO: Currently, all reminders are sent in german.
    def send_reminder(
        self,
        user: BitpollUser,
        poll: Poll,
        choice: Choice,
        time_range: timedelta,
        date_only: bool,
    ):
        link = reverse("poll_vote", args=(poll.url,))
        user_name = user.displayname or user.get_full_name() or user.username
        edit_range = ALLOW_EDIT_HOURS + time_range
        email_content = render_to_string(
            "poll/mail_reminder.txt",
            {
                "receiver_name": user_name,
                "poll_name": poll.title,
                "choice_name": choice.text,
                "poll_link": link,
                "choice_date": choice.date,
                "time_hours": int(edit_range.days * 24 + edit_range.seconds / 3600),
                "time_after_date": int(
                    ALLOW_EDIT_HOURS.days * 24 + ALLOW_EDIT_HOURS.seconds / 3600
                ),
                "date_only": date_only,
            },
        )
        print(f"Sending reminder to {user_name} for {poll.title} - {choice.text}")
        send_mail(
            f"Zeit läuft ab: Abstimmung {poll.title} - {choice.text}",
            email_content,
            None,
            [user.email],
        )
