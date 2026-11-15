# Instructions for the rater

ToS;DR (tosdr.org) describes what a service's terms or privacy policy say as short "cases", for example "You waive
your right to a class action". Each card in `cards.md` shows one case and one passage from a service's terms or
privacy policy.

For each card in `cards.md`, answer one question: **does this passage state or clearly imply the case?**

- **YES**: a careful reader could quote this passage as evidence for the case.
- **PARTLY**: the passage states something close (narrower, broader, or only part of the case), or implies it only
  weakly.
- **NO**: the passage does not state or imply the case.

Judge each card on its own text: do not assume anything about the rest of the document or the service. There is no
expected distribution of answers.

Do not open, list or search any file or directory, do not run commands, and do not use the web: everything you need
is below. Your final reply must be ONLY one JSON object covering every card, with nothing before or after it, in this
shape: {"S001": {"verdict": "YES", "why": "one short sentence"}, ...}, using each card's own id. "verdict" is one of
YES, PARTLY, NO, and "why" is one short sentence (the words that state the case, or what is missing).

==========================================================================================
# 107 cards

For each card: does the passage state or clearly imply the case? Answer in verdicts.json.

## M001
**Case:** This service cannot be held responsible for disputes that you may have with other users

**Passage:**

```
If you use Pinterest for commercial purposes without agreeing to our as required by Section 2(c) of these Terms, you agree to indemnify and hold harmless Pinterest, Inc., Pinterest Europe Ltd. and their affiliates from any claims (including reasonable legal fees) relating to your use of our Service. Pinterest reserves the right, at its own cost, to assume the exclusive defence and control of any matter otherwise subject to indemnification, in which event you will fully cooperate with Pinterest.

More simply put

If you are a business user and Pinterest is sued because of your use of the Service, you’re financially responsible.

9\. Disclaimers

===============

To the extent permitted by applicable law, the Service and all content on Pinterest is provided on an 'as is' basis without warranty of any kind, whether express or implied.

Pinterest specifically disclaims any and all warranties and conditions of merchantability, fitness for a particular purpose and non-infringement, and any warranties arising out of course of dealing or usage of trade.

Pinterest takes no responsibility and assumes no liability for any User Content that you or any other person or third party posts or sends using the Service. You understand and agree that you may be exposed to User Content that is inaccurate, objectionable, inappropriate for children or otherwise unsuited to your purpose.
```

## M002
**Case:** No guarantee is given regarding quality

**Passage:**

```
By law, consumers have certain rights that cannot be excluded or altered by a contract. Nothing in this Agreement affects those rights you may have as a consumer. Other than as expressly stated in this Agreement or as required by law (see Legal Guarantee), YouTube does not give any specific promises about the Service. For example, we don’t give any additional promises about: the Content provided through the Service; the specific features of the Service, or its accuracy, reliability, availability, or ability to meet your needs; or that any Content you submit will be accessible or stored on the Service.

**Limitation of Liability**

---------------------------
```

## M003
**Case:**  You are being tracked via social media cookies/pixels

**Passage:**

```
1. **Usage Information.** When you use Bluesky, we collect certain information automatically, including your Internet protocol (IP) address (which can be used to derive your general location), user settings, cookie identifiers, mobile carrier, other unique identifiers, browser or device information, and Internet service provider (ISP). We may also collect personal information about your use of Bluesky, including the posts you view on Bluesky, the links you click within Bluesky, and the frequency and duration of your activities.

2. **Cookies (and Other Technologies).** We and third parties that provide content or other functionality on Bluesky may use cookies, pixel tags, and other technologies (**"Tracking Technologies"**) to automatically collect information. See Section 9, Cookies, for more information.

3. **Personal Data We Collect from Other Sources**

1. **Third Parties, generally.** We may collect personal information from third parties. For example, you may direct a developer application or other third-party social networking application to share personal information with us or you may live in a jurisdiction that requires age verification and we will collect information from a third-party provider telling us whether you meet certain age requirements.
```

## M004
**Case:** This service is a subsidiary of Company X

**Passage:**

```
Ad partners, developers, and publishers.** Our ad and business partners share information with us such as browser cookie IDs, X-generated identifiers, []mobile device IDs, hashed user information like email addresses, demographic or interest data, and content viewed or actions taken on a website or app. Some of our ad partners, particularly our advertisers, also enable us to collect similar information directly from their website or app by integrating our advertising technology. Information shared by ad partners and affiliates or collected by X from the websites and apps of ad partners and affiliates may be combined with the other information you share with X and that X receives, generates, or infers about you described elsewhere in this Privacy Policy.

**Other third parties, account connections, and integrations.** We may receive information about you from third parties who are not our ad partners, such as other X users, developers, and partners who help us evaluate the safety and quality of content on our platform, our [corporate affiliates], and other services you link to your X account. You may choose to connect your X account to your account on another service, and that other service may send us information about your account on that service.

2\. How We Use Information

--------------------------
```

## M005
**Case:** Third parties are involved in operating the service

**Passage:**

```
Please keep us informed if your Personal Data changes at any point during your relationship with us so we can keep our records accurate and current. Update your Personal Data in the App or on the Site.

4\. Applicability of this Policy

--------------------------------

This Policy is separate from our [Terms of Service] and our [Community Guidelines], that also govern your use of Bluesky.

5\. Third-party Services

------------------------

Bluesky and the Services may include links to third-party websites, plug-ins, applications, services, products, and technology (“**Third-party Services**”). Clicking on links to and using Third-party Services may allow third parties to collect or share your Personal Data. We are not responsible for the content, security or privacy practices of those Third-party Services and this Policy does not apply to your use of Third-party Services. You should consider the privacy and cookie policies / notices of those third parties to find out how your Personal Data may be used.

6\. If you do not want to provide Personal Data

-----------------------------------------------
```

## M006
**Case:** The service can stop being provided at any time

**Passage:**

```
We do not warrant that Pinterest or any portion of the Service, or any materials or content offered through Pinterest, are accurate, complete or current, or will be uninterrupted, secure or free of errors, viruses or other harmful components.

We may make changes to Pinterest for various reasons. We will have no liability for any change to Pinterest or any suspension or termination of your access to or use of Pinterest.

The limitations, exclusions and disclaimers in this Section apply to the fullest extent permitted by applicable law.

More simply put

We work every day to improve our Service and we hope you love it. We may make changes to Pinterest from time to time and for various reasons – including adding, removing or changing features and how our Service works. But services like Pinterest aren't perfect, and you agree to use ours 'as is' without warranties.

10\. Limitation of liability

============================
```

## M007
**Case:** Your account can be deleted or permanently suspended without prior notice and without a reason

**Passage:**

```
-----------------------

You may stop using the Service at any time. You can also [delete the Service] from your Google Account, which involves closing your YouTube channel and removing your data, with the option to download a copy of your data first.

**Terminations and Suspensions by YouTube**

-------------------------------------------

YouTube reserves the right to suspend or terminate your Google account or your access to all or part of the Service if: (a) you materially or repeatedly breach this Agreement; (b) we are required to do so to comply with a legal requirement or a court order; or (c) there are objective and concrete reasons to believe there has been conduct that creates liability or harm to any user, other third party, YouTube or our Affiliates.

**Notice for Termination or Suspension**

----------------------------------------

We will notify you with the reason for termination or suspension by YouTube, and where such action is taken for cause, we will give you the opportunity to remedy or stop the stated behaviour, unless there are objective and concrete reasons to believe that to do so: (a) would violate the law or the direction of a legal enforcement authority; (b) would compromise an investigation or (c) would substantially compromise the integrity, operation or security of the Service; or (d) would cause substantial harm to any user, other third party, YouTube or our Affiliates.

**Effect of Account Suspension or Termination**
```

## M008
**Case:** The court of law governing the terms is in a jurisdiction that is less friendly to user privacy protection

**Passage:**

```
All disputes must be brought in the party's individual capacity and not as a member in any class or representative proceeding. You agree that, by entering into these Terms, you are waiving the right to a trial by jury or to participate in a class action.

Nothing in these Terms shall affect any non-waivable statutory rights that apply to you. To the extent that any dispute isn’t arbitrable under applicable laws or otherwise, you agree that the dispute will be resolved exclusively in accordance with Section 12 of these Terms.

**Batched arbitration**: To provide a more efficient arbitration process, you and we each agree that if 25 or more similar arbitration demands are filed within a 60-day period or with the assistance of the same law firm or group of law firms, AAA will consolidate the arbitration demands. For each batch, AAA will administer one set of filing and administrative fees per side, per batch, and AAA will appoint one arbitrator to resolve each batch as a single consolidated arbitration. Arbitration demands are similar if they arise from similar facts and raise similar legal issues while seeking similar relief. Any dispute about similarity will be submitted to a single arbitrator, whose fees will be paid by us.

More simply put

You agree to notify us of any dispute and try to resolve it amicably. If that doesn’t work, the dispute will be efficiently decided through arbitration, not in court.

12\. Governing law and jurisdiction
```

## M009
**Case:** The terms may be changed at any time, but you will receive notification of the changes

**Passage:**

```
We may revise, add or remove any or all portions of these Terms from time to time and the most current version will always be posted on our website. Unless otherwise required by law, we will notify you of any material changes to these Terms before any update enters into effect. Your continued access to or use of Pinterest after such an update constitutes your binding acceptance of such changes. Disputes arising under these Terms will be resolved in accordance with the version of these Terms in place at the time the dispute arose. For clarity, by continuing to use Pinterest, you are agreeing to be bound by the then-current version of these Terms.

More simply put

If we're making a material change to the Terms, we'll let you know ahead of time. If you don’t agree with the new Terms, please stop using Pinterest.

### b. Assignment

If you’re a consumer in the EEA, Switzerland or the UK, either you or we may assign this agreement, and any rights and licences granted under it, to a third party. In all other cases, these Terms, and any rights and licences granted hereunder, may not be transferred or assigned by you, but may be assigned by us without restriction. Any attempted transfer or assignment in violation hereof shall be null and void.

In case of such an assignment by us, you are entitled to terminate the agreement with immediate effect by deactivating your account. We will provide you with reasonable notice of any such assignment.

### c. Entire agreement/severability
```

## M010
**Case:** Third-party cookies are employed, but with opt out instructions

**Passage:**

```
**Third-party content and integrations.** We share or disclose your information with your consent or at your direction, such as when you [authorize a third-party web client or application] to access your account or when you direct us to share your feedback with a business. Similarly, to improve your experience, we work with third-party partners to display their video content on X or to allow cross-platform sharing. When you watch or otherwise interact with content from our video or cross-platform sharing partners, they may receive and process your personal information as described in their privacy policies. For video content, you can adjust your [autoplay settings] if you prefer that content not to play automatically.

**Third-party collaborators.** Depending on your [settings], or if you decide to share your data, we may share or disclose your information with third parties. If you do not opt out, in some instances the recipients of the information may use it for their own independent purposes in addition to those stated in X’s Privacy Policy, including, for example, to train their artificial intelligence models, whether generative or otherwise.
```

## M011
**Case:** No guarantee is given regarding quality

**Passage:**

```
If you use Pinterest for commercial purposes without agreeing to our as required by Section 2(c) of these Terms, you agree to indemnify and hold harmless Pinterest, Inc., Pinterest Europe Ltd. and their affiliates from any claims (including reasonable legal fees) relating to your use of our Service. Pinterest reserves the right, at its own cost, to assume the exclusive defence and control of any matter otherwise subject to indemnification, in which event you will fully cooperate with Pinterest.

More simply put

If you are a business user and Pinterest is sued because of your use of the Service, you’re financially responsible.

9\. Disclaimers

===============

To the extent permitted by applicable law, the Service and all content on Pinterest is provided on an 'as is' basis without warranty of any kind, whether express or implied.

Pinterest specifically disclaims any and all warranties and conditions of merchantability, fitness for a particular purpose and non-infringement, and any warranties arising out of course of dealing or usage of trade.

Pinterest takes no responsibility and assumes no liability for any User Content that you or any other person or third party posts or sends using the Service. You understand and agree that you may be exposed to User Content that is inaccurate, objectionable, inappropriate for children or otherwise unsuited to your purpose.
```

## M012
**Case:** Third-party cookies are employed, but with opt out instructions

**Passage:**

```
* Posts and other content you post (including the date, application, and version of X) and information about your broadcast activity (e.g., Spaces), including broadcasts you’ve created and when you created them, your lists, bookmarks, and Communities you are a part of.

* Your interactions with other users’ content, such as reposts, likes, bookmarks, shares, downloads, replies, if other users mention or tag you in content or if you mention or tag them, and broadcasts you’ve participated in (including your viewing history, listening, commenting, speaking, and reacting).

* How you interact with others on the platform, such as people you follow and people who follow you, metadata related to [Encrypted Messages], and when you use [Direct Messages], including the contents of the messages, the recipients, and date and time of messages.

* If you communicate with us, such as through email, we will collect information about the communication and its content.

* We collect information on links you interact with across our services (including in our emails sent to you).

**Purchase and payments.** To allow you to make a payment or send money using X features or services, including through an intermediary, we may receive information about your transaction such as when it was made, when a subscription is set to expire or auto-renew, and amounts paid or received.

**Device information.** We collect information from and about the devices you use to access X, including:
```

## M013
**Case:** The service claims that third parties it shares your personal information with are bound by confidentiality obligations

**Passage:**

```
5. **Other Purposes.** We also use your personal information for other purposes as requested by you, as permitted by applicable law, or where we reasonably consider that we need to use it for another reason and that reason is compatible with the original purpose.

6. **Legal Bases for Processing.** For explanations of our legal bases for processing in jurisdictions where this disclosure is required, see Section 15, Supplemental Notice for Certain Jurisdictions, below.

11\. How We Share your Personal Data

------------------------------------

1. **Sharing to Provide Bluesky and Services**

1. **Your Posts and Public Profile.** Bluesky is a decentralized microblogging service where most user activity is public by design. This includes your posts, profile, likes, following, and blocks.

2. **Other Users You Share or Interact With.** Bluesky may allow you to share personal information, messages, or interact with other users.

3. **Third-party Services You Share or Interact With.** Bluesky may link to or allow you to interface, interact, share information with, direct us to share information with, access and/or use Third-party Services. If you do, the information you share will be subject to any Third-Party Service's privacy policy. For example, if you request that we share your personal information with a developer application or payment processor, we may facilitate the request.
```

