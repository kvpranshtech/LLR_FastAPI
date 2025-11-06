"""
    - modfied the code in july 2023
    - no more modification needed
"""


# use for defining email method for sending
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from adminv2.models import PaymentRefundEmails
from allauth.account.models import EmailCC
from site_settings.models import StaticPages
from django.template import Template, Context
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
# from django.utils.html import strip_tags


# def get_email_template(slug, context_data):
#     try:
#         static_page = StaticPages.objects.get(slug=slug)
#         template_content = static_page.body_content
#         template = Template(template_content)
#         context = Context(context_data)
#         return template.render(context)
#     except ObjectDoesNotExist:
#         return None




#test email
def sendTestEmail(email_send_to='vishal@textdrip.com'):
    subject = "test mail"
    message = f"""Thank you for using LandlineRemover.com \n this is test email"""
    return send_mail(subject,message, settings.DEFAULT_FROM_EMAIL, [email_send_to], fail_silently=False)


def sendAlertEmail(email_send_to, subject, message):
    return send_mail(subject,message, settings.DEFAULT_FROM_EMAIL, [email_send_to], fail_silently=True)


#no direct use - helping parent method
def email_BaseMethod(subject, email_send_to, html_message, allow_cc=False,bypass_cc=False):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = EmailMultiAlternatives(
       subject=subject,
       from_email=from_email,
       to=[email_send_to],
    )
    if allow_cc and not bypass_cc:
        #message.cc = ["info@landlineremover.com"]
        #pass
        cc_emails = list(EmailCC.objects.filter(is_active=True, is_deleted=False).values_list("email", flat=True))
        message.cc = cc_emails
    if allow_cc and bypass_cc:
        print("-----------", bypass_cc)
        message.cc = ["info@landlineremover.com","anil@pranshtech.com"]


    message.attach_alternative(html_message, "text/html")
    message.send(fail_silently=True)
    return None 


# function for sending email on invitation 
# def sendWelcomeEmail(email_send_to, allow_cc=True):
#     subject = f'Welcome to the LandlineRemover.com'
#     html_message = render_to_string('pages/mails/welcome.html', {})
#     email_BaseMethod(subject, email_send_to, html_message, allow_cc)
#     return None



