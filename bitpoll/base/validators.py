from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from zoneinfo import available_timezones


def validate_timezone(value):
    if value not in available_timezones():
        raise ValidationError(
            _("%(value)s is not a valid timezone"),
            params={"value": value},
        )