## M014
**Case:** This service informs you that its Terms of Service does not apply to third-party services

**Passage:**

```
Pinterest may contain links to third-party websites, advertisers, services, software components, special offers or other events or activities that are not owned or controlled by us. We don’t endorse or assume any responsibility for any such third-party websites, information, materials, products or services. If you access any third-party website, service or content, etc. from Pinterest, you do so at your own risk and you agree that we have no liability arising from your use of, purchase from or access to any third-party website, service or content, etc.

More simply put

We allow users to include links to content outside Pinterest. We are not responsible for any content you view on, or your use of, third-party websites or services.

7\. Termination

===============

We may terminate or suspend your right to access or use Pinterest for any violation of these Terms. Where appropriate, we will provide you with written notice and you can appeal a decision that you think was made in error. For more information about how we enforce our policies or otherwise take action on content on Pinterest, please see our .

You can also terminate or delete your account at any time. You can find out in our Help Centre.

Upon termination, Sections 3, 8, 9, 10, 11, 12 and 13 of these Terms will continue to be in operation.

More simply put

We reserve the right to refuse Service to anyone and will provide notice of termination where appropriate.

8\. Indemnity

=============
```

## M015
**Case:** Specific content can be deleted without reason and may be removed without prior notice

**Passage:**

```
You have the right to withdraw from this contract within 14 days without giving any reason.

The withdrawal period will expire after 14 days from the day of the conclusion of the contract.

To exercise the right of withdrawal, you must inform us of your decision to withdraw from this contract by an unequivocal statement (e.g. a letter sent by post or e-mail). You can contact us by email at [account-withdrawal@google.com]; by phone +35 31800832663 (see below for country-specific telephone numbers); or by writing to us at Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Ireland. You may use the attached model withdrawal form, but it is not obligatory. You can also electronically fill in and submit the model withdrawal form or any other unequivocal statement on our website ([g.co/EEAWithdrawalForm]). If you use this option, we will communicate to you an acknowledgement of receipt of such a withdrawal on a durable medium (e.g. by e-mail) without delay.

To meet the withdrawal deadline, it is sufficient for you to send your communication concerning your exercise of the right of withdrawal before the withdrawal period has expired.

Effects of withdrawal
```

## M016
**Case:** Third-party cookies are used for advertising

**Passage:**

```
We may disclose all of these categories of Personal Data for a business purpose to service providers or other third parties, as outlined in this Policy.

2. **Disclosure of Personal Data.** As detailed in Section 11, How We Share your Personal Data, we may disclose the categories of Personal Data identified above to the following categories of third parties for various business purposes: other Bluesky companies, service providers, our professional advisers, business partners, other businesses as needed to provide our Services, and certain third parties where you have provided consent, where it is in connection with a corporate transaction, or where we are required by law or in connection with other legal process.

3. **Sources of Personal Data.** We collect Personal Data from you, from your browser or device when you interact with our Services, from our business partners and affiliates, from third parties you direct to share information with us, and from other third-party providers. For more information, see Section 13, Your Privacy Choices and Rights.

4. **Purpose for collection.** We collect Personal Data about you for the purposes described in Section 10, How We Use Personal Data.

5. **Notice of financial incentives.** We do not sell Personal Data collected about you, or share Personal Data collected about you for cross-context behavioural advertising. We do not currently send emails for direct marketing purposes.
```

## M017
**Case:** The data retention period is kept to the minimum necessary for fulfilling its purposes

**Passage:**

```
* We keep your usage information, such as the content you post, your interactions with other users’ content and how you interact with others on the platform for the duration of your account or until such content is removed.

* We keep your payment information, including your credit or debit card number and billing address for the duration you use our paid products and services. Records of transactions will be kept for longer, in accordance with applicable law.

* If you communicate with us, such as through email, we will keep information about the communication and its content for up to 18 months, unless it is necessary for us to retain it for a longer period to comply with our legal obligations or to exercise or defend our legal rights.

* We generally collect device information, location information, inferred identity information and log information using cookies. We keep cookies and information collected using cookies for up to 13 months. You can learn more about how we use cookies and similar technologies [here].

* We keep information about your views or interactions with ads on or off X, as well as how you interact with our content on third-party sites for up to 12 months.

* We keep information shared by ad and business partners for up to 12 months.
```

## M018
**Case:** If you offer suggestions to the service, they become the owner of the ideas that you give them

**Passage:**

```
By accessing or using Pinterest, you agree to comply with and be bound by these Terms and you will not attempt to circumvent them. If you do not agree to our Terms, you must not access or use Pinterest.

More simply put

Every company has its terms. These are ours. They include these Terms of Service and other policies listed above.

1\. The Service

===============

Pinterest helps to bring everyone the inspiration to create a life they love. To do that, we show you things we think will be relevant, interesting and personal to you based on your on-site and off-site activity. To provide the Service, we need to be able to identify you and your interests, and we use your personal data to do this. For more information, please read our . Some of the things we show you are promoted by advertisers. As part of the Service, we try to ensure that even promoted content is relevant and interesting to you. You can identify promoted content because it will be clearly labelled.

More simply put

Pinterest helps to bring everyone the inspiration to create a life they love. We'll use your interests to show you content and ads on and off Pinterest that are relevant to you.

2\. Using Pinterest

===================

### a. Who can use Pinterest
```

## M019
**Case:** The service claims that third parties it shares your personal information with are bound by confidentiality obligations

**Passage:**

```
X has carefully considered the legal reasons it is permitted to collect, use, share and otherwise process your information. If you want to dig in to learn more and better understand the nuances, we’d encourage you to check out [this additional information about data processing]. And no, we don’t sell your personal information.

**6.2 We move your data to make X work for you.**

Just as you use X to seamlessly participate in global conversations with people in countries all over the world, X must move information across borders and to different countries around the world to support the safe and reliable service you depend on. For example, if you live in Europe and are having a conversation with someone in the United States, information has to move between those countries to provide that experience – it’s what you expect from us.

We also use data centers and cloud providers, and engage [our affiliates] and third-party partners and [service providers] located in many parts of the world to help us provide our services. Before we move data between countries we look at the risks that may be presented to the data and rely on [standard contractual clauses] (SCCs), where applicable, to ensure your data rights are protected. To request a copy of the SCCs, please contact us [here]. If data will be shared with a third party, we require them to maintain the same protections over your data that we provide directly.
```

## M020
**Case:** You cannot distribute or disclose your account to third parties

**Passage:**

```
To protect your Google account, keep your password confidential. You should not reuse your Google account password on third-party applications. Learn more about [keeping your Google account secure], including what to do if you learn of any unauthorised use of your password or Google account.

**Your Information**

--------------------

Our [Privacy Policy] explains how we treat your personal data and protect your privacy when you use the Service. The [YouTube Kids Privacy Notice] provides additional information about our privacy practices that are specific to YouTube Kids.

We will process any audio or audiovisual content uploaded by you to the Service in accordance with the [YouTube Data Processing Terms], except in cases where you uploaded such content for personal purposes or household activities. [Learn More].

**Permissions and Restrictions**

--------------------------------

You may access and use the Service as made available to you, as long as you comply with this Agreement and the law. You may view or listen to Content for your personal, non-commercial use. You may also show YouTube videos through the embeddable YouTube player.

The following restrictions apply to your use of the Service. You are not allowed to:
```

## M021
**Case:** The service claims that third parties it shares your personal information with are bound by confidentiality obligations

**Passage:**

```
**With other X users.** Depending on your [settings], and based on the X products and services you use, we share:

* Your interactions with X content of other users, such as replies, and people you follow.

* Content you send to a specific X user, such as through [Direct Messages]. Please keep in mind that if you’ve shared information like Direct Messages or protected posts with someone else who accesses X through a third-party service, the information may be shared with the third-party service.

**With partners.** Depending on your [settings], we also provide certain third parties with information to help us offer or operate our products and services. You can learn more about these partnerships in our [Help Center]. You can control whether X shares your personal information with these partners by using the “Data sharing with business partners” option in your [Privacy and Safety settings]. (This setting does not control sharing described elsewhere in this Privacy Policy, such as when we share information with our service providers, or through partnerships other than as described in this [Help Center] article.)

**3.2 With third parties and third-party integrations.**
```

## M022
**Case:** You have a reduced time period to take legal action against the service

**Passage:**

```
with legal advice.

More simply put

If you post your Content on Pinterest, it still belongs to you. In using Pinterest, you agree to only post User Content that follows these Terms and our policies, is lawful and doesn’t violate anyone else’s rights. If you post User Content that is infringing, illegal or violates our Terms or policies, we can take action against the User Content and, where appropriate, your account. Where appropriate, you can appeal those actions.

### b. How we and other users can use your User Content
```

## M023
**Case:** This service assumes no liability for unauthorized access to your personal information

**Passage:**

```
To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, special, consequential or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, or any loss of data, use, goodwill or other intangible losses, resulting from (a) your access to or use of or inability to access or use the Service; (b) any conduct or content of any third party on the Service, including, without limitation, any defamatory, offensive or illegal conduct of other users or third parties; (c) unauthorised access, use or alteration of your transmissions or content.

In no event shall our aggregate liability for all claims relating to the Service exceed one hundred US dollars (US $100.00). The foregoing does not affect any liability that cannot be excluded or limited under applicable law.

If we cause damage to you and you're a consumer in the EEA or UK, the above doesn't apply. Instead, Pinterest's liability will be limited to foreseeable damages arising due to a breach of material contractual obligations typical for this type of contract. Pinterest isn't liable for damages that result from a non-material breach of any other applicable duty of care. This limitation of liability won't apply to any statutory liability that cannot be limited, to liability for death or personal injury caused by our negligence or willful misconduct, or to exclude our responsibility for something we have specifically promised to you.

More simply put
```

## M024
**Case:** This service does not guarantee that it or the products obtained through it meet your expectations or requirements

**Passage:**

```
By law, consumers have certain rights that cannot be excluded or altered by a contract. Nothing in this Agreement affects those rights you may have as a consumer. Other than as expressly stated in this Agreement or as required by law (see Legal Guarantee), YouTube does not give any specific promises about the Service. For example, we don’t give any additional promises about: the Content provided through the Service; the specific features of the Service, or its accuracy, reliability, availability, or ability to meet your needs; or that any Content you submit will be accessible or stored on the Service.

**Limitation of Liability**

---------------------------
```

## M025
**Case:** Alternative accounts are not allowed

**Passage:**

```
YouTube operates a system of “strikes” in respect of Content that violates the [YouTube Community Guidelines]. Each strike comes with varying restrictions and may result in the permanent removal of your channel from YouTube. A full description of how a strike affects your channel is available on the [Community Guidelines Strikes Basics] page. If you believe that a strike has been issued in error, you may [appeal here], in which case we will consider your appeal reasoning and reassess our decision.

If your channel has been restricted due to a strike, you must not use another channel to circumvent these restrictions. Violation of this prohibition is a material breach of this Agreement and Google reserves the right to terminate your Google account or your access to all or part of the Service.

**Copyright Protection**

------------------------

We provide information to help copyright holders manage their intellectual property online in our [YouTube Copyright Center]. If you believe your copyright has been infringed on the Service, please [send us a notice] .

We respond to notices of alleged copyright infringement according to the process in our [YouTube Copyright Center], where you can also find information about how to resolve a copyright strike. YouTube's policies provide for the termination, in appropriate circumstances, of repeat infringers’ access to the Service.

**Account Suspension & Termination**

====================================

**Terminations by You**
```

## M026
**Case:** Your content can be licensed to third parties

**Passage:**

```
By providing Content to the Service, you grant to YouTube and its Affiliates (including YouTube LLC, Google LLC and Google Commerce Limited) a worldwide, non-exclusive, royalty-free licence to use that Content (including to host, to make publicly available, reproduce, distribute, modify, display and perform it, taking into account the moral rights) for the sole purpose of operating, and improving the Service (including through the use of third-party service providers), and only to the extent necessary therefore.

**Licence to Other Users**

--------------------------

You also grant each other user of the Service a worldwide, non-exclusive, royalty-free licence to access your Content through the Service, and to use that Content (including to reproduce, distribute, modify, display, and perform it, taking into account the moral rights) only to the extent necessary therefore and as enabled by a feature of the Service.

**Duration of Licence**

-----------------------

The licences granted by you continue until the Content is removed as described below. Once removed, the licences will terminate, except where you permitted the further use of Content after your removal, or the law requires otherwise. For example, removal of Content by you does not require YouTube to: (a) recall Content that is being used by other users within any limited offline viewing functionality of the Service; or (b) delete copies we reasonably need to keep for legal purposes.

**Right to Monetize**
```

## M027
**Case:** Your private content may be accessed by people working for the service

**Passage:**

```
We may also use different signals and your data to infer, preserve, use, share, or disclose your age and identity information in order to comply with regulatory requirements as well as for safety, security, fraud, know-your-customer, know-your-business, and identity verification, as the case may be. We may also share or disclose your age and identity information with our partners, service providers, and others for these purposes.

**3.4 With our affiliates.**

We may share information amongst our [affiliates] to provide our products and services.

**3.5 As a result of a change in ownership.**

We may share, sell, or transfer information about you in connection with a merger, acquisition, reorganization, sale of assets, or bankruptcy. This Privacy Policy will apply to your personal information that is shared with (before and after the close of any transaction) or transferred to the new entity.

4\. How Long We Keep Information

--------------------------------

We keep different types of information for different periods of time, depending on how long we need to retain it in order to provide you with our products and services, to comply with our legal requirements and for safety and security reasons. For example:

* We keep your profile information, such as your display name, user name, password and email address for the duration of your account. We cannot provide you with our products and services without retaining this information.
```

## M028
**Case:** A free help desk is provided

**Passage:**

