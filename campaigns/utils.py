from django.core.mail import send_mail
from django.conf import settings


def send_email_notification(subject, msg_body):
    send_mail(subject, msg_body, settings.DEFAULT_FROM_EMAIL, [settings.SERVER_EMAIL],
              fail_silently=True)
    return


def copy_tree(parent_message, composer):
    """
    Copy the whole tree and return the root message
    """
    options = parent_message.options.all()

    # copy parent message
    parent_message.pk = None
    parent_message.composer = composer
    parent_message.save()

    if options:
        for option in options:
            option.pk = None
            option.child_msg = copy_tree(option.child_msg, composer)
            option.parent_msg = parent_message
            option.save()
    return parent_message


def collect_tree_content(parent_message):
    content = parent_message.get_full_content()

    options = parent_message.options.all()
    if options:
        for option in options:
            content += ' ' + collect_tree_content(option.child_msg)
    return content
