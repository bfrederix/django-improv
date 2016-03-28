class ReadOnlyFieldsMixin(object):
    readonly_fields =()

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFieldsMixin, self).__init__(*args, **kwargs)
        for field in (field for name, field in self.fields.iteritems() if name in self.readonly_fields):
            field.widget.attrs['disabled'] = 'true'
            field.required = False

    def clean(self):
        cleaned_data = super(ReadOnlyFieldsMixin,self).clean()
        for field in self.readonly_fields:
           cleaned_data[field] = getattr(self.instance, field)

        return cleaned_data


user_agreement_copy = """
Terms and Conditions
--------------------

Last Updated: 3/28/2016

Please read these Terms and Conditions carefully before using
the http://www.dumpedit.com website. For a description of "Channels" and some of our services,
please refer to our documentation at http://docs.dumpedit.com/.

Your access to and use of the Service is conditioned on your acceptance of and compliance with
these Terms. These Terms apply to all visitors, users and others who access or use the Dumpedit
Service. These terms can be accessed on your user profile page at any time.

By accessing or using the Service you agree to be bound by these Terms. If you disagree
with any part of the terms then you may not access the Service.

The User Agreement and Privacy Policy may be modified from time to time; the date of the most
recent revisions will appear on this document, so check this document often. Continued access
of the Service by you will constitute your acceptance of any changes or revisions to the
User Agreement and Privacy Policy. If you fail to follow the terms and/or conditions that
apply to the Service, whether listed in this User Agreement and Privacy Policy, posted
on various pages in the Service, or otherwise communicated to users, we may terminate your
account. We reserve the right to take any technical, legal, and/or other action(s) that
we deem necessary and/or appropriate, with or without notice, to prevent violations and
enforce the Agreement and remediate any purported violations. You acknowledge and agree that we
have the right to stop or prevent violations under the Agreement and you specifically waive
any right to challenge or dispute such determination.

Content
-------

A. Dumpedit allows you to post suggestions, forum posts, create show/theater/troupe channels, store,
share and otherwise make available certain information, text, graphics, videos, or
other material ("Content"). You are responsible for any data shared on this site and
consent to allowing your content to be shared publicly.

B. You agree to your content being monitored for offensive or inappropriate content. Any content
is subject to being removed at will. You agree that any violations can lead to the termination
of your account.

C. We make no guarantees that content submitted by other users will be monitored for
acceptable use. We do no pre-screen Content before it is posted so you may be exposed
to Content that is offensive and/or inappropriate, including Content
that violates the Agreement.

Registering / Logging into our site
-----------------------------------

A. When logging into our site, you consent to allowing us access to your information including name,
e-mail, service (Google, Facebook, etc.) identification numbers, usernames, and other
profile content. You consent to allowing access of this data to any "Channel" owners and admins of
the show/troupe/theater pages you interact on. We may register you to these "Channel" pages
when you access them so that they may have access to your profile information. You acknowledge
and consent to your username and/or avatar or profile picture appearing on our site or being
used in e-mails.

B. You consent to being e-mailed by owners or admins of Channels that you have interacted with as
long as they comply with the rules set forth in this User Agreement. You may unsubscribe to
their mailings at any time and Channel owners or admins are required to cease e-mailing you
in accordance with the CAN-SPAM Act. Any Channel owners or admins are completely responsible
for any failures to comply with this User Agreement. Dumpedit assumes no responsibility for
such violations.

C. You consent to us generating a username for you from your e-mail address or otherwise, or changing
your username if we feel it appropriate or necessary.

D. You may not impersonate, imitate or pretend to be somebody else or a different show when
registering or setting up an account, channel, or profile on our service.


Rules of Usage
--------------

A. The Service is not intended for users under the age of 18. Such users are expressly prohibited
from registering or logging in for the Service or submitting their personally identifiable
information to us.

B. You shall ensure that you will not abuse the service by submitting extra votes or suggestions
to the service.

C. Unless otherwise specified, the Service is intended for your personal, non-commercial use only.
"Channel" owners or admins may contact users that access their channel, but may not sell
obtained user information under any circumstances. Channel owners or admins assume all liability
if they violate these terms.

D. You are solely responsible if you access any other site, application, destination or service from
our site. We do not pre-screen content for external links.

E. You must comply with all local, state, federal, provincial, national, international, and
foreign laws, rules, and regulations in accessing and using the Service, and will
immediately notify us if you learn of or suspect a security breach or any illegal
activity in connection with the Service.

F. Users and Channel owners or admins may not post, e-mail, upload, send or otherwise make
available on or through our Service any Content that constitutes junk mail, spam,
pyramid schemes, chain letters, phishing, unrelated advertising, and/or commercial offers.
All Channel Owners and admins with access to user e-mails must abide by the CAN-SPAM Act and
are not allowed to give others access or sell access to users personal information or e-mail.

G. You may not copy, harvest, crawl, index, capture, or store any Content if we have taken
steps to prohibit or prevent you from doing so, or do not approve of you doing so.

H. You may not modify, copy, or reverse engineer works based on this Service.

I. You may not engage in personal attacks, use any language that is abusive, intimidating,
bullying, criminal, racist, sexist, harassing, hateful, violent, or that victimizes/disparages
an individual on or through our Service. Such content may be removed at will and your
account may be terminated.

Channel Subscriptions Available on or through our Service
---------------------------------------------------------

A. You acknowledge that any subscriptions you purchase on this site are on a per-channel basis.
Subscriptions only give you access to premium features for a single channel, not all the
channels you have created.

B. You agree that any subscription purchased through our service are not automatically refundable
in the event that any bugs, issues, or interruptions in service occur. A refund may
be possible and certainly considered, but at our discretion.

C. You agree to monthly recurring charges being made to your credit card until you cancel your
subscription.

Disclaimer of Limitation of Liability
-------------------------------------

A. CERTAIN FEATURES, FUNCTIONALITY, AND/OR CONTENT OFFERED ON OR THROUGH THE SERVICE MAY
BE HOSTED OR ADMINISTERED BY THIRD PARTIES. THESE SERVICE PROVIDERS MAY REQUIRE THAT
YOU AGREE TO THEIR ADDITIONAL TERMS AND CONDITIONS. YOUR COMPLIANCE WITH ANY SUCH
ADDITIONAL TERMS AND CONDITIONS IS SOLELY YOUR RESPONSIBILITY AND WE WILL HAVE NO LIABILITY
IN CONNECTION WITH THESE SERVICES.

B. YOU ACKNOWLEDGE THAT YOU ARE USING THE SERVICE AT YOUR OWN RISK. THE SERVICE IS
PROVIDED "AS IS", "WITH ALL FAULTS" AND ON AN "AS AVAILABLE" BASIS. WE ARE NOT LIABLE FOR
ANY SOFTWARE DISABLING DEVICES, TIME BOMBS, VIRUSES, WORMS, BUGS, OR DEVICES OR DEFECTS
OF SIMILAR NATURE THAT ARE TRANSMITTED ON OR THROUGH THE SERVICE.

Links to Third-party Sites
--------------------------

A. Dumpedit is not responsible for the contents of any third-party sites or services,
any links contained in third-party sites or services, or any changes or updates to
third-party sites or services. Dumpedit may provide these links and access to
third-party sites and services to you as a convenience only and does not imply
an endorsement by Dumpedit of the third-party site or service.

Termination or Suspension of the Service
----------------------------------------

A. We reserve the right to terminate or suspend your account or channel for any or
no reason, with or without notice.

Communications with You
-----------------------

A. You understand and agree that joining the Service may include receiving certain
communications from us, such as transactional or relationship messages, and/or
messages about your account/profile, and that these communications are considered
part of your account/profile and you may not be able to opt out of receiving them
without ceasing to be a registered user of the Service.

Disputes and Jurisdiction
-------------------------

A. The Service is based in the United States. It is not intended for any other country.
Users from other countries may use the service, but without any guarantees that it will
operate in the same way as the service does in the United States.

B. In any dispute between us, your sole remedy is to stop using this Service.

C. You agree that in the event of any dispute between us, you will first contact us
and make a good faith sustained effort to resolve the dispute before resorting
to any court action.

General
-------

A. We reserve the right to add additional rules that apply to the Service. Such
additional rules are hereby incorporated into the Agreement by this reference. Your use
of the Service constitutes your agreement to comply with these additional rules.

PRIVACY POLICY
--------------

This privacy policy describes how this Service uses and protects any information
that you give us when you use this website. We may change this policy by updating
this page. You should check this page regulary to ensure that you are happy with
any changes.

A. The Service generally collects personally identifiable information with
your specific knowledge and consent (i.e. when you log into our site with Facebook or
Google).

B. Our servers may also automatically collect information about you, your online
behavior and your computer, mobile or other device.

C. If you choose to use any third party social networking services that are integrated
with our Service, we may receive personally identifiable information and share that
information with the Channel owners or admins of Channels that you interact with in our
Service.

D. We may allow access to our database by third parties that provide us with services,
such as technical maintenance, market research, and classified ads functionality,
but only for the purpose of providing those services.

E. We may also provide access to our database in order to cooperate with official
investigations or legal proceedings.

F. We reserve the right to use and share aggregated, anonymous data about our users
for any lawful business purpose, such as analyzing usage trends, seeking compatible
advertisers, sponsors, clients, and customers.

G. Our Service will place and/or store code or other types of information and/or
devices (e.g., "cookies") on your computer, mobile or other device. We may use
this for any lawful business purpose.

H. Because no system of physical or electronic security is impenetrable, we cannot
guarantee the security of the information you send to us, and by using this Service
you agree to assume all risk in connection with the information sent to us.

I. We do not currently support any browser based Do Not Track (DNT) settings or
participate in any DNT frameworks at this time. Proceed at your own risk.

If you have any concerns or questions about any aspect of this policy, please contact
us through the "Contact" section in the footer of the homepage.
"""