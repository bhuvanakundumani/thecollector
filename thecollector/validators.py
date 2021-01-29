from wtforms.validators import ValidationError
import math


class RelativeNumberRange(object):
    """
    Validates that a number is of a minimum and/or maximum value.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param min:
        The minimum required value of the number or a another field's value.
        If a string field is provided, the length of it will be used.
        If not provided, minimum value will not be checked.
    :param max:
        The maximum required value of the number or a another field's value.
        If a string field is provided, the length of it will be used.
        If not provided, maximum value will not be checked.
    :param exclusive:
        If exclusive is True, equal min and max will throw error as well.
    :param allow_empty:
        If True, an empty field won't trigger the validation.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)s` and `%(max)s` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """

    def __init__(
        self,
        min=None,
        max=None,
        exclusive=False,
        allow_empty=False,
        message=None,
    ):
        self.min = min
        self.max = max
        self.exclusive = exclusive
        self.allow_empty = allow_empty
        self.message = message

    def __call__(self, form, field):
        data, max, min = field.data, self.max, self.min
        if not isinstance(self.min, (int, float, complex)):
            try:
                min = form[self.min].data
                if isinstance(min, str):
                    min = len(min)
            except KeyError:
                raise ValidationError(
                    field.gettext("Invalid field name '%s'.") % self.min
                )
        if not isinstance(self.max, (int, float, complex)):
            try:
                max = form[self.max].data
                if isinstance(max, str):
                    max = len(max)
            except KeyError:
                raise ValidationError(
                    field.gettext("Invalid field name '%s'.") % self.max
                )
        if not (  # only run validation if allow_empty is False or data is given
            self.allow_empty and (data is None or data == "")
        ) and (
            data is None
            or not isinstance(data, (int, float, complex))
            or math.isnan(data)
            or (min is not None and data < min)
            or (max is not None and data > max)
            or (self.exclusive and min == max)
        ):
            message = self.message
            if message is None:
                # we use %(min)s interpolation to support floats, None, and
                # Decimals without throwing a formatting exception.
                if not isinstance(data, (int, float, complex)):
                    message = field.gettext("Not a valid number value")
                elif self.exclusive and min == max:
                    message = field.gettext(
                        "Check your parameters for minimum and maximum are both set to %(min)s."
                    )
                elif max is None:
                    message = field.gettext("Number must be at least %(min)s.")
                elif min is None:
                    message = field.gettext("Number must be at most %(max)s.")
                else:
                    message = field.gettext(
                        "Number must be between %(min)s and %(max)s."
                    )
            raise ValidationError(message % dict(min=min, max=max))


class AnswerIndicesImplyContext(object):
    """
    Validates if the answer field value is equal to context[start:end]

    :param context:
        The name of the context field to take a substring out of.
    :param start:
        The name of the start index field of the context.
    :param end:
        The name of the end index field of the context.
    :param allow_empty:
        If True, answer can be empty providing both start and end are
        empty as well.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(context_label)s`, `%(context_name)s`,
        `%(start_label)s`, `%(starts_name)s`, `%(end_label)s` and
        `%(end_name)s` to provide a more helpful error.
    """

    def __init__(self, context, start, end, allow_empty=False, message=None):
        self.fields = [
            context,
            start,
            end,
        ]
        self.allow_empty = allow_empty
        self.message = message

    def __call__(self, form, answer):
        for i in range(len(self.fields)):
            try:
                form[self.fields[i]]
            except KeyError:
                raise ValidationError(
                    answer.gettext("Invalid field name '%s'.") % self.fields[i]
                )
        [context, start, end] = self.fields
        if not (  # only run validation if allow_empty is False or some kind of data is given
            self.allow_empty
            and (answer.data is None or answer.data == "")
            and (form[start].data is None or form[start].data == "")
            and (form[end].data is None or form[end].data == "")
        ) and (  # trigger cases of the ValidatorError
            (form[context].data is None or form[context].data == "")
            or (answer.data is None or answer.data == "")
            or (form[start].data is None or form[start].data == "")
            or (form[end].data is None or form[end].data == "")
            or isinstance(form[context].data, int)
            or answer.data != form[context].data[form[start].data : form[end].data]
        ):
            d = {
                "context_label": hasattr(form[context], "label")
                and form[context].label.text
                or context,
                "context_name": context,
                "start_label": hasattr(form[start], "label")
                and form[start].label.text
                or start,
                "start_name": start,
                "end_label": hasattr(form[end], "label")
                and form[end].label.text
                or end,
                "end_name": end,
            }
            message = self.message
            if message is None:
                message = answer.gettext(
                    "Field must be equal to the start index and the end index "
                    "of the context, %(context_name)s."
                )
            raise ValidationError(message % d)