def get_welcome_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)  # Retrieve the static page with the given slug
        template_content = static_page.body_content  # Get the HTML content of the template

        # Render the content using Django's template engine
        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        # Now insert it inside the main mail.html template
        email_html = render_to_string("pages/mails/mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


# Function for sending welcome email
def sendWelcomeEmail(email_send_to, user, allow_cc=True):
    try:
        content = {'email': user}
        html_message = get_welcome_email_template('welcome-email', content)

        if not html_message:
            html_message = render_to_string('pages/mails/welcome.html', content)
        print(f"---------------- Welcome mail send to {email_send_to} ----------------------")
        email_BaseMethod(f'Welcome to LandlineRemover.com', email_send_to, html_message, allow_cc)
        return True
    except Exception as e:
        print(f"Error in sending welcome email: {e}")
        return False
# sendWelcomeEmail('kirtan.pranshtech@gmail.com', allow_cc=True)

# function for sending email on payment charge
# def sendAfterPaymentEmail(email_send_to, amount_, credits_, timestamp_, allow_cc=True):
#     subject = f'Payment Transaction'
#     context= {
#         'amount_':amount_,
#         'credits_':credits_,
#         'timestamp_':timestamp_,
#     }
#     html_message = render_to_string('pages/mails/payment.html', context)
#
#     email_BaseMethod(subject, email_send_to, html_message, allow_cc)
#
#     return None


def get_payment_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)  # Retrieve the static page with the given slug
        template_content = static_page.body_content  # Get the HTML content of the template

        # Render the content using Django's template engine
        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        # Now insert it inside the main mail.html template
        email_html = render_to_string("pages/mails/payment.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None

# Function for sending payment transaction email
def sendAfterPaymentEmail(email_send_to, amount_, credits_, timestamp_,mode_, payment_through_, allow_cc=True):
    try:
        context = {
            'amount_': amount_,
            'credits_': credits_,
            'timestamp_': timestamp_,
            'mode_': mode_,
            'payment_through_': payment_through_,
            'url_': settings.SITE_DOMAIN_LINK
        }

        html_message = get_payment_email_template('payment-success', context)

        if not html_message:
            html_message = render_to_string('pages/mails/payment.html', context)

        email_BaseMethod(f'Payment Transaction', email_send_to, html_message, allow_cc)
        return True
    except Exception as e:
        print(f"Error in sending payment email: {e}")
        return False

# sendAfterPaymentEmail('kirtan.pranshtech@gmail.com', 150, 100000, '10-02-204', allow_cc=True)


# For success email template
def get_success_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content  # HTML content stored in DB

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/csv_success.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None

def email_SendAfterCSVSuccessfull(email_send_to, filename, download_file_url, allow_cc=False):
    try:
        subject = 'Notification: Your file is ready to download!'

        # Context for template rendering
        context = {
            'filename_': filename,
            'download_url_': download_file_url
        }

        # Fetch email content from the database template
        email_content = get_success_email_template('success-csv-file', context)

        # Fallback to default template if no database template exists
        if not email_content:
            email_content = render_to_string('pages/mails/csv_success.html', context)

        # Send Email
        email = EmailMultiAlternatives(subject, '', to=[email_send_to])
        email.attach_alternative(email_content, "text/html")
        email.send()

        return True
    except Exception as e:
        print(f"Email Sending Failed: {e}")
        return False
# function for sending email after csv failed 
# def email_SendAfterCSVFailed(email_send_to, filename, allow_cc=False):
#     try:
#         subject = f'Notification: Your file is failed to process!'
#         context= {
#             'filename_':filename,
#         }
#         html_message = render_to_string('pages/mails/csv_failed.html',context)
#         email_BaseMethod(subject, email_send_to, html_message, allow_cc)
#         return True
#     except:
#         return False


# from utils.handle_emailing import email_SendAfterCSVFailed

# email_SendAfterCSVFailed(email_send_to="kirtan.pranshtech@gmail.com",filename="test_email-0123-qwer-1456210-577yg.csv", allow_cc=False)

# email_SendAfterCSVSuccessfull(email_send_to="kirtan.pranshtech@gmail.com",filename="test_email-0123-qwer-1456210-577yg.csv", download_file_url="test_email-0123-qwer-1456210-577yg.csv", allow_cc=False)



# def email_SendAfterCSVFailed(email_send_to, filename, allow_cc=False):
#     try:
#         subject = 'Notification: Your file has failed to process!'
#
#
#         context = {'filename_': filename}
#         email_content = get_email_template('csv-failed-template', context)
#
#         if not email_content:
#             email_content = render_to_string('pages/mails/csv_failed.html', context)
#
#         # Send Email
#         email = EmailMultiAlternatives(subject, '', to=[email_send_to])
#         email.attach_alternative(email_content, "text/html")
#         email.send()
#         return True
#     except Exception as e:
#         print(f"Email Sending Failed: {e}")
#         return False

#  To get the template dynamically from the Staticpages Model
def get_faild_email_template(slug, context_data):
    try:

        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        # Render the content using Django's template engine
        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        # Now insert it inside the mail.html template
        email_html = render_to_string("pages/mails/mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def email_SendAfterCSVFailed(email_send_to, filename, allow_cc=False):
    try:
        subject = 'Notification: Your file has failed to process!'
        context = {'filename_': filename}
        email_content = get_faild_email_template('csv-failed-template', context)

        if not email_content:
            email_content = render_to_string('pages/mails/csv_failed.html', context)

        # Send Email
        email = EmailMultiAlternatives(subject, '', to=[email_send_to])
        email.attach_alternative(email_content, "text/html")
        email.send()

        return True
    except Exception as e:
        print(f"Email Sending Failed: {e}")
        return False

# function for sending email after export completed
# def email_SendAfterExportCompleted(email_send_to,title,allow_cc=False):
#     try:
#         subject = f'Your export "{title}" has been completed.'
#         context= {
#             'title':title,
#         }
#         html_message = render_to_string('pages/mails/export_completed.html',context)
#         email_BaseMethod(subject, email_send_to, html_message, allow_cc)
#         return True
#     except:
#         return False

# Template for export email
def get_export_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def email_SendAfterExportCompleted(email_send_to, title,download_url ,allow_cc=False):
    try:
        context = {
            'title': title,
            'download_url': download_url
        }

        html_message = get_export_email_template('export-success', context)

        if not html_message:
            html_message = render_to_string('pages/mails/export_completed.html', context)

        email_BaseMethod(f'Your export "{title}" has been completed.', email_send_to, html_message, allow_cc)

        return True
    except Exception as e:
        print(f"Error in sending export completion email: {e}")
        return False
# email_SendAfterExportCompleted('kirtan.pranshtech@gmail.com', 'title', allow_cc=False)


# def email_SendOnInquiry(name, email,subject, message ,allow_cc=False):
#     try:
#         # subject = f'Notification: Contact Us Inquiry!'
#         context= {
#             'email': email,
#             'subject': subject,
#             'name': name,
#             'message': message
#         }
#         html_message = render_to_string('pages/mails/contact_us_inquiry.html', context)
#         email_BaseMethod(subject, 'info@landlineremover.com', html_message, allow_cc)
#         return True
#     except:
#         return False


# Function to retrieve and render the email template based on slug
def get_inquiry_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None

# Function to send the email after "Contact Us" inquiry
def email_SendOnInquiry(name, email, subject, message, allow_cc=True):
    try:
        context = {
            'email': email,
            'subject': subject,
            'name': name,
            'message': message
        }

        html_message = get_inquiry_email_template('contact-us-inquiry', context)

        if not html_message:
            html_message = render_to_string('pages/mails/contact_us_inquiry.html', context)

        # email_BaseMethod(subject, 'info@landlineremover.com', html_message, allow_cc)

        if settings.SITE_DOMAIN_LINK == "https://app.landlineremover.com":
            email_BaseMethod(subject, 'info@landlineremover.com', html_message, allow_cc)
        else:
            email_BaseMethod(subject, email, html_message, allow_cc)

        return True
    except Exception as e:
        print(f"Error in sending inquiry email: {e}")
        return False

# email_SendOnInquiry(kirtan, test@gmail.com, 'general query', 'message', allow_cc=False)


def get_otp_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content  # Retrieve the content of the email template

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/auto_top-up_otp.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None

# handle Auto Top Up email
def send_auto_top_up_otp_email(user_email, otp):
    try:
        # Context for rendering OTP
        context = {
            'otp': otp
        }

        html_message = get_otp_email_template('auto-top-up-otp', context)

        if not html_message:

            html_message = render_to_string('pages/mails/auto_top-up_otp.html', context)

        email_BaseMethod('Verification Email', user_email, html_message, allow_cc=False)

        return True
    except Exception as e:
        print(f"Error in sending OTP email: {e}")
        return False


def get_email_template(slug, context_data):
    """ Fetch the email template from the database and render it with context data. """
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content  # Fetch stored template HTML

        # Render template with dynamic context
        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        # Wrap content inside an HTML structure if needed
        email_html = render_to_string("pages/mails/team_invitation_mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def send_invitation_email(invitation, from_email, to_user, credits_type):
    accept_url = f"{settings.SITE_DOMAIN_LINK}/accept-invite/{invitation.token}/"
    # cancel_url = "http://127.0.0.1:9001/"

    subject = "You have been invited to join a team"

    context = {
        "team_name": invitation.team.team_name,
        "accept_url": accept_url,
        # "cancel_url": cancel_url,
        "from_email": from_email,
        'credits_type': ', '.join(credits_type)
    }

    html_content = get_email_template('team-invitation', context)

    if not html_content:
        html_content = render_to_string("pages/mails/team_invitation_mail.html", context)
    text_content = strip_tags(html_content)

    try:
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_user])
        msg.attach_alternative(html_content, "text/html")  # Attach HTML version
        msg.send()
        print("Mail sent successfully!")

    except Exception as e:
        print("Issue in mail send:", str(e))


def get_invite_accept_mail_template(slug, context_data):
    """ Fetch the email template from the database and render it with context data. """
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        # Render template with dynamic context
        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        # Wrap content inside an HTML structure if needed
        email_html = render_to_string("pages/mails/team_join_request_mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None

def send_team_join_email(user,to_user ,team_name, team_id ,time_on_send ,team_invitation_id):
    accept_url = f"{settings.SITE_DOMAIN_LINK}/team/requested-users/{team_id}/?open_accept_model={team_invitation_id}"
    reject_url = f"{settings.SITE_DOMAIN_LINK}/team/requested-users/{team_id}/?open_reject_model={team_invitation_id}"

    print(f"----------user *---------- {user}")
    subject = "User requested to join a team"
    context = {
        "team_name": team_name,
        "from_email": user,
        "request_time": time_on_send,
        "accept_url": accept_url,
        "reject_url": reject_url
    }

    html_content = get_invite_accept_mail_template('team-request', context)

    if not html_content:
        html_content = render_to_string("pages/mails/team_join_request_mail.html", context)
    text_content = strip_tags(html_content)

    try:
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_user])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print("Mail sent successfully for team join request !")

    except Exception as e:
        print("Issue in mail send:", str(e))