```
You may not use, access, download or otherwise make available the Service (including related software), except as authorised by applicable trade restrictions, including but not limited to US, EU and UK sanctions and export controls. You agree not to use the Service for any purpose prohibited by applicable trade restrictions.

Any use of Pinterest not expressly permitted by these Terms is a breach of these Terms and may violate copyright, trademark and other laws.

### b. Our licence to you

Subject to your compliance with these Terms and our policies, we hereby grant you a limited, non-exclusive, non-transferable, non-sublicensable and revocable licence to access and use the Service as contemplated under these Terms and our policies.

You may not permit Pinterest to be used by or for the benefit of unauthorised third parties. Nothing in these Terms will be construed as granting you any right to transfer or assign rights to access or use Pinterest. All rights not expressly granted to you are reserved by us and our licensors. Except as described in Section 3(b), you may not: (i) modify or make derivative works based upon the Service; (ii) reverse engineer the Service; (iii) copy any features or functions of the Service.

### c. Commercial use of Pinterest
```

## M029
**Case:** When the service wants to make a material change to its terms, you are notified at least 30 days in advance

**Passage:**

```
If you have a YouTube channel, you may be able to upload Content to the Service. You may use your Content to promote your business or artistic enterprise. If you choose to upload Content, you must not submit to the Service any Content that does not comply with this Agreement or the law. For example, the Content you submit must not include third-party intellectual property (such as copyrighted material) unless you have permission from that party or are otherwise legally entitled to do so (including by way of any available exceptions or limitations to copyright or related rights provided for in European Union law). You are legally responsible for the Content you submit to the Service. We may use automated systems that analyze your Content to help detect infringement and abuse, such as spam, malware, and illegal content.

**Rights you Grant**

--------------------

You retain all of your ownership rights in your Content. In short, what belongs to you stays yours. However, we do require you to grant certain rights to YouTube and other users of the Service, as described below.

**Licence to YouTube**

----------------------
```

## M030
**Case:** You shall not interfere with another person's enjoyment of the service

**Passage:**

```
1. access, reproduce, download, distribute, transmit, broadcast, display, sell, license, alter, modify or otherwise use any part of the Service or any Content except: (a) as specifically permitted by the Service; (b) with prior written permission from YouTube and, if applicable, the respective rights holders; or (c) as permitted by applicable law;

2. circumvent, disable, fraudulently engage, or otherwise interfere with the Service (or attempt to do any of these things), including security-related features or features that: (a) prevent or restrict the copying or other use of Content; or (b) limit the use of the Service or Content;

3. access the Service using any automated means (such as robots, botnets or scrapers) except: (a) in the case of public search engines, in accordance with YouTube’s robots.txt file; (b) with YouTube’s prior written permission; or (c) as permitted by applicable law;

4. collect or use any information that might identify a person (for example, harvesting usernames or faces), unless permitted by that person or allowed under section 3 above;

5. use the Service to distribute unsolicited promotional or commercial content or other unwanted or mass solicitations (spam);

6. cause or encourage any inaccurate measurements of genuine user engagement with the Service, including by paying people or providing them with incentives to increase a video’s views, likes, or dislikes, or to increase a channel’s subscribers, or otherwise manipulate metrics;
```

## M031
**Case:** Tracking pixels are used in service-to-user communication

**Passage:**

```
This Supplemental Notice for Brazil's General Data Protection Law (Law No. 13.709/2018 – the "**LGPD**") only applies to our processing of personal data that is subject to the LGPD. For purposes of the LGPD, personal information means any information relating to an identified or identifiable individual.

If you are a user of Bluesky App Services in Brazil, the below additional terms: (a) are incorporated into this Privacy Notice; (b) apply to your use of the Bluesky App Services, and (c) supersede and control over any conflicts in the rest of the Privacy Notice to the extent of any inconsistency.

1. **Legal bases.** We guarantee that the processing of personal information subject to the LGPD by us will be always carried out in accordance with one of the legal bases that include: (1) your consent; (2) compliance with legal or regulatory obligations; (3) execution of a contract with you; (4) to exercise our rights in contracts or judicial, administrative or arbitral proceedings; (5) the protection of your – or third parties' – life and physical safety; (6) our legitimate interests; (7) credit protection; (8) prevention of fraud and the safety of the data subject in processes of identification and authentication.

2. **Data Subject's Rights.** In addition to the rights outlined in section 7 of this Privacy Notice, for purposes of the LGPD you also have the right to:
```

## M032
**Case:** Sensitive data is collected and shared to target advertising

**Passage:**

```
* Information about your connection, such as your IP address, browser type, and related information.

* Information about your device and its settings, such as device and advertising ID, operating system, carrier, language, memory, apps installed, and battery level.

* Your device address book, if you’ve chosen to share it with us.

**Location information.** When you use X, we collect some information about your approximate location to provide the service you expect, including showing you relevant ads. You can also choose to share your current precise location or places where you’ve previously used X by enabling these settings in your account.

**Inferred identity.** We may collect or receive information that we use to infer your identity as detailed below:

* When you sign into X on a browser or device, we will associate that browser or device with your account. Subject to your settings, we may also associate your account with browsers or devices other than those you use to sign into X (or associate your signed-out device or browser with other browsers or devices or X-generated identiﬁers).
```

## M033
**Case:** This service assumes no responsibility and liability for the contents of links to other websites

**Passage:**

```
the detriment of the user of the Service.

**Third-Party Links**

---------------------

The Service may contain links to third-party websites and online services that are not owned or controlled by YouTube. YouTube has no control over, and assumes no responsibility for, such websites and online services. Be aware when you leave the Service; we suggest you read the terms and privacy policy of each third-party website and online service that you visit.

**About this Agreement**

========================

**Changing this Agreement**

---------------------------

We may change this Agreement in a reasonable manner, (1) to reflect changes to our Service or how we do business - for example, when we add new products or features or remove old ones, (2) for legal, regulatory, or security reasons, or (3) to prevent abuse or harm.

If we change this Agreement, we’ll provide you with at least 15 days’ advance notice before the changes take effect. When we notify you of changes, we’ll provide you with the new version of the terms and point out the material changes. If you don’t object before the changes take effect, you’ll be deemed to have accepted the changed terms. Our notice will explain this objection process. You can refuse to accept the changes, in which case the changes won’t apply to you, but we reserve the right to end our relationship with you if all other termination requirements are met.

**Continuation of this Agreement**

----------------------------------
```

## M034
**Case:** You agree to defend, indemnify, and hold the service harmless in case of a claim related to your use of the service

**Passage:**

```
If you use Pinterest for commercial purposes without agreeing to our as required by Section 2(c) of these Terms, you agree to indemnify and hold harmless Pinterest, Inc., Pinterest Europe Ltd. and their affiliates from any claims (including reasonable legal fees) relating to your use of our Service. Pinterest reserves the right, at its own cost, to assume the exclusive defence and control of any matter otherwise subject to indemnification, in which event you will fully cooperate with Pinterest.

More simply put

If you are a business user and Pinterest is sued because of your use of the Service, you’re financially responsible.

9\. Disclaimers

===============

To the extent permitted by applicable law, the Service and all content on Pinterest is provided on an 'as is' basis without warranty of any kind, whether express or implied.

Pinterest specifically disclaims any and all warranties and conditions of merchantability, fitness for a particular purpose and non-infringement, and any warranties arising out of course of dealing or usage of trade.

Pinterest takes no responsibility and assumes no liability for any User Content that you or any other person or third party posts or sends using the Service. You understand and agree that you may be exposed to User Content that is inaccurate, objectionable, inappropriate for children or otherwise unsuited to your purpose.
```

## M035
**Case:** Blocking first-party cookies may limit your ability to use the service

**Passage:**

```
Breaking down how we use the information we collect is not simple because of the way the systems that bring our services to you work. For example, the same piece of information may be used differently for different purposes to ultimately deliver a single service. We think it’s most useful to describe the five main ways we use information and if you have questions that are not answered, you can always [contact us]. Here we go:

**2.1 Operate, improve, and personalize our services.**

We use the information we collect to provide and operate X products and services. We also use the information we collect to improve and personalize our products and services so that you have a better experience on X, including by showing you more relevant content and ads, suggesting people and topics to follow, enabling and helping you discover [affiliates], third-party apps, and services. We may use the information we collect and publicly available information to help train our machine learning or artificial intelligence models for the purposes outlined in this policy.

We may use the information we collect from accounts of other services that you choose to connect to your X account to provide you features like cross-posting or cross-service authentication, and to operate our services.

We use your contact information to help others find your account if your settings permit, including through third-party services and client applications.
```

## M036
**Case:** You are responsible for maintaining the security of your account and for the activities on your account

**Passage:**

```
You acknowledge and agree that, as between you and us, we own all right, title and interest in and to Pinterest and all intellectual property rights (including but not limited to the copyrights, trademarks and patents) therein (the “Pinterest IP”) and you must not use any of the Pinterest IP, except as necessary for your permitted use of Pinterest. For clarity, Pinterest IP does not include User Content.

If you use Pinterest IP in breach of these Terms, your right to use Pinterest will terminate immediately and you must, at our option, return or destroy any copies of the Pinterest IP you have made. No right, title or interest in or to Pinterest or any Pinterest IP is transferred to you under these Terms, and we reserve all rights not expressly granted.

More simply put

We respect intellectual property, including copyrights and trademarks. You should, too.

5\. Security

============

We care about the security of our users. While we work to protect the security of your User Content and account, we can’t guarantee that unauthorised third parties won’t be able to defeat our security measures. Keep your password secure and do not disclose it to any other person or entity. Please notify us immediately of any unauthorised access to your account or any other breach of security.

More simply put

You can help us keep your account and Pinterest secure by bearing in mind.

6\. Third-party links, sites and services

=========================================
```

## M037
**Case:** You waive your right to a class action

**Passage:**

```
Arbitration is a more informal way to resolve our disagreements than a lawsuit in court. By accepting these Terms, you agree that the US Federal Arbitration Act governs the interpretation and enforcement of this Section, and that you and Pinterest are each waiving the right to a trial by jury or to participate in a class action. The arbitrator also has exclusive authority to resolve any dispute relating to the interpretation, applicability or enforceability of this binding arbitration agreement, including any dispute regarding arbitrability.

Any arbitration will be administered by the American Arbitration Association ("AAA") under the applicable rules then in effect for the AAA. If the AAA rules conflict in any way with these Terms, the Terms will govern. You can find AAA’s forms at . The arbitrator shall issue a reasoned written decision explaining the essential findings and conclusions on which the award is based. A judgment on the arbitrator’s award may be entered in any court of competent jurisdiction. Where the AAA’s Consumer Arbitration Rules apply, if the arbitrator determines that a party’s claim was frivolous or brought for an improper purpose, the arbitrator must assign all fees and costs associated with the arbitration to that party.
```

## M038
**Case:** If you are the target of a copyright claim, your content and/or your account may be removed

**Passage:**

```
You will only post User Content that you have the rights to post, and you won’t post User Content that infringes the intellectual property rights of others (e.g. copyright infringement, trademark infringement or counterfeit), or that is otherwise unlawful, unless an exception or limitation applies under applicable law. We can take action against User Content that violates these Terms or our policies or where we are permitted or required by law, such as by removing, restricting or limiting access to, or distribution of, the content. We can also suspend or terminate accounts of users who repeatedly or seriously infringe third-party intellectual property rights, violate the law, these Terms or our policies, or where permitted or required to do so by law. We are a neutral intermediary and we do not review all User Content before or after it is published on the Service, so we are not responsible for or liable to any third party for the content or accuracy of any User Content posted by you or any other Pinterest user. For more information about how we enforce our policies or otherwise take action on content on Pinterest, see our . Where appropriate, you can appeal the decisions you think were made in error. You may have a right under local law to bring a claim for breach of contract if you believe we have breached these Terms by removing, restricting or limiting access to, or distribution of, your User Content, or suspending or terminating your account. Pinterest cannot provide you
```

## M039
**Case:** You can opt out of targeted advertising

**Passage:**

```
13\. Your Privacy Choices and Rights

------------------------------------

1. **Your Privacy Choices.** The privacy choices you have about your Personal Data information are determined by applicable law and are described below.

1. **Email Communications.** If you receive a marketing email from us, you may opt out by using the unsubscribe link at the bottom of such email. You will continue to receive transaction-related, non-promotional emails related to Bluesky. You will not be opted out of those communications.

2. **Mobile Devices.** We may send you push notifications through our App when you enable them. You may opt out from receiving these push notifications by changing the settings on your mobile device. We may collect precise location-based information via the App, but only if you permit us to do so. You may opt out of this collection by changing the settings on your mobile device.

3. **"Do Not Track".** Do Not Track (**"DNT"**) is a privacy preference that users can set in certain web browsers. Please note that we currently do not respond to or honor DNT signals or similar mechanisms transmitted by web browsers, as there is no consistent industry standard for compliance.

2. **Your Privacy Rights.** Depending on what laws apply to your Personal Data, you may have the right to:
```

## M040
**Case:** When the service wants to make a material change to its terms, you are notified at least 30 days in advance

**Passage:**

```
===================================

If you are a consumer in the EEA, Switzerland or the UK, these Terms and your use of the Service shall be governed by the law of the country where you live, and any claim, dispute, or controversy arising from or in connection with or relating to these Terms, Pinterest, or the Service shall be resolved in the courts of the country where you live.

In all other cases, these Terms and your use of the Service shall be governed by the laws of the State of California, without respect to its conflict of laws principles. For any actions not subject to Section 11 (Arbitration), the exclusive place of jurisdiction for any claim, dispute or controversy arising from or in connection with these Terms or the Service is San Francisco County, California, or the United States District Court for the Northern District of California, and such disputes will be determined under California law.

More simply put

The Bay Area is beautiful at this time of year. In fact, it doesn't matter what time of year it is, that's what's so great! Let’s resolve any disputes in California. If you are a consumer in the EEA, Switzerland or the UK, however, you can file disputes in your home courts.

13\. General terms

==================

### a. Notification procedures and changes to these Terms
```

## M041
**Case:** Your personal data may be sold unless you opt out