# refund mail sent to user
def get_refund_mail_template(slug, context_data):
    """ Fetch the email template from the database and render it with context data. """
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        # Render template with dynamic context
        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        # Wrap content inside an HTML structure if needed
        email_html = render_to_string("pages/mails/user_refund_mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


# def send_refund_email_to_user(to_user,username,amount, credits, credit_type, time):
#
#     subject = "Refund Confirmation from - LandlineRemover"
#     context = {
#         "amount_": amount,
#         'username':username,
#         "credits_": credits,
#         "credit_type_": credit_type,
#         "timestamp_": time,
#     }
#
#     html_content = get_refund_mail_template('refund-mail-template', context)
#
#     if not html_content:
#         html_content = render_to_string("pages/mails/user_refund_mail.html", context)
#     text_content = strip_tags(html_content)
#
#     try:
#
#
#         msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_user])
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()
#
#     except Exception as e:
#         print("Issue in mail send:", str(e))

def send_refund_email_to_user(to_user, username, amount, credits, credit_type, time):
    try:
        # Get the user object
        user = User.objects.filter(email=to_user).first()
        if user:
            profile = getattr(user, "profile", None)
            if profile and getattr(profile, "is_test_user", False):
                print(f"⏭️ Skipping refund email for test user: {username}")
                return  # ✅ skip sending email

        subject = "Refund Confirmation from - LandlineRemover"
        context = {
            "amount_": amount,
            'username': username,
            "credits_": credits,
            "credit_type_": credit_type,
            "timestamp_": time,
        }

        html_content = get_refund_mail_template('refund-mail-template', context)
        if not html_content:
            html_content = render_to_string("pages/mails/user_refund_mail.html", context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_user])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"✅ Refund email sent to {username}")

    except Exception as e:
        print(f"❌ Error in send_refund_email_to_user: {e}")


# refund mail sent to staff users
def get_refund_mail_staff_template(slug, context_data):
    """ Fetch the email template from the database and render it with context data. """
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        # Render template with dynamic context
        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        # Wrap content inside an HTML structure if needed
        email_html = render_to_string("pages/mails/staff_refund_mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


# def send_refund_email_to_staff(staff_username_, staff_email_, refunded_to_username_, amount_, credits_, credit_type_, current_time):
#     subject = "Payment Refund"
#
#     context = {
#         "staff_username_": staff_username_,
#         "refunded_to_username_": refunded_to_username_,
#         "amount_": amount_,
#         "credits_": credits_,
#         "credit_type_": credit_type_,
#         "timestamp_": current_time
#     }
#
#     html_content = get_refund_mail_staff_template('refund-staff-mail', context)
#     if not html_content:
#         html_content = render_to_string("pages/mails/staff_refund_mail.html", context)
#     text_content = strip_tags(html_content)
#
#     try:
#         user_obj = User.objects.filter(email=staff_email_).first()
#         cc_emails = ['info@landlineremover.com', 'vishal@textdrip.com']  # Default cc list
#
#         if user_obj:
#             if PaymentRefundEmails.objects.filter(user=user_obj).exists():
#                 cc_emails = ['vishal@textdrip.com']
#
#         msg = EmailMultiAlternatives(
#             subject,
#             text_content,
#             settings.DEFAULT_FROM_EMAIL,
#             [staff_email_],
#             cc=cc_emails
#         )
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()
#         print("Mail sent successfully for team join request!")
#
#     except Exception as e:
#         print("Issue in mail send:", str(e))


def send_refund_email_to_staff(staff_username_, staff_email_, refunded_to_username_, amount_, credits_, credit_type_, current_time):
    try:
        # Skip sending to staff if refund is for a test user
        refunded_user = User.objects.filter(username=refunded_to_username_).first()
        if refunded_user:
            profile = getattr(refunded_user, "profile", None)
            if profile and getattr(profile, "is_test_user", False):
                print(f"⏭️ Skipping staff refund email — refunded user is test user: {refunded_to_username_}")
                return  # ✅ skip sending email

        subject = "Payment Refund"
        context = {
            "staff_username_": staff_username_,
            "refunded_to_username_": refunded_to_username_,
            "amount_": amount_,
            "credits_": credits_,
            "credit_type_": credit_type_,
            "timestamp_": current_time
        }

        html_content = get_refund_mail_staff_template('refund-staff-mail', context)
        if not html_content:
            html_content = render_to_string("pages/mails/staff_refund_mail.html", context)
        text_content = strip_tags(html_content)

        user_obj = User.objects.filter(email=staff_email_).first()
        cc_emails = ['info@landlineremover.com', 'vishal@textdrip.com']
        if user_obj and PaymentRefundEmails.objects.filter(user=user_obj).exists():
            cc_emails = ['vishal@textdrip.com']

        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [staff_email_],
            cc=cc_emails
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"✅ Staff refund email sent to {staff_username_}")

    except Exception as e:
        print(f"❌ Error in send_refund_email_to_staff: {e}")


def get_subscription_end_mail_template(slug, context_data):
    """ Fetch the email template from the database and render it with context data. """
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/user_subscription_end_mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def send_subscription_end_mail_(to_user, username, subscription_plan, subscription_type, subscription, days_left, time):

    subject = "Subscription plan is ending!!"

    context = {
        'username': username,
        "subscription": subscription,
        "days_left": days_left,
        "end_date": time,
        "subscription_plan": subscription_plan,
        "subscription_type": subscription_type,

    }

    html_content = get_subscription_end_mail_template('subscription-end-mail-template', context)

    if not html_content:
        html_content = render_to_string("pages/mails/user_refund_mail.html", context)
    text_content = strip_tags(html_content)

    try:
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_user])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    except Exception as e:
        print("Issue in mail send:", str(e))

def get_subscription_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/subscription_payment.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def sendSubscriptionEmail(email_send_to, amount_,  timestamp_,mode_, payment_through_, allow_cc=True):
    try:
        context = {
            'amount_': amount_,
            'timestamp_': timestamp_,
            'mode_': mode_,
            'payment_through_': payment_through_,
            'url_': settings.SITE_DOMAIN_LINK
        }

        html_message = get_subscription_email_template('payment-subscription', context)

        if not html_message:
            html_message = render_to_string('pages/mails/subscription_payment.html', context)

        email_BaseMethod(f'Payment Transaction', email_send_to, html_message, allow_cc)
        return True
    except Exception as e:
        print(f"Error in sending payment email: {e}")
        return False



def get_inactive_user_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/inactive_user.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def sendInactiveUserEmail(username, email_send_to):
    try:
        context = {
            'username': username,
            'url_': settings.SITE_DOMAIN_LINK
        }

        html_message = get_inactive_user_email_template('inactive-user-mail', context)

        if not html_message:
            html_message = render_to_string('pages/mails/inactive_user.html', context)

        email_BaseMethod(f'Inactive Account', email_send_to, html_message)
        return True
    except Exception as e:
        print(f"Error in sending Inactive Account email to user: {e}")
        return False

def get_delete_user_email_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/delete_user.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def sendDeleteUserEmail(username, email_send_to):
    try:
        context = {
            'username': username,
        }

        html_message = get_delete_user_email_template('delete-user-mail', context)

        if not html_message:
            html_message = render_to_string('pages/mails/delete_user.html', context)

        email_BaseMethod(f'Delete Account', email_send_to, html_message)
        return True
    except Exception as e:
        print(f"Error in sending Inactive Account email to user: {e}")
        return False


def get_forgot_password_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/forgot_password_mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def sendForgotPasswordEmail(username, token, email_send_to):
    try:
        context = {
            'username': username,
            'token': token,
            'url_': settings.SITE_DOMAIN_LINK,

        }

        html_message = get_forgot_password_template('forgot-password-mail', context)

        if not html_message:
            html_message = render_to_string('pages/mails/forgot_password_mail.html', context)

        email_BaseMethod(f'Reset Password', email_send_to, html_message)
        return True
    except Exception as e:
        print(f"Error in sending Inactive Account email to user: {e}")
        return False

def get_password_change_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/password_change_mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def send_password_change_email(email_send_to):
    try:
        context = {
            'url_': settings.SITE_DOMAIN_LINK,
        }

        html_message = get_password_change_template('password-change-mail', context)

        if not html_message:
            html_message = render_to_string('pages/mails/password_change_mail.html', context)

        email_BaseMethod(f'Password Changed Successfully', email_send_to, html_message)
        return True
    except Exception as e:
        print(f"Error in sending Inactive Account email to user: {e}")
        return False


def get_custom_subscription_send_template(slug, context_data):
    try:
        static_page = StaticPages.objects.get(slug=slug)
        template_content = static_page.body_content

        django_template = Template(template_content)
        rendered_content = django_template.render(Context(context_data))

        email_html = render_to_string("pages/mails/custom_subscription_mail.html", {"content": rendered_content})

        return email_html
    except ObjectDoesNotExist:
        return None


def send_custom_subscription_mail(email_send_to, token):
    try:
        url = f'/custom-subscription/{token}/'
        context = {
            'url_': settings.SITE_DOMAIN_LINK+url,
        }

        html_message = get_custom_subscription_send_template('custom-subscription-mail', context)

        if not html_message:
            html_message = render_to_string('pages/mails/custom_subscription_mail.html', context)

        email_BaseMethod(f'Subscription Plan', email_send_to, html_message)
        return True

    except Exception as e:
        print(f"Error in sending Inactive Account email to user: {e}")
        return False