**Passage:**

```
13\. Your Privacy Choices and Rights

------------------------------------

1. **Your Privacy Choices.** The privacy choices you have about your Personal Data information are determined by applicable law and are described below.

1. **Email Communications.** If you receive a marketing email from us, you may opt out by using the unsubscribe link at the bottom of such email. You will continue to receive transaction-related, non-promotional emails related to Bluesky. You will not be opted out of those communications.

2. **Mobile Devices.** We may send you push notifications through our App when you enable them. You may opt out from receiving these push notifications by changing the settings on your mobile device. We may collect precise location-based information via the App, but only if you permit us to do so. You may opt out of this collection by changing the settings on your mobile device.

3. **"Do Not Track".** Do Not Track (**"DNT"**) is a privacy preference that users can set in certain web browsers. Please note that we currently do not respond to or honor DNT signals or similar mechanisms transmitted by web browsers, as there is no consistent industry standard for compliance.

2. **Your Privacy Rights.** Depending on what laws apply to your Personal Data, you may have the right to:
```

## M042
**Case:** Your personal data may be sold unless you opt out

**Passage:**

```
**Third-party content and integrations.** We share or disclose your information with your consent or at your direction, such as when you [authorize a third-party web client or application] to access your account or when you direct us to share your feedback with a business. Similarly, to improve your experience, we work with third-party partners to display their video content on X or to allow cross-platform sharing. When you watch or otherwise interact with content from our video or cross-platform sharing partners, they may receive and process your personal information as described in their privacy policies. For video content, you can adjust your [autoplay settings] if you prefer that content not to play automatically.

**Third-party collaborators.** Depending on your [settings], or if you decide to share your data, we may share or disclose your information with third parties. If you do not opt out, in some instances the recipients of the information may use it for their own independent purposes in addition to those stated in X’s Privacy Policy, including, for example, to train their artificial intelligence models, whether generative or otherwise.
```

## M043
**Case:** The service claims to be GDPR compliant for European users

**Passage:**

```
Our approach to privacy compliance is broader than simply complying with the terms of the GDPR, the UK GDPR, the CCPA and the array of other data protection laws and regulations that apply to our global business. Rather, we think about how our work can benefit as many of our users as possible and work towards legal compliance in a way that strengthens our comprehensive data security and privacy program, and supports the evolution of our principles and overarching mission as a company.

We want to help people understand how we work to give them the transparency and tools they need to have meaningful controls over what data we collect about them, how it is used, and when it is shared.

Our teams are consistently working behind the scenes to understand new legal requirements and user expectations to ensure \>x< is prepared to meet the commitments we made to our users and to provide an industry-leading level of transparency and user control. You will continue to see us make updates across our core product, terms, policies, user functionality and operations to keep these commitments to the people who rely on us to engage in the public conversation.

**If you are an \>x< user**, you can find out more information in our [privacy policy].
```

## M044
**Case:** App required for this service requires broad device permissions

**Passage:**

```
3. **Deidentified information.** We may receive or process Personal Data to create deidentified information that can no longer reasonably be used to infer information about, or otherwise be linked to, a particular individual or household. Where we maintain deidentified information, we will maintain and use it in deidentified form and will not try to reidentify the information except as required or permitted by applicable law.

4. **Appeals.** If you are a resident of certain U.S. States, you have the right to appeal decisions regarding your privacy requests. All appeal requests should be submitted using the contact details found in Section 18, Contact Us. If your appeal is denied, you may contact your local Attorney General.

5. **CALIFORNIA SPECIFIC DISCLOSURES** The following disclosures only apply to California residents:

1. **Personal Data collection.** California law requires that we provide disclosures to you about what Personal Data we collect by reference to the categories of Personal Data set forth within California law. To address this obligation, we have identified the relevant California Personal Data category for the Personal Data set out in Section 8, Personal Data we Collect:

1. **Identifiers** like your name, address, phone number, email address, passport or other government identity information including driver's licence information, account information, or other similar identifiers.
```

## M045
**Case:** When the service wants to make a material change to its terms, you are notified at least 30 days in advance

**Passage:**

```
the detriment of the user of the Service.

**Third-Party Links**

---------------------

The Service may contain links to third-party websites and online services that are not owned or controlled by YouTube. YouTube has no control over, and assumes no responsibility for, such websites and online services. Be aware when you leave the Service; we suggest you read the terms and privacy policy of each third-party website and online service that you visit.

**About this Agreement**

========================

**Changing this Agreement**

---------------------------

We may change this Agreement in a reasonable manner, (1) to reflect changes to our Service or how we do business - for example, when we add new products or features or remove old ones, (2) for legal, regulatory, or security reasons, or (3) to prevent abuse or harm.

If we change this Agreement, we’ll provide you with at least 15 days’ advance notice before the changes take effect. When we notify you of changes, we’ll provide you with the new version of the terms and point out the material changes. If you don’t object before the changes take effect, you’ll be deemed to have accepted the changed terms. Our notice will explain this objection process. You can refuse to accept the changes, in which case the changes won’t apply to you, but we reserve the right to end our relationship with you if all other termination requirements are met.

**Continuation of this Agreement**

----------------------------------
```

## M046
**Case:** Referring and/or exit pages are tracked

**Passage:**

```
1. **Usage Information.** When you use Bluesky, we collect certain information automatically, including your Internet protocol (IP) address (which can be used to derive your general location), user settings, cookie identifiers, mobile carrier, other unique identifiers, browser or device information, and Internet service provider (ISP). We may also collect personal information about your use of Bluesky, including the posts you view on Bluesky, the links you click within Bluesky, and the frequency and duration of your activities.

2. **Cookies (and Other Technologies).** We and third parties that provide content or other functionality on Bluesky may use cookies, pixel tags, and other technologies (**"Tracking Technologies"**) to automatically collect information. See Section 9, Cookies, for more information.

3. **Personal Data We Collect from Other Sources**

1. **Third Parties, generally.** We may collect personal information from third parties. For example, you may direct a developer application or other third-party social networking application to share personal information with us or you may live in a jurisdiction that requires age verification and we will collect information from a third-party provider telling us whether you meet certain age requirements.
```

## M047
**Case:** No guarantee is given regarding quality

**Passage:**

```
1. access, reproduce, download, distribute, transmit, broadcast, display, sell, license, alter, modify or otherwise use any part of the Service or any Content except: (a) as specifically permitted by the Service; (b) with prior written permission from YouTube and, if applicable, the respective rights holders; or (c) as permitted by applicable law;

2. circumvent, disable, fraudulently engage, or otherwise interfere with the Service (or attempt to do any of these things), including security-related features or features that: (a) prevent or restrict the copying or other use of Content; or (b) limit the use of the Service or Content;

3. access the Service using any automated means (such as robots, botnets or scrapers) except: (a) in the case of public search engines, in accordance with YouTube’s robots.txt file; (b) with YouTube’s prior written permission; or (c) as permitted by applicable law;

4. collect or use any information that might identify a person (for example, harvesting usernames or faces), unless permitted by that person or allowed under section 3 above;

5. use the Service to distribute unsolicited promotional or commercial content or other unwanted or mass solicitations (spam);

6. cause or encourage any inaccurate measurements of genuine user engagement with the Service, including by paying people or providing them with incentives to increase a video’s views, likes, or dislikes, or to increase a channel’s subscribers, or otherwise manipulate metrics;
```

## M048
**Case:** Your personal information may be collected, regardless of whether you interacted directly with the service or not

**Passage:**

```
1. **No Targeted Advertising Sales.** We do not sell or share Personal Data for the purpose of displaying advertisements that are selected based on Personal Data from your activities on or use of Bluesky ("**Targeted Advertising**").

2. **Sensitive information.** We may disclose sensitive information for a business purpose like those described below, we do not sell or share sensitive information for the purpose of Targeted Advertising.

The following Personal Data elements we, or our service providers, collect may be classified as "sensitive" under certain privacy laws ("**Sensitive Information**") including:

1. username and password;

2. birthday;

3. telephone number;

4. government identifiers (like driver's license numbers);

5. payment information; and

6. confirmation that a user is 18 years old or older.

We use this sensitive information for the purposes described in Section 10, How We Use Personal Data, to the extent necessary to operate Bluesky and our Services, to enter into and perform on a contract with you, to comply with legal and regulatory requirements, to protect the safety of our users and third parties, or as otherwise permissible for our own internal purposes consistent with applicable laws.
```

## M049
**Case:** This service is only available for use individually and non-commercially

**Passage:**

```
You may not use, access, download or otherwise make available the Service (including related software), except as authorised by applicable trade restrictions, including but not limited to US, EU and UK sanctions and export controls. You agree not to use the Service for any purpose prohibited by applicable trade restrictions.

Any use of Pinterest not expressly permitted by these Terms is a breach of these Terms and may violate copyright, trademark and other laws.

### b. Our licence to you

Subject to your compliance with these Terms and our policies, we hereby grant you a limited, non-exclusive, non-transferable, non-sublicensable and revocable licence to access and use the Service as contemplated under these Terms and our policies.

You may not permit Pinterest to be used by or for the benefit of unauthorised third parties. Nothing in these Terms will be construed as granting you any right to transfer or assign rights to access or use Pinterest. All rights not expressly granted to you are reserved by us and our licensors. Except as described in Section 3(b), you may not: (i) modify or make derivative works based upon the Service; (ii) reverse engineer the Service; (iii) copy any features or functions of the Service.

### c. Commercial use of Pinterest
```

## M050
**Case:** You aren’t forced into binding arbitration in case of disputes

**Passage:**

```
We may revise, add or remove any or all portions of these Terms from time to time and the most current version will always be posted on our website. Unless otherwise required by law, we will notify you of any material changes to these Terms before any update enters into effect. Your continued access to or use of Pinterest after such an update constitutes your binding acceptance of such changes. Disputes arising under these Terms will be resolved in accordance with the version of these Terms in place at the time the dispute arose. For clarity, by continuing to use Pinterest, you are agreeing to be bound by the then-current version of these Terms.

More simply put

If we're making a material change to the Terms, we'll let you know ahead of time. If you don’t agree with the new Terms, please stop using Pinterest.

### b. Assignment

If you’re a consumer in the EEA, Switzerland or the UK, either you or we may assign this agreement, and any rights and licences granted under it, to a third party. In all other cases, these Terms, and any rights and licences granted hereunder, may not be transferred or assigned by you, but may be assigned by us without restriction. Any attempted transfer or assignment in violation hereof shall be null and void.

In case of such an assignment by us, you are entitled to terminate the agreement with immediate effect by deactivating your account. We will provide you with reasonable notice of any such assignment.

### c. Entire agreement/severability
```

## M051
**Case:** Information is provided about how your personal data is collected

**Passage:**

```
You can access, correct, or modify the information you provided to us by editing your profile and adjusting your account [settings].

* You can learn more about the information we have collected or inferred about you in [][Your X Data] and request access to additional information [][here].

* You can download a copy of your information, such as your posts, by following the instructions [here].

To protect your privacy and maintain security, we take steps to verify your identity before granting you access to your personal information or complying with a deletion, portability, or other related request. We may, in certain situations, reject your request for access, correction, or portability, for example, we may reject access where you are unable to verify your identity.

**5.2 Deleting your information.**

If you follow the instructions [here], your account will be deactivated and your data will be queued for deletion. When deactivated, your X account, including your display name, username, and public profile, will no longer be viewable on X.com, X for iOS, and X for Android. For up to 30 days after deactivation it is still possible to restore your X account if it was accidentally or wrongfully deactivated.

**5.3 Objecting to, restricting, or withdrawing your consent.**
```

## M052
**Case:** You are tracked via web beacons, tracking pixels, browser fingerprinting, and/or device fingerprinting

**Passage:**

```
* Information about your connection, such as your IP address, browser type, and related information.

* Information about your device and its settings, such as device and advertising ID, operating system, carrier, language, memory, apps installed, and battery level.

* Your device address book, if you’ve chosen to share it with us.

**Location information.** When you use X, we collect some information about your approximate location to provide the service you expect, including showing you relevant ads. You can also choose to share your current precise location or places where you’ve previously used X by enabling these settings in your account.

**Inferred identity.** We may collect or receive information that we use to infer your identity as detailed below:

* When you sign into X on a browser or device, we will associate that browser or device with your account. Subject to your settings, we may also associate your account with browsers or devices other than those you use to sign into X (or associate your signed-out device or browser with other browsers or devices or X-generated identiﬁers).
```

## M053
**Case:** Sensitive data is collected and shared to target advertising

**Passage:**

```
1. **No Targeted Advertising Sales.** We do not sell or share Personal Data for the purpose of displaying advertisements that are selected based on Personal Data from your activities on or use of Bluesky ("**Targeted Advertising**").

2. **Sensitive information.** We may disclose sensitive information for a business purpose like those described below, we do not sell or share sensitive information for the purpose of Targeted Advertising.

The following Personal Data elements we, or our service providers, collect may be classified as "sensitive" under certain privacy laws ("**Sensitive Information**") including:

1. username and password;

2. birthday;

3. telephone number;

4. government identifiers (like driver's license numbers);

5. payment information; and

6. confirmation that a user is 18 years old or older.

We use this sensitive information for the purposes described in Section 10, How We Use Personal Data, to the extent necessary to operate Bluesky and our Services, to enter into and perform on a contract with you, to comply with legal and regulatory requirements, to protect the safety of our users and third parties, or as otherwise permissible for our own internal purposes consistent with applicable laws.
```

## M054
**Case:** Third-party cookies are used for statistics

**Passage:**

```
**Cookies and similar technologies.** Like many websites, we use cookies and similar technologies to collect additional website usage data and to operate our services. Cookies are not required for many parts of our products and services such as searching and looking at public proﬁles. You can learn more about how we use cookies and similar technologies [here].

**Interactions with our content on third-party sites.** When you view our content on third-party websites that integrate X content, such as embedded timelines or post buttons, we may receive log information that includes the web page you visited.

**1.3 Information we receive from third parties.**

When you use other online products and services, they may share information about that usage with us.**
```

## M055
**Case:** The service claims to be GDPR compliant for European users

**Passage:**

```
Our services are not directed to children, and you may not use our services if you are under the age of 13. You must also be old enough to consent to the processing of your personal data in your country (in some countries we may allow your [parent or guardian to do so on your behalf]). We do not knowingly collect personal information from children under 13. If you become aware that your child has provided us with personal information without your consent, please contact us [here]. If we become aware that a child under 13 has provided us with personal information, we take steps to remove such information and terminate the child’s account. You can find additional resources for parents and teens [here].

Our services are not directed to children, and you may not use our services if you are under the age of 13. You must also be old enough to consent to the processing of your personal data in your country (in some countries we may allow your [parent or guardian to do so on your behalf]). We do not knowingly collect personal information from children under 13. If you become aware that your child has provided us with personal information without your consent, please contact us [here]. If we become aware that a child under 13 has provided us with personal information, we take steps to remove such information and terminate the child’s account. You can find additional resources for parents and teens [here].

8\. Changes To This Privacy Policy

----------------------------------
```

## M056
**Case:** The service assumes no liability for any damages the user incurs

**Passage:**

```
1. In the event of intent, gross negligence or of a breach of a contractual core duty, the fulfillment of which enables the proper implementation of this contract in the first place, and upon the fulfillment of which the other party regularly may rely ("cardinal obligation") also by its representatives and vicarious agents (_Erfüllungsgehilfen_), both You and YouTube shall be liable according to the statutory provisions. The same shall apply in the event of injury to life, body or health, in the event of damages resulting from a violation of a guarantee as to quality (_Beschaffenheitsgarantie_), in case of a procurement risk as well as in the event of defaults concealed fraudulently (_arglistig verschwiegene Mängel_). In the event of damages to property and financial damages (_Sach- und Vermögensschäden_) caused by slight negligence of either You or YouTube, its representatives or vicarious agents, and not resulting from a violation of a guarantee, a procurement risk or a breach of a cardinal obligation, liability shall be limited to the amount of the damage which was foreseeable at the time of conclusion of the contract and typical taking into account the nature of the contract (_vorhersehbarer und vertragstypischer Schaden_). Liability based on the German Product Liability Act (_Produkthaftungsgesetz_) shall remain unaffected in any case. Any further liability of either party other than set out above shall be excluded. This does not entail a change in the burden of proof to
```

## M057
**Case:** Your personal information may be collected, regardless of whether you interacted directly with the service or not

**Passage:**

```
1. **Usage Information.** When you use Bluesky, we collect certain information automatically, including your Internet protocol (IP) address (which can be used to derive your general location), user settings, cookie identifiers, mobile carrier, other unique identifiers, browser or device information, and Internet service provider (ISP). We may also collect personal information about your use of Bluesky, including the posts you view on Bluesky, the links you click within Bluesky, and the frequency and duration of your activities.

2. **Cookies (and Other Technologies).** We and third parties that provide content or other functionality on Bluesky may use cookies, pixel tags, and other technologies (**"Tracking Technologies"**) to automatically collect information. See Section 9, Cookies, for more information.

3. **Personal Data We Collect from Other Sources**

1. **Third Parties, generally.** We may collect personal information from third parties. For example, you may direct a developer application or other third-party social networking application to share personal information with us or you may live in a jurisdiction that requires age verification and we will collect information from a third-party provider telling us whether you meet certain age requirements.
```

## M058
**Case:** You waive your right to a class action

**Passage:**

```
All disputes must be brought in the party's individual capacity and not as a member in any class or representative proceeding. You agree that, by entering into these Terms, you are waiving the right to a trial by jury or to participate in a class action.

Nothing in these Terms shall affect any non-waivable statutory rights that apply to you. To the extent that any dispute isn’t arbitrable under applicable laws or otherwise, you agree that the dispute will be resolved exclusively in accordance with Section 12 of these Terms.

**Batched arbitration**: To provide a more efficient arbitration process, you and we each agree that if 25 or more similar arbitration demands are filed within a 60-day period or with the assistance of the same law firm or group of law firms, AAA will consolidate the arbitration demands. For each batch, AAA will administer one set of filing and administrative fees per side, per batch, and AAA will appoint one arbitrator to resolve each batch as a single consolidated arbitration. Arbitration demands are similar if they arise from similar facts and raise similar legal issues while seeking similar relief. Any dispute about similarity will be submitted to a single arbitrator, whose fees will be paid by us.

More simply put

You agree to notify us of any dispute and try to resolve it amicably. If that doesn’t work, the dispute will be efficiently decided through arbitration, not in court.

12\. Governing law and jurisdiction
```

## M059
**Case:** Third-party cookies are used for advertising

**Passage:**

```
1. **Usage Information.** When you use Bluesky, we collect certain information automatically, including your Internet protocol (IP) address (which can be used to derive your general location), user settings, cookie identifiers, mobile carrier, other unique identifiers, browser or device information, and Internet service provider (ISP). We may also collect personal information about your use of Bluesky, including the posts you view on Bluesky, the links you click within Bluesky, and the frequency and duration of your activities.

2. **Cookies (and Other Technologies).** We and third parties that provide content or other functionality on Bluesky may use cookies, pixel tags, and other technologies (**"Tracking Technologies"**) to automatically collect information. See Section 9, Cookies, for more information.

3. **Personal Data We Collect from Other Sources**

1. **Third Parties, generally.** We may collect personal information from third parties. For example, you may direct a developer application or other third-party social networking application to share personal information with us or you may live in a jurisdiction that requires age verification and we will collect information from a third-party provider telling us whether you meet certain age requirements.
```

## M060
**Case:** Many third parties are involved in operating the service

**Passage:**

```
**With other X users.** Depending on your [settings], and based on the X products and services you use, we share:

* Your interactions with X content of other users, such as replies, and people you follow.

* Content you send to a specific X user, such as through [Direct Messages]. Please keep in mind that if you’ve shared information like Direct Messages or protected posts with someone else who accesses X through a third-party service, the information may be shared with the third-party service.

**With partners.** Depending on your [settings], we also provide certain third parties with information to help us offer or operate our products and services. You can learn more about these partnerships in our [Help Center]. You can control whether X shares your personal information with these partners by using the “Data sharing with business partners” option in your [Privacy and Safety settings]. (This setting does not control sharing described elsewhere in this Privacy Policy, such as when we share information with our service providers, or through partnerships other than as described in this [Help Center] article.)

**3.2 With third parties and third-party integrations.**
```

## M061
**Case:** This service assumes no liability for unauthorized access to your personal information

**Passage:**

```
You acknowledge and agree that, as between you and us, we own all right, title and interest in and to Pinterest and all intellectual property rights (including but not limited to the copyrights, trademarks and patents) therein (the “Pinterest IP”) and you must not use any of the Pinterest IP, except as necessary for your permitted use of Pinterest. For clarity, Pinterest IP does not include User Content.

If you use Pinterest IP in breach of these Terms, your right to use Pinterest will terminate immediately and you must, at our option, return or destroy any copies of the Pinterest IP you have made. No right, title or interest in or to Pinterest or any Pinterest IP is transferred to you under these Terms, and we reserve all rights not expressly granted.

More simply put

We respect intellectual property, including copyrights and trademarks. You should, too.

5\. Security

============

We care about the security of our users. While we work to protect the security of your User Content and account, we can’t guarantee that unauthorised third parties won’t be able to defeat our security measures. Keep your password secure and do not disclose it to any other person or entity. Please notify us immediately of any unauthorised access to your account or any other breach of security.

More simply put

You can help us keep your account and Pinterest secure by bearing in mind.

6\. Third-party links, sites and services

=========================================
```

## M062
**Case:** The service can stop being provided at any time

**Passage:**

```
-----------------------

You may stop using the Service at any time. You can also [delete the Service] from your Google Account, which involves closing your YouTube channel and removing your data, with the option to download a copy of your data first.

**Terminations and Suspensions by YouTube**

-------------------------------------------

YouTube reserves the right to suspend or terminate your Google account or your access to all or part of the Service if: (a) you materially or repeatedly breach this Agreement; (b) we are required to do so to comply with a legal requirement or a court order; or (c) there are objective and concrete reasons to believe there has been conduct that creates liability or harm to any user, other third party, YouTube or our Affiliates.

**Notice for Termination or Suspension**

----------------------------------------

We will notify you with the reason for termination or suspension by YouTube, and where such action is taken for cause, we will give you the opportunity to remedy or stop the stated behaviour, unless there are objective and concrete reasons to believe that to do so: (a) would violate the law or the direction of a legal enforcement authority; (b) would compromise an investigation or (c) would substantially compromise the integrity, operation or security of the Service; or (d) would cause substantial harm to any user, other third party, YouTube or our Affiliates.

**Effect of Account Suspension or Termination**
```

## M063
**Case:** You must create an account to use this service

**Passage:**

```
**Your Use of the Service**

===========================

**Content on the Service**

--------------------------

The content on the Service includes videos, audio (for example music and other sounds), graphics, photos, text (such as comments and scripts), branding (including trade names, trademarks, service marks, or logos), interactive features, software, metrics, and other materials (collectively, "Content”). Content may be provided to the Service and distributed by our users and YouTube is a provider of hosting services for such Content. Content is the responsibility of the person or entity that provides it to the Service. If you see any Content you believe does not comply with these terms, such as by violating the [Community Guidelines] or the law, you can [report it to us].

**Google Accounts and YouTube Channels**

----------------------------------------

Some parts of the Service may be available without a [Google account]. However, you do need a Google account to use certain features. With a Google account, you may be able to like videos, subscribe to channels, create your own YouTube channel, and more. You can follow these instructions to [create a Google account].

Creating a YouTube channel will give you access to additional features and functions, such as uploading videos, making comments or creating playlists. Here are some details about how to [create your own YouTube channel].
```

## M064
**Case:** Promises will be kept after a merger or acquisition

**Passage:**

```
We may also use different signals and your data to infer, preserve, use, share, or disclose your age and identity information in order to comply with regulatory requirements as well as for safety, security, fraud, know-your-customer, know-your-business, and identity verification, as the case may be. We may also share or disclose your age and identity information with our partners, service providers, and others for these purposes.

**3.4 With our affiliates.**

We may share information amongst our [affiliates] to provide our products and services.

**3.5 As a result of a change in ownership.**

We may share, sell, or transfer information about you in connection with a merger, acquisition, reorganization, sale of assets, or bankruptcy. This Privacy Policy will apply to your personal information that is shared with (before and after the close of any transaction) or transferred to the new entity.

4\. How Long We Keep Information

--------------------------------

We keep different types of information for different periods of time, depending on how long we need to retain it in order to provide you with our products and services, to comply with our legal requirements and for safety and security reasons. For example:

* We keep your profile information, such as your display name, user name, password and email address for the duration of your account. We cannot provide you with our products and services without retaining this information.
```

## M065
**Case:** Information is provided about security practices

**Passage:**

```
We use your information to provide our advertising and sponsored content services subject to your [settings], which helps make ads on X more relevant to you. We also use this information to measure the effectiveness of ads and to help recognize your devices to serve you ads on and off of X. Some of our ad partners also enable us to collect similar information directly from their website or app by integrating our advertising technology. Information shared by ad partners and affiliates or collected by X from the websites and apps of ad partners and affiliates may be combined with the other information you share with X and that X receives, generates, or infers about you, as described elsewhere in our Privacy Policy.

**2.2 Foster safety and security.**

We use information we collect to provide for the safety and security of our users, our products, services, and your account. This includes verifying your identity, authenticating your account, estimating or verifying your age as may be required under law, and defending against fraud, unauthorized use, and illegal activity. We also use the information to evaluate and affect the safety and quality of content on X - this includes investigating and enforcing our policies and terms, as well as applicable law.

**2.3 Measure, analyze and make our services better.**
```

## M066
**Case:** You aren’t forced into binding arbitration in case of disputes

**Passage:**

```
We are building the best Service we can, but it won't always be perfect. We're not liable for various losses or damages.

11\. Arbitration

================

If you are a consumer in the EEA, Switzerland or the United Kingdom (UK), Section 11 does not apply to you.

For any dispute you have with us, you agree to first contact us and try to resolve the dispute informally. To the extent permitted by law, neither party may initiate any legal proceeding – whether in court, arbitration or any other forum – until the Notice of Dispute and Informal Dispute Resolution processes described below are complete. Nothing in this Section, however, will prevent either you or us from seeking temporary injunctive relief in court (or in arbitration) to preserve the status quo or to help enforce this arbitration clause at the outset of any dispute.
```

## M067
**Case:** Information is provided about how your personal data is collected

**Passage:**

```
* **Preferences.** When you set your preferences using your [settings], we collect that information so that we can respect your preferences.

* **Biometric information.** Based on your consent, we may collect and use your biometric information for safety, security, and identification purposes.

* **Job applications / recommendations.** We may collect and use your personal information (such as your biographical information, employment history, educational history, employment preferences, skills and abilities, and job search activity and engagement, in addition to the information we already collect as disclosed in the “Information we collect when you use X” section of our Privacy Policy below) to recommend potential jobs to you, to share with potential employers when you apply for a job, to enable connections for professional opportunities, and to show you more relevant advertising.

**1.2 Information we collect when you use X.**

When you use our services, we collect information about how you use our products and services. We use that information to provide you with products and services, to help keep X more secure and respectful for everyone, and more relevant to you.

**Usage information.** We collect information about your activity on X, including:
```

## M068
**Case:** Information is provided about how your personal data is collected

**Passage:**

```
* When you provide other information to X, including an email address or phone number, we associate that information with your X account. Subject to your settings, we may also use this information in order to infer other information about you and/or your identity, for example by associating your account with hashes of email addresses that share common components with the email address you have provided to X.

* When you access X and are not signed in, we may infer your identity based on the information we collect.

**Log information.** We may receive information when you view content on or otherwise interact with our products and services, even if you have not created an account or are signed out, such as:

* IP address and related information; browser type and language; operating system; the referring webpage; access times; pages visited; location; your mobile carrier; device information (including device and application IDs); search terms and IDs (including those not submitted as queries); ads shown to you on X; X-generated identiﬁers; and identiﬁers associated with cookies. We also receive log information when you click on, view, or interact with links on our services, including when you install another application through X.

**Advertisements.** When you view or interact with ads we serve on or oﬀ X, we may collect information about those views or interactions (e.g., watching a video ad or preroll, clicking on an ad, interacting with reposts of or replies to an ad).
```

## M069
**Case:** If you are the target of a copyright claim, your content and/or your account may be removed

**Passage:**

```
YouTube operates a system of “strikes” in respect of Content that violates the [YouTube Community Guidelines]. Each strike comes with varying restrictions and may result in the permanent removal of your channel from YouTube. A full description of how a strike affects your channel is available on the [Community Guidelines Strikes Basics] page. If you believe that a strike has been issued in error, you may [appeal here], in which case we will consider your appeal reasoning and reassess our decision.

If your channel has been restricted due to a strike, you must not use another channel to circumvent these restrictions. Violation of this prohibition is a material breach of this Agreement and Google reserves the right to terminate your Google account or your access to all or part of the Service.

**Copyright Protection**

------------------------

We provide information to help copyright holders manage their intellectual property online in our [YouTube Copyright Center]. If you believe your copyright has been infringed on the Service, please [send us a notice] .

We respond to notices of alleged copyright infringement according to the process in our [YouTube Copyright Center], where you can also find information about how to resolve a copyright strike. YouTube's policies provide for the termination, in appropriate circumstances, of repeat infringers’ access to the Service.

**Account Suspension & Termination**

====================================

**Terminations by You**
```

## M070
**Case:** This service cannot be held responsible for disputes that you may have with other users

**Passage:**

```
You will only post User Content that you have the rights to post, and you won’t post User Content that infringes the intellectual property rights of others (e.g. copyright infringement, trademark infringement or counterfeit), or that is otherwise unlawful, unless an exception or limitation applies under applicable law. We can take action against User Content that violates these Terms or our policies or where we are permitted or required by law, such as by removing, restricting or limiting access to, or distribution of, the content. We can also suspend or terminate accounts of users who repeatedly or seriously infringe third-party intellectual property rights, violate the law, these Terms or our policies, or where permitted or required to do so by law. We are a neutral intermediary and we do not review all User Content before or after it is published on the Service, so we are not responsible for or liable to any third party for the content or accuracy of any User Content posted by you or any other Pinterest user. For more information about how we enforce our policies or otherwise take action on content on Pinterest, see our . Where appropriate, you can appeal the decisions you think were made in error. You may have a right under local law to bring a claim for breach of contract if you believe we have breached these Terms by removing, restricting or limiting access to, or distribution of, your User Content, or suspending or terminating your account. Pinterest cannot provide you
```

## M071
**Case:** The service is provided 'as is' and to be used at your sole risk

**Passage:**

```
the detriment of the user of the Service.

**Third-Party Links**

---------------------

The Service may contain links to third-party websites and online services that are not owned or controlled by YouTube. YouTube has no control over, and assumes no responsibility for, such websites and online services. Be aware when you leave the Service; we suggest you read the terms and privacy policy of each third-party website and online service that you visit.

**About this Agreement**

========================

**Changing this Agreement**

---------------------------

We may change this Agreement in a reasonable manner, (1) to reflect changes to our Service or how we do business - for example, when we add new products or features or remove old ones, (2) for legal, regulatory, or security reasons, or (3) to prevent abuse or harm.

If we change this Agreement, we’ll provide you with at least 15 days’ advance notice before the changes take effect. When we notify you of changes, we’ll provide you with the new version of the terms and point out the material changes. If you don’t object before the changes take effect, you’ll be deemed to have accepted the changed terms. Our notice will explain this objection process. You can refuse to accept the changes, in which case the changes won’t apply to you, but we reserve the right to end our relationship with you if all other termination requirements are met.

**Continuation of this Agreement**

----------------------------------
```

## M072
**Case:** Information is provided about security practices

**Passage:**

```
2. **For Administrative Purposes.** We use personal information for various administrative purposes, such as:

1. Pursuing our legitimate interests like direct marketing, research and development (including marketing research), network and information security, and fraud prevention;

2. Detecting security incidents, protecting against malicious, deceptive, fraudulent or illegal activity, and taking appropriate actions against malicious actors;

3. Measuring interest in, and engagement with Bluesky and with Services;

4. Creating de-identified and/or aggregated information;

5. Carrying out analytics;

6. Improving, upgrading, or enhancing Bluesky and Services;

7. Developing new products and services;

8. Ensuring internal quality control and safety;

9. Sharing information with third parties as needed to provide Bluesky and Services;

10. Enforcing our agreements and policies; and

11. Carrying out activities that are required to comply with our legal obligations.

3. **For Marketing.** We may use personal information to provide you with marketing. If you have any questions about our marketing practices, you may contact us using the information provided below. You can opt-out from receiving marketing communications from us by using the unsubscribe link at the bottom of each e-mail.

4. **With Your Consent.** We may use personal information for other purposes that are clearly disclosed to you at the time you provide personal information or with your consent.
```

## M073
**Case:** Your personal data may be sold unless you opt out

**Passage:**

```
You may exercise your rights in relation to your Personal Data as outlined in this Policy, and as applicable, by submitting a ticket through your account or by emailing [support@bsky.app].

6. **NEVADA SPECIFIC DISCLOSURES**

Nevada law requires operators of online services to provide a way for Nevada residents to request to opt-out of the sale of Personal Data. Although we do not sell Personal Data, Nevada residents can still submit this type of opt-out request by contacting us using the details listed in Section 18, Contact Us.

7. **EU and UK GDPR**

This Supplemental Notice for EU/UK GDPR only applies to our processing of personal information that is subject to the EU or UK GDPR. Personal information means any information relating to an identified or identifiable individual. If you do not provide your personal information when requested, you may not be able to use our Bluesky App Services if that personal information is necessary to provide you with our Bluesky App Services or if we are legally required to collect it.

We process personal information when we have a valid legal basis, including as set forth below:

1. **Performance of a Contract:** Bluesky may need to process your personal information where required to perform our contract with you, namely the Terms of Service, and for the purposes described in Section 4(A) of this Privacy Notice.
```

## M074
**Case:** Your account can be deleted or permanently suspended without prior notice and without a reason

**Passage:**

```
You may use Pinterest only if you follow these Terms and all applicable laws. Using Pinterest may include downloading software to your computer, phone, tablet or other device. You agree that we may automatically update that software, and these Terms will apply to any updates. When you create your Pinterest account, you must provide us with accurate and complete information.

Any use of or access to Pinterest by anyone under the age of 13 is not allowed. If you are older than 13, you can use Pinterest if you are over the minimum age of consent in your country. If you are aged 13 to 18, you may only use the Service with the permission of your parent or legal guardian. Please make sure your parent or legal guardian has reviewed and discussed these Terms with you.

If we have previously disabled your account for violation of these Terms, any of our policies or for legal reasons, you will not create a new Pinterest account without our express written permission, which is provided at our sole discretion.

In using Pinterest, you agree not to scrape, collect, search, copy or otherwise access data or content from Pinterest in unauthorised ways, such as by using automated means (without our express prior permission), or access or attempt to access data you do not have permission to access.
```

## M075
**Case:** This service informs you that its Privacy Policy does not apply to third-party services

**Passage:**

```
**With other X users.** Depending on your [settings], and based on the X products and services you use, we share:

* Your interactions with X content of other users, such as replies, and people you follow.

* Content you send to a specific X user, such as through [Direct Messages]. Please keep in mind that if you’ve shared information like Direct Messages or protected posts with someone else who accesses X through a third-party service, the information may be shared with the third-party service.

**With partners.** Depending on your [settings], we also provide certain third parties with information to help us offer or operate our products and services. You can learn more about these partnerships in our [Help Center]. You can control whether X shares your personal information with these partners by using the “Data sharing with business partners” option in your [Privacy and Safety settings]. (This setting does not control sharing described elsewhere in this Privacy Policy, such as when we share information with our service providers, or through partnerships other than as described in this [Help Center] article.)

**3.2 With third parties and third-party integrations.**
```

## M076
**Case:**  Terms may be changed any time at their discretion, without notice to you 

**Passage:**

```
We may revise, add or remove any or all portions of these Terms from time to time and the most current version will always be posted on our website. Unless otherwise required by law, we will notify you of any material changes to these Terms before any update enters into effect. Your continued access to or use of Pinterest after such an update constitutes your binding acceptance of such changes. Disputes arising under these Terms will be resolved in accordance with the version of these Terms in place at the time the dispute arose. For clarity, by continuing to use Pinterest, you are agreeing to be bound by the then-current version of these Terms.

More simply put

If we're making a material change to the Terms, we'll let you know ahead of time. If you don’t agree with the new Terms, please stop using Pinterest.

### b. Assignment

If you’re a consumer in the EEA, Switzerland or the UK, either you or we may assign this agreement, and any rights and licences granted under it, to a third party. In all other cases, these Terms, and any rights and licences granted hereunder, may not be transferred or assigned by you, but may be assigned by us without restriction. Any attempted transfer or assignment in violation hereof shall be null and void.

In case of such an assignment by us, you are entitled to terminate the agreement with immediate effect by deactivating your account. We will provide you with reasonable notice of any such assignment.

### c. Entire agreement/severability
```

## M077
**Case:** Tracking pixels are used in service-to-user communication

**Passage:**

```
1. **Usage Information.** When you use Bluesky, we collect certain information automatically, including your Internet protocol (IP) address (which can be used to derive your general location), user settings, cookie identifiers, mobile carrier, other unique identifiers, browser or device information, and Internet service provider (ISP). We may also collect personal information about your use of Bluesky, including the posts you view on Bluesky, the links you click within Bluesky, and the frequency and duration of your activities.

2. **Cookies (and Other Technologies).** We and third parties that provide content or other functionality on Bluesky may use cookies, pixel tags, and other technologies (**"Tracking Technologies"**) to automatically collect information. See Section 9, Cookies, for more information.

3. **Personal Data We Collect from Other Sources**

1. **Third Parties, generally.** We may collect personal information from third parties. For example, you may direct a developer application or other third-party social networking application to share personal information with us or you may live in a jurisdiction that requires age verification and we will collect information from a third-party provider telling us whether you meet certain age requirements.
```

## M078
**Case:** Third parties are involved in operating the service

**Passage:**

```
4. **Service Providers.** We may share Personal Data with our third-party service providers and vendors. This includes service providers and vendors that provide us with IT support, hosting, payment processing, customer service, and related services.

5. **Business Partners.** We may share Personal Data with our business partners to provide you with a product or service you have requested. We may also share your personal information with business partners with whom we jointly offer products or services.

2. **Sharing to Protect Us or Others.** We may access, preserve, and disclose any information we store if we, in good faith, believe doing so is required or appropriate to: (i) comply with law enforcement, regulatory, or national security requests and legal process, like a court order or subpoena; (ii) protect your, our, or others' rights, property, or safety; (iii) enforce our policies or contracts; (iv) collect amounts owed to us; or (v) assist with an investigation or prosecution of suspected or actual illegal activity.

3. **Sharing with other Bluesky Companies.** We may share with parent or subsidiary companies to coordinate and manage our business, in accordance with the purposes set out in this Policy. These recipients will process Personal Data in the same way as set out in this Policy.
```

## M079
**Case:** No guarantee is made regarding the correction of software errors

**Passage:**

```
We do not warrant that Pinterest or any portion of the Service, or any materials or content offered through Pinterest, are accurate, complete or current, or will be uninterrupted, secure or free of errors, viruses or other harmful components.

We may make changes to Pinterest for various reasons. We will have no liability for any change to Pinterest or any suspension or termination of your access to or use of Pinterest.

The limitations, exclusions and disclaimers in this Section apply to the fullest extent permitted by applicable law.

More simply put

We work every day to improve our Service and we hope you love it. We may make changes to Pinterest from time to time and for various reasons – including adding, removing or changing features and how our Service works. But services like Pinterest aren't perfect, and you agree to use ours 'as is' without warranties.

10\. Limitation of liability

============================
```

## M080
**Case:** Many third parties are involved in operating the service

**Passage:**

```
**Cookies and similar technologies.** Like many websites, we use cookies and similar technologies to collect additional website usage data and to operate our services. Cookies are not required for many parts of our products and services such as searching and looking at public proﬁles. You can learn more about how we use cookies and similar technologies [here].

**Interactions with our content on third-party sites.** When you view our content on third-party websites that integrate X content, such as embedded timelines or post buttons, we may receive log information that includes the web page you visited.

**1.3 Information we receive from third parties.**

When you use other online products and services, they may share information about that usage with us.**
```

## M081
**Case:** You can choose with whom you share content

**Passage:**

```
**With other X users.** Depending on your [settings], and based on the X products and services you use, we share:

* Your interactions with X content of other users, such as replies, and people you follow.

* Content you send to a specific X user, such as through [Direct Messages]. Please keep in mind that if you’ve shared information like Direct Messages or protected posts with someone else who accesses X through a third-party service, the information may be shared with the third-party service.

**With partners.** Depending on your [settings], we also provide certain third parties with information to help us offer or operate our products and services. You can learn more about these partnerships in our [Help Center]. You can control whether X shares your personal information with these partners by using the “Data sharing with business partners” option in your [Privacy and Safety settings]. (This setting does not control sharing described elsewhere in this Privacy Policy, such as when we share information with our service providers, or through partnerships other than as described in this [Help Center] article.)

**3.2 With third parties and third-party integrations.**
```

## M082
**Case:** You should revisit the terms periodically, although in case of material changes, the service will notify

**Passage:**

```
the detriment of the user of the Service.

**Third-Party Links**

---------------------

The Service may contain links to third-party websites and online services that are not owned or controlled by YouTube. YouTube has no control over, and assumes no responsibility for, such websites and online services. Be aware when you leave the Service; we suggest you read the terms and privacy policy of each third-party website and online service that you visit.

**About this Agreement**

========================

**Changing this Agreement**

---------------------------

We may change this Agreement in a reasonable manner, (1) to reflect changes to our Service or how we do business - for example, when we add new products or features or remove old ones, (2) for legal, regulatory, or security reasons, or (3) to prevent abuse or harm.

If we change this Agreement, we’ll provide you with at least 15 days’ advance notice before the changes take effect. When we notify you of changes, we’ll provide you with the new version of the terms and point out the material changes. If you don’t object before the changes take effect, you’ll be deemed to have accepted the changed terms. Our notice will explain this objection process. You can refuse to accept the changes, in which case the changes won’t apply to you, but we reserve the right to end our relationship with you if all other termination requirements are met.

**Continuation of this Agreement**

----------------------------------
```

## M083
**Case:** This service is only available for use individually and non-commercially

**Passage:**

```
7. misuse any reporting, flagging, complaint, dispute, or appeals process, including by making groundless, vexatious, or frivolous submissions;

8. run contests on or through the Service that do not comply with [YouTube’s contest policies and guidelines];

9. use the Service to view or listen to Content other than for personal, non-commercial use (for example, you may not publicly screen videos or stream music from the Service); or

10. use the Service to: (a) sell any advertising, sponsorships, or promotions placed on, around, or within the Service or Content, other than those allowed in the [Advertising on YouTube] policies (such as compliant product placements); or (b) sell advertising, sponsorships, or promotions on any page of any website or application that only contains Content from the Service or where Content from the Service is the primary basis for such sales (for example, selling ads on a webpage where YouTube videos are the only content of value).

**Reservation**

---------------

Any right not expressly granted to you in this Agreement remains the right of YouTube or the respective rights holders. This means, for example, that using the Service does not give you ownership of any intellectual property rights in the Content you access (including any branding used on or displayed in the Service).

**Develop, Improve and Update the Service**

-------------------------------------------
```

## M084
**Case:** You can opt out of targeted advertising

**Passage:**

```
2. **For Administrative Purposes.** We use personal information for various administrative purposes, such as:

1. Pursuing our legitimate interests like direct marketing, research and development (including marketing research), network and information security, and fraud prevention;

2. Detecting security incidents, protecting against malicious, deceptive, fraudulent or illegal activity, and taking appropriate actions against malicious actors;

3. Measuring interest in, and engagement with Bluesky and with Services;

4. Creating de-identified and/or aggregated information;

5. Carrying out analytics;

6. Improving, upgrading, or enhancing Bluesky and Services;

7. Developing new products and services;

8. Ensuring internal quality control and safety;

9. Sharing information with third parties as needed to provide Bluesky and Services;

10. Enforcing our agreements and policies; and

11. Carrying out activities that are required to comply with our legal obligations.

3. **For Marketing.** We may use personal information to provide you with marketing. If you have any questions about our marketing practices, you may contact us using the information provided below. You can opt-out from receiving marketing communications from us by using the unsubscribe link at the bottom of each e-mail.

4. **With Your Consent.** We may use personal information for other purposes that are clearly disclosed to you at the time you provide personal information or with your consent.
```

## M085
**Case:** Your personal data is used to employ targeted third-party advertising

**Passage:**

```
1. **No Targeted Advertising Sales.** We do not sell or share Personal Data for the purpose of displaying advertisements that are selected based on Personal Data from your activities on or use of Bluesky ("**Targeted Advertising**").

2. **Sensitive information.** We may disclose sensitive information for a business purpose like those described below, we do not sell or share sensitive information for the purpose of Targeted Advertising.

The following Personal Data elements we, or our service providers, collect may be classified as "sensitive" under certain privacy laws ("**Sensitive Information**") including:

1. username and password;

2. birthday;

3. telephone number;

4. government identifiers (like driver's license numbers);

5. payment information; and

6. confirmation that a user is 18 years old or older.

We use this sensitive information for the purposes described in Section 10, How We Use Personal Data, to the extent necessary to operate Bluesky and our Services, to enter into and perform on a contract with you, to comply with legal and regulatory requirements, to protect the safety of our users and third parties, or as otherwise permissible for our own internal purposes consistent with applicable laws.
```

## M086
**Case:** The terms may be changed at any time, but you will receive notification of the changes

**Passage:**

```
===================================

If you are a consumer in the EEA, Switzerland or the UK, these Terms and your use of the Service shall be governed by the law of the country where you live, and any claim, dispute, or controversy arising from or in connection with or relating to these Terms, Pinterest, or the Service shall be resolved in the courts of the country where you live.

In all other cases, these Terms and your use of the Service shall be governed by the laws of the State of California, without respect to its conflict of laws principles. For any actions not subject to Section 11 (Arbitration), the exclusive place of jurisdiction for any claim, dispute or controversy arising from or in connection with these Terms or the Service is San Francisco County, California, or the United States District Court for the Northern District of California, and such disputes will be determined under California law.

More simply put

The Bay Area is beautiful at this time of year. In fact, it doesn't matter what time of year it is, that's what's so great! Let’s resolve any disputes in California. If you are a consumer in the EEA, Switzerland or the UK, however, you can file disputes in your home courts.

13\. General terms

==================

### a. Notification procedures and changes to these Terms
```

## M087
**Case:** You can opt out of targeted advertising

**Passage:**

```
1. **No Targeted Advertising Sales.** We do not sell or share Personal Data for the purpose of displaying advertisements that are selected based on Personal Data from your activities on or use of Bluesky ("**Targeted Advertising**").

2. **Sensitive information.** We may disclose sensitive information for a business purpose like those described below, we do not sell or share sensitive information for the purpose of Targeted Advertising.

The following Personal Data elements we, or our service providers, collect may be classified as "sensitive" under certain privacy laws ("**Sensitive Information**") including:

1. username and password;

2. birthday;

3. telephone number;

4. government identifiers (like driver's license numbers);

5. payment information; and

6. confirmation that a user is 18 years old or older.

We use this sensitive information for the purposes described in Section 10, How We Use Personal Data, to the extent necessary to operate Bluesky and our Services, to enter into and perform on a contract with you, to comply with legal and regulatory requirements, to protect the safety of our users and third parties, or as otherwise permissible for our own internal purposes consistent with applicable laws.
```

## M088
**Case:** You can retrieve an archive of your data

**Passage:**

```
1. **Request Access to and Portability of Your Personal Information,** including: (i) obtaining access to or a copy of your personal information; and (ii) receiving an electronic copy of personal information that you have provided to us, or asking us to send that information to another company in a structured, commonly used, and machine-readable format (also known as the "right of data portability");

2. **Request Correction** of your personal information where it is inaccurate, incomplete, or outdated. We may provide self-service tools for you to update your personal information;

3. **Request Deletion, Anonymization or Blocking** of personal information including when processing is based on your consent, or when processing is unnecessary, excessive or noncompliant (also known as the "right to be forgotten").

4. **Request to Opt-Out of Certain Processing Activities** if we engage in certain data processing activities that give you a right of opt-out under applicable privacy laws;

5. **Request Restriction of or Object to** our processing of your personal information;

6. **Withdraw your Consent** to our processing of your personal information. Please note that your withdrawal will only take effect for future processing and will not affect the lawfulness of processing before the withdrawal;

7. **Be Informed** about third parties with which your personal information has been shared; and
```

## M089
**Case:** The court of law governing the terms is in a jurisdiction that is less friendly to user privacy protection

**Passage:**

```
If your use of the Service ends, the following terms of this Agreement will continue to apply to you: “Other Legal Terms”, “About This Agreement”, and the licenses granted by you will continue in limited cases as described under “Duration of License”.

**Severance**

-------------

If it turns out that a particular term of this Agreement is not enforceable for any reason, this will not affect any other terms.

**Assignment**

--------------

YouTube may transfer all or part of this Agreement to an Affiliate or, if YouTube is sold, to a third party.

**No Waiver**

-------------

If you do not comply with this Agreement and we do not take action immediately, this doesn’t mean that we are giving up any rights that we may have (such as the right to take action in the future).

**Governing Law**

-----------------

If you are based in Germany, this Agreement, and your relationship with YouTube under this Agreement, will be governed by the laws of Germany under the exclusion of the CISG, and legal proceedings may be brought in your local courts that have jurisdiction according to the statutory rules. This choice of law does not make any statement with regard to the law applicable to the respective Service itself.

**EEA instructions on withdrawal**

If you’re an EEA-based consumer, then starting on May 28, 2022, EEA consumer law gives you the right to withdraw from this contract as described in the EU’s Model Instructions on Withdrawal, provided below:

Right of withdrawal
```

## M090
**Case:** You may be tracked on other websites

**Passage:**

```
We use cookies and other Tracking Technologies to collect certain information automatically. Tracking Technologies allow a website to recognize your device and can serve several purposes: to ensure that the website takes the user’s preferences into account by storing language preferences, to collect statistical data and adapt the content. Tracking Technologies can help provide you with a good experience when you browse websites and also help improve website functionality.

1. **Strictly Necessary Cookies.** Some cookies are strictly necessary to make our Bluesky App Services available to you. We cannot provide you with our Bluesky App Services without this type of cookie.

2. **Analytical or Performance Cookies.** We may also use cookies for website analytics purposes in order to operate, maintain and improve our Bluesky App Services. We may use our own analytics cookies or use third-party analytics providers.

You can block cookies by setting your internet browser to block some or all cookies. However, if you use your browser settings to block all cookies (including strictly necessary cookies) you may not be able to access all or parts of the Sites and the Bluesky App. You can change your browser settings to block or notify you when you receive a cookie, delete cookies or browse our Sites using your browser’s anonymous usage setting.
```

## M091
**Case:** This service gives your personal data to third parties involved in its operation

**Passage:**

```
**With service providers.** We may share your information with our [service providers] that perform functions and provide services on our behalf, including payment services providers who facilitate payments; service providers that host our various blogs and wikis; service providers that help us understand the use of our services; applicant tracking system providers to send and receive applicant and job data to potential employers; service providers supporting age assurance solutions; and those that provide fraud detection services.

**With advertisers.** Advertising revenue enables us to provide our products and services. Advertisers may learn information from your engagement with their ads on or off X. For example, if you click on an external link or ad on our services, that advertiser or website operator might figure out that you came from X, along with other information associated with the ad you clicked, such as characteristics of the audience it was intended to reach and other X-generated identifiers for that ad. They may also collect other personal information from you, such as cookie identifiers, or your IP address.
```

## M092
**Case:** Information is provided about security practices

**Passage:**

```
1. **Obtain confirmation that we process your personal information.** In response to this request, we will inform you whether we process your personal information or not. Please note that, if you are a user, we necessarily process your personal information.

2. **Obtain information about the possibility of not providing your consent and the respective consequences.** When consent is used as a legal basis for the processing of your personal information, you have the right to be informed about the possibility of not providing consent and the consequences of refusal.

16\. Security

-------------

We make reasonable efforts to protect your information by using physical and electronic safeguards designed to improve the security of the information we maintain. However, as our Services are hosted electronically, we can make no guarantees as to the security or privacy of your information.

17\. Children's Personal Information

------------------------------------

The Bluesky App Services are not directed to children under 13 (or other age as required by local law outside of the United States). We do not knowingly collect personal information from children.

If you are a parent or guardian and believe your child has uploaded personal information to our site without your consent, you may contact us using the information provided below.

18\. Contact Us

---------------

If you have any questions about this Privacy Policy, please contact us at [support@bsky.app].
```

## M093
**Case:** The service will only respond to government requests that are reasonable

**Passage:**

```
3. **Deidentified information.** We may receive or process Personal Data to create deidentified information that can no longer reasonably be used to infer information about, or otherwise be linked to, a particular individual or household. Where we maintain deidentified information, we will maintain and use it in deidentified form and will not try to reidentify the information except as required or permitted by applicable law.

4. **Appeals.** If you are a resident of certain U.S. States, you have the right to appeal decisions regarding your privacy requests. All appeal requests should be submitted using the contact details found in Section 18, Contact Us. If your appeal is denied, you may contact your local Attorney General.

5. **CALIFORNIA SPECIFIC DISCLOSURES** The following disclosures only apply to California residents:

1. **Personal Data collection.** California law requires that we provide disclosures to you about what Personal Data we collect by reference to the categories of Personal Data set forth within California law. To address this obligation, we have identified the relevant California Personal Data category for the Personal Data set out in Section 8, Personal Data we Collect:

1. **Identifiers** like your name, address, phone number, email address, passport or other government identity information including driver's licence information, account information, or other similar identifiers.
```

## M094
**Case:** Other rules, terms, conditions and/or guidelines may apply

**Passage:**

```
If you want to use Pinterest for commercial purposes, you must create a business account and agree to our . If you do open an account for a company, organisation or other entity, "you" includes you and that entity, and you represent and warrant that you are authorised to grant all permissions and licences provided in these Terms and bind the entity to these Terms, and that you agree to these Terms on the entity's behalf. To the extent that any provisions in the conflict with these Terms, the shall govern to the extent of the conflict.

If you post content on Pinterest that is sponsored or branded – such as when a business partner pays or incentivises you to post it – or is in any way commercial in nature, you are subject to our .

More simply put

These Terms are an agreement between you and us. You cannot use Pinterest if you're under 13 (or older in some countries). If you use Pinterest for commercial purposes, you need to set up a business account. If you post commercial, sponsored or branded content, you need to comply with our Commercial and Branded Content Guidelines. We grant you a revocable licence to use Pinterest, which is subject to our Terms and policies as outlined immediately above. Unless we have agreed otherwise, if your account has been suspended, you can’t return to Pinterest.

3\. Your User Content

=====================

### a. Posting User Content
```

## M095
**Case:** You may be tracked on other websites

**Passage:**

```
Please keep us informed if your Personal Data changes at any point during your relationship with us so we can keep our records accurate and current. Update your Personal Data in the App or on the Site.

4\. Applicability of this Policy

--------------------------------

This Policy is separate from our [Terms of Service] and our [Community Guidelines], that also govern your use of Bluesky.

5\. Third-party Services

------------------------

Bluesky and the Services may include links to third-party websites, plug-ins, applications, services, products, and technology (“**Third-party Services**”). Clicking on links to and using Third-party Services may allow third parties to collect or share your Personal Data. We are not responsible for the content, security or privacy practices of those Third-party Services and this Policy does not apply to your use of Third-party Services. You should consider the privacy and cookie policies / notices of those third parties to find out how your Personal Data may be used.

6\. If you do not want to provide Personal Data

-----------------------------------------------
```

## M096
**Case:** Many third parties are involved in operating the service

**Passage:**

```
X has carefully considered the legal reasons it is permitted to collect, use, share and otherwise process your information. If you want to dig in to learn more and better understand the nuances, we’d encourage you to check out [this additional information about data processing]. And no, we don’t sell your personal information.

**6.2 We move your data to make X work for you.**

Just as you use X to seamlessly participate in global conversations with people in countries all over the world, X must move information across borders and to different countries around the world to support the safe and reliable service you depend on. For example, if you live in Europe and are having a conversation with someone in the United States, information has to move between those countries to provide that experience – it’s what you expect from us.

We also use data centers and cloud providers, and engage [our affiliates] and third-party partners and [service providers] located in many parts of the world to help us provide our services. Before we move data between countries we look at the risks that may be presented to the data and rely on [standard contractual clauses] (SCCs), where applicable, to ensure your data rights are protected. To request a copy of the SCCs, please contact us [here]. If data will be shared with a third party, we require them to maintain the same protections over your data that we provide directly.
```

## M097
**Case:** You can choose with whom you share content

**Passage:**

```
5. **Other Purposes.** We also use your personal information for other purposes as requested by you, as permitted by applicable law, or where we reasonably consider that we need to use it for another reason and that reason is compatible with the original purpose.

6. **Legal Bases for Processing.** For explanations of our legal bases for processing in jurisdictions where this disclosure is required, see Section 15, Supplemental Notice for Certain Jurisdictions, below.

11\. How We Share your Personal Data

------------------------------------

1. **Sharing to Provide Bluesky and Services**

1. **Your Posts and Public Profile.** Bluesky is a decentralized microblogging service where most user activity is public by design. This includes your posts, profile, likes, following, and blocks.

2. **Other Users You Share or Interact With.** Bluesky may allow you to share personal information, messages, or interact with other users.

3. **Third-party Services You Share or Interact With.** Bluesky may link to or allow you to interface, interact, share information with, direct us to share information with, access and/or use Third-party Services. If you do, the information you share will be subject to any Third-Party Service's privacy policy. For example, if you request that we share your personal information with a developer application or payment processor, we may facilitate the request.
```

## M098
**Case:**  You are being tracked via social media cookies/pixels

**Passage:**

```
2. **Customer Records** like your driver's licence number, passport number, partial debit card information, partial credit card information, bank account information or other payment or financial information.

3. **Protected Classification Characteristics** like age, date of birth, and gender.

4. **Commercial Information** like information about products or services purchased and your use of our Services.

5. **Biometric Information** which is described above and which is collected only by third-party providers to the extent necessary to conduct age or identity verification. We do not collect, receive, possess, or have access to this data.

6. **Internet / Network Information** like device information, and log data.

7. **Sensory Information** like pictures and videos (content) you upload.

8. **Professional / Employment Information** like the business or organisation you are associated with and, where applicable, your title with that business or organisation and information relating to your role with the business or organisation.

9. **Other Personal Data** like communication preferences, customer service and communication history, personal data an individual permits us to see when interacting with us through social media, Personal Data an individual provides us in relation to a question or request, and messages you send us through our Services or make available to us on social media.

10. **Inferences** like information generated from your use of our Services.
```

## M099
**Case:** You are prohibited from publishing any third party’s personally identifiable information without their consent

**Passage:**

```
1. access, reproduce, download, distribute, transmit, broadcast, display, sell, license, alter, modify or otherwise use any part of the Service or any Content except: (a) as specifically permitted by the Service; (b) with prior written permission from YouTube and, if applicable, the respective rights holders; or (c) as permitted by applicable law;

2. circumvent, disable, fraudulently engage, or otherwise interfere with the Service (or attempt to do any of these things), including security-related features or features that: (a) prevent or restrict the copying or other use of Content; or (b) limit the use of the Service or Content;

3. access the Service using any automated means (such as robots, botnets or scrapers) except: (a) in the case of public search engines, in accordance with YouTube’s robots.txt file; (b) with YouTube’s prior written permission; or (c) as permitted by applicable law;

4. collect or use any information that might identify a person (for example, harvesting usernames or faces), unless permitted by that person or allowed under section 3 above;

5. use the Service to distribute unsolicited promotional or commercial content or other unwanted or mass solicitations (spam);

6. cause or encourage any inaccurate measurements of genuine user engagement with the Service, including by paying people or providing them with incentives to increase a video’s views, likes, or dislikes, or to increase a channel’s subscribers, or otherwise manipulate metrics;
```

## M100
**Case:** You have a reduced time period to take legal action against the service

**Passage:**

```
If your use of the Service ends, the following terms of this Agreement will continue to apply to you: “Other Legal Terms”, “About This Agreement”, and the licenses granted by you will continue in limited cases as described under “Duration of License”.

**Severance**

-------------

If it turns out that a particular term of this Agreement is not enforceable for any reason, this will not affect any other terms.

**Assignment**

--------------

YouTube may transfer all or part of this Agreement to an Affiliate or, if YouTube is sold, to a third party.

**No Waiver**

-------------

If you do not comply with this Agreement and we do not take action immediately, this doesn’t mean that we are giving up any rights that we may have (such as the right to take action in the future).

**Governing Law**

-----------------

If you are based in Germany, this Agreement, and your relationship with YouTube under this Agreement, will be governed by the laws of Germany under the exclusion of the CISG, and legal proceedings may be brought in your local courts that have jurisdiction according to the statutory rules. This choice of law does not make any statement with regard to the law applicable to the respective Service itself.

**EEA instructions on withdrawal**

If you’re an EEA-based consumer, then starting on May 28, 2022, EEA consumer law gives you the right to withdraw from this contract as described in the EU’s Model Instructions on Withdrawal, provided below:

Right of withdrawal
```

## M101
**Case:** Your account may be suspended and/or terminated for breaching the Terms of Service

**Passage:**

```
-----------------------

You may stop using the Service at any time. You can also [delete the Service] from your Google Account, which involves closing your YouTube channel and removing your data, with the option to download a copy of your data first.

**Terminations and Suspensions by YouTube**

-------------------------------------------

YouTube reserves the right to suspend or terminate your Google account or your access to all or part of the Service if: (a) you materially or repeatedly breach this Agreement; (b) we are required to do so to comply with a legal requirement or a court order; or (c) there are objective and concrete reasons to believe there has been conduct that creates liability or harm to any user, other third party, YouTube or our Affiliates.

**Notice for Termination or Suspension**

----------------------------------------

We will notify you with the reason for termination or suspension by YouTube, and where such action is taken for cause, we will give you the opportunity to remedy or stop the stated behaviour, unless there are objective and concrete reasons to believe that to do so: (a) would violate the law or the direction of a legal enforcement authority; (b) would compromise an investigation or (c) would substantially compromise the integrity, operation or security of the Service; or (d) would cause substantial harm to any user, other third party, YouTube or our Affiliates.

**Effect of Account Suspension or Termination**
```

## M102
**Case:** Promises will be kept after a merger or acquisition

**Passage:**

```
4. **Sharing to obtain Professional Services.** We may share Personal Data with our legal advisors, bankers, auditors, accountants, consultants, and insurers. Our professional advisors will process Personal Data as necessary to provide their services to us.

5. **Sharing in the Event of Merger, Sale, or Other Asset Transfers.** If we are involved in a merger, acquisition, financing, reorganization, bankruptcy, receivership, purchase or sale of assets, transition of service to another provider, or other similar corporate transaction, your personal information may be processed as part of such a transaction.

12\. International data transfers

---------------------------------

We may transfer, process, and store all personal information we collect anywhere in the world. Different countries have different data protection laws.

If we transfer personal information from the European Economic Area, Switzerland, Brazil and/or the United Kingdom to a country that does not provide an adequate level of protection under applicable data protection laws, we will do so (i) using appropriate safeguards; (ii) based on safeguards like the European Commission-approved, UK Government-approved, or Brazil’s Data Protection Authority Standard Contractual Clauses or Addenda; or (iii) otherwise in accordance with applicable data protection laws.

For more information about the safeguards we use for international transfers of your personal information, please contact us as set forth below.
```

## M103
**Case:** Many third parties are involved in operating the service

**Passage:**

```
We may disclose all of these categories of Personal Data for a business purpose to service providers or other third parties, as outlined in this Policy.

2. **Disclosure of Personal Data.** As detailed in Section 11, How We Share your Personal Data, we may disclose the categories of Personal Data identified above to the following categories of third parties for various business purposes: other Bluesky companies, service providers, our professional advisers, business partners, other businesses as needed to provide our Services, and certain third parties where you have provided consent, where it is in connection with a corporate transaction, or where we are required by law or in connection with other legal process.

3. **Sources of Personal Data.** We collect Personal Data from you, from your browser or device when you interact with our Services, from our business partners and affiliates, from third parties you direct to share information with us, and from other third-party providers. For more information, see Section 13, Your Privacy Choices and Rights.

4. **Purpose for collection.** We collect Personal Data about you for the purposes described in Section 10, How We Use Personal Data.

5. **Notice of financial incentives.** We do not sell Personal Data collected about you, or share Personal Data collected about you for cross-context behavioural advertising. We do not currently send emails for direct marketing purposes.
```

## M104
**Case:** This service gives your personal data to third parties involved in its operation

**Passage:**

```
**With other X users.** Depending on your [settings], and based on the X products and services you use, we share:

* Your interactions with X content of other users, such as replies, and people you follow.

* Content you send to a specific X user, such as through [Direct Messages]. Please keep in mind that if you’ve shared information like Direct Messages or protected posts with someone else who accesses X through a third-party service, the information may be shared with the third-party service.

**With partners.** Depending on your [settings], we also provide certain third parties with information to help us offer or operate our products and services. You can learn more about these partnerships in our [Help Center]. You can control whether X shares your personal information with these partners by using the “Data sharing with business partners” option in your [Privacy and Safety settings]. (This setting does not control sharing described elsewhere in this Privacy Policy, such as when we share information with our service providers, or through partnerships other than as described in this [Help Center] article.)

**3.2 With third parties and third-party integrations.**
```

## M105
**Case:** The court of law governing the terms is in a jurisdiction that is friendlier to user privacy protection

**Passage:**

```
If your use of the Service ends, the following terms of this Agreement will continue to apply to you: “Other Legal Terms”, “About This Agreement”, and the licenses granted by you will continue in limited cases as described under “Duration of License”.

**Severance**

-------------

If it turns out that a particular term of this Agreement is not enforceable for any reason, this will not affect any other terms.

**Assignment**

--------------

YouTube may transfer all or part of this Agreement to an Affiliate or, if YouTube is sold, to a third party.

**No Waiver**

-------------

If you do not comply with this Agreement and we do not take action immediately, this doesn’t mean that we are giving up any rights that we may have (such as the right to take action in the future).

**Governing Law**

-----------------

If you are based in Germany, this Agreement, and your relationship with YouTube under this Agreement, will be governed by the laws of Germany under the exclusion of the CISG, and legal proceedings may be brought in your local courts that have jurisdiction according to the statutory rules. This choice of law does not make any statement with regard to the law applicable to the respective Service itself.

**EEA instructions on withdrawal**

If you’re an EEA-based consumer, then starting on May 28, 2022, EEA consumer law gives you the right to withdraw from this contract as described in the EU’s Model Instructions on Withdrawal, provided below:

Right of withdrawal
```

## M106
**Case:** Your content can be licensed to third parties

**Passage:**

```
1. access, reproduce, download, distribute, transmit, broadcast, display, sell, license, alter, modify or otherwise use any part of the Service or any Content except: (a) as specifically permitted by the Service; (b) with prior written permission from YouTube and, if applicable, the respective rights holders; or (c) as permitted by applicable law;

2. circumvent, disable, fraudulently engage, or otherwise interfere with the Service (or attempt to do any of these things), including security-related features or features that: (a) prevent or restrict the copying or other use of Content; or (b) limit the use of the Service or Content;

3. access the Service using any automated means (such as robots, botnets or scrapers) except: (a) in the case of public search engines, in accordance with YouTube’s robots.txt file; (b) with YouTube’s prior written permission; or (c) as permitted by applicable law;

4. collect or use any information that might identify a person (for example, harvesting usernames or faces), unless permitted by that person or allowed under section 3 above;

5. use the Service to distribute unsolicited promotional or commercial content or other unwanted or mass solicitations (spam);

6. cause or encourage any inaccurate measurements of genuine user engagement with the Service, including by paying people or providing them with incentives to increase a video’s views, likes, or dislikes, or to increase a channel’s subscribers, or otherwise manipulate metrics;
```

## M107
**Case:** Your personal information may be collected, regardless of whether you interacted directly with the service or not

**Passage:**

```
We may disclose all of these categories of Personal Data for a business purpose to service providers or other third parties, as outlined in this Policy.

2. **Disclosure of Personal Data.** As detailed in Section 11, How We Share your Personal Data, we may disclose the categories of Personal Data identified above to the following categories of third parties for various business purposes: other Bluesky companies, service providers, our professional advisers, business partners, other businesses as needed to provide our Services, and certain third parties where you have provided consent, where it is in connection with a corporate transaction, or where we are required by law or in connection with other legal process.

3. **Sources of Personal Data.** We collect Personal Data from you, from your browser or device when you interact with our Services, from our business partners and affiliates, from third parties you direct to share information with us, and from other third-party providers. For more information, see Section 13, Your Privacy Choices and Rights.

4. **Purpose for collection.** We collect Personal Data about you for the purposes described in Section 10, How We Use Personal Data.

5. **Notice of financial incentives.** We do not sell Personal Data collected about you, or share Personal Data collected about you for cross-context behavioural advertising. We do not currently send emails for direct marketing purposes.
```

