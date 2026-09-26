"""Rebuild the disclosed, RoleLens candidate profile fixture.

This file is the committed source of the profiles. Running it writes
profiles.json next to the script. No network, model API, or personal data.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROVENANCE = "generated with GPT-6 Codex on 2026-09-26"
LICENSE = "CC0-1.0; authored for this project"


def profile(profile_id: str, cohort: str, tags: list[str], cv: str) -> dict:
    return {
        "id": profile_id,
        "cohort": cohort,
        "variation_tags": tags,
        "synthetic": True,
        "provenance": PROVENANCE,
        "license": LICENSE,
        "cv_text": cv.strip(),
    }


PROFILES = [
    profile("RL-P01", "normal", ["fintech", "early_career", "product_analytics"], """
Candidate RL-P01 | Associate Product Manager

Experience: At a regional payments app (2023-2026), I worked on merchant onboarding and the help flow used by small retailers. I interviewed 14 support agents and eight merchants, mapped points where applicants abandoned identity checks, and wrote stories for a two-sprint redesign. The team recorded a lower abandonment rate after release, although marketing changes in the same quarter mean I cannot attribute the full change to my work. I owned the event taxonomy and reviewed the dashboard weekly with operations.

Earlier, as a business analyst at a local software studio, I prepared SQL extracts for fraud-operations reports and checked discrepancies with analysts. I did not design the fraud model. My exposure to language models is a small internal experiment that grouped support tickets; I compared 50 samples by hand and recommended keeping a human reviewer for escalation cases. I can explain the test and its limits, but it was never deployed.

Education and working style: BSc in information systems. Comfortable with SQL, spreadsheet analysis, interview notes, Figma wireframes, and writing acceptance criteria. I prefer to show actual user quotes alongside funnel numbers when deciding what to build.
"""),
    profile("RL-P02", "normal", ["B2B_SaaS", "workflow", "stakeholder_management"], """
Candidate RL-P02 | Product Owner

Experience: I spent four years at a B2B procurement software provider, beginning in customer success and moving into product ownership. My current area is approvals for finance teams with different regional policies. I gathered examples of rejected requests, translated them into decision tables, and worked with engineering on audit-log behaviour. A pilot with six customers reduced repeated support requests, but we have not isolated which part of the release made the difference.

For the last year I have also maintained a search feature for contract records. I partnered with a data engineer to inspect retrieval misses and wrote clearer empty-state copy. The search service uses vendor embeddings; I understand the input and output flow and can prioritise problems from customer evidence, but I did not choose the model or tune its index. I have facilitated trade-off meetings where legal staff wanted complete traceability and sales wanted fewer clicks.

Education and tools: BA in economics, product analytics certificate, SQL at a working level, Jira, Figma, and basic Python scripts for cleaning exports. I am looking for an AI product role where I can build deeper evaluation skills.
"""),
    profile("RL-P03", "normal", ["retail", "experimentation", "junior"], """
Candidate RL-P03 | Digital Product Analyst

Experience: At a grocery marketplace, I supported the team responsible for search and category browsing. I planned an A/B test of a new substitution notice, checked sample-ratio balance with the analyst, and reported both conversion and cancellation effects. The result was mixed: browsing conversion improved for returning customers while first-time customer complaints rose. I recommended another iteration instead of a broad rollout and documented the decision in a one-page memo.

I also ran monthly calls with shoppers who used assistive technologies. Their feedback changed the placement of product-size information and led to a separate accessibility defect queue. A vendor demonstrated an image tagging model for catalogue data. I assembled a small error review with 80 images and found mistakes on package variants; the pilot stopped before production. My role was product discovery and review, not model development.

Education and tools: BBA with a statistics minor. I use SQL, Looker, survey tools, Figma, and spreadsheets. I have written simple Python notebooks to reconcile experiment counts, but I would need help designing a robust machine-learning deployment plan.
"""),
    profile("RL-P04", "normal", ["healthcare", "safety", "service_design"], """
Candidate RL-P04 | Service Product Specialist

Experience: I work for an outpatient scheduling platform, where clinics struggle with late cancellations and confusing preparation instructions. I observed reception teams, mapped patient journeys, and redesigned reminder wording with nurses and an accessibility reviewer. In a three-clinic pilot, fewer patients called to clarify preparation, but clinic staffing changed during the same period; I report this as a directional signal only. I kept a log of exceptions rather than removing difficult cases from the analysis.

In 2025, I explored whether an assistant could answer routine scheduling questions from approved clinic content. I specified a rule that anything involving symptoms or treatment should route to staff, then manually reviewed 40 example answers for unsupported advice. The vendor built the prototype; I wrote the scope, reviewed failures, and stopped it from being presented as a medical adviser. I am familiar with approval workflows and consent requirements, though I have no production AI launch.

Education and tools: Public-health degree, service design training, interview facilitation, spreadsheets, and basic SQL. I am interested in products where safe escalation is treated as part of the user experience.
"""),
    profile("RL-P05", "normal", ["media", "content", "personalization"], """
Candidate RL-P05 | Content Platform PM

2022-present, home-page discovery team at a streaming company:
- Coordinated editors, design, and engineering so curated collections could be updated without a weekly engineering ticket. Editorial turnaround improved after release; audience effects differed by genre and never became a clean single-number win.
- Wrote a measurement plan separating impressions, starts, and completed viewing. In a recommendation review, gathered examples of repetitive suggestions and specified a feedback control. Data scientists owned the ranking tests and model changes.
- Tested an internal programme-note summary tool. Editors still checked names and distribution rights before anything could be published. Several confident-looking errors in early drafts shaped the review checklist.

2019-2022, editorial tools coordinator: Planned migration of archive tags, collected complaints about missing titles, and helped support teams explain changes to editors. This was workflow ownership rather than algorithm work.

Education and tools: BA in media studies with later statistics coursework. SQL for product reporting, dashboards, Figma, and requirement documents. Comfortable mediating between creative teams and engineers; less experienced with model deployment and infrastructure decisions. I am most useful when a good-looking engagement metric hides a poor viewing experience.
"""),
    profile("RL-P06", "normal", ["education", "learning_product", "qualitative_research"], """
Candidate RL-P06 | Learning Product Manager

Experience: I manage practice exercises for an adult-language learning app. Learner interviews revealed that people wanted feedback on specific mistakes, rather than a generic score. I worked with teachers to create an error taxonomy and with engineers to show a short explanation after each exercise. In a limited rollout, learners attempted more corrections; retention did not change clearly over the observation window. I presented both findings to the leadership team.

The company later trialled automatic feedback on written responses. I selected a set of responses from different proficiency levels and compared model comments with teacher comments, looking for fabricated grammar rules and discouraging language. I proposed a teacher-review queue for low-confidence cases. I did not own the model selection, and the trial was not released to all learners. My strongest skills are designing the learning flow, aligning educators, and turning observations into prioritised product changes.

Education and tools: MA in applied linguistics, short course in product analytics, working SQL, Figma, and survey analysis. I am learning Python and have used it to sample anonymised practice responses for manual review.
"""),
    profile("RL-P07", "normal", ["logistics", "operations", "roadmapping"], """
Candidate RL-P07 | Operations Platform PM

Experience: At a last-mile delivery company, I lead a small product area covering dispatcher screens and driver incident reporting. Dispatchers previously copied route exceptions between three tools. I spent shifts at two depots, logged repeated handoffs, and proposed a shared queue with explicit ownership. After rollout the median time to assign an exception fell, though volume and staffing differed from the baseline month. I provided the raw definition of the metric in my release review.

I worked with an optimisation team on delivery estimates. My role was to define which errors mattered to customers and which needed manual override. I compared predicted and actual arrival windows by route type; I did not build the prediction service. A proposed chatbot for drivers was postponed because offline access and multilingual instructions were more urgent. I am comfortable explaining that priority decision to stakeholders who expected an AI feature.

Education and tools: Industrial engineering degree, seven years across operations and product roles. I use SQL, mapping dashboards, issue trackers, and process diagrams. I have led cross-functional planning but have limited direct experience with foundation-model evaluation.
"""),
    profile("RL-P08", "normal", ["developer_tools", "technical_PM", "API"], """
Candidate RL-P08 | Developer Experience Product Manager

Current scope: API onboarding for a cloud-monitoring startup. The first-alert journey was taking new developers too many steps. After watching setup sessions, I reordered documentation examples, specified clearer authentication errors, and asked the team to publish a working sample repository. Failed setup attempts fell in our instrumentation. I checked support tickets as a counterweight because the dashboard alone could miss people who abandoned setup early.

Earlier role: Solutions engineer. Wrote Python examples for REST integrations and investigated customer issues using application logs. I still discuss rate limits, latency, and reliability directly with engineers, although the engineering lead owns architecture choices.

Side project at work: Compared lexical documentation search with an embedding service on 60 queries and wrote relevance notes, including stale-example failures. Another team implemented the search service. This gave me practical evaluation experience, not ownership of model training or production guardrails.

Tools and education: Computer-science degree; Python, SQL, Git, API documentation, customer interviews, and release notes. I prefer a working demo tested against concrete developer tasks to a feature list. Commercial pricing and enterprise procurement have been outside my remit so far.
"""),
    profile("RL-P09", "normal", ["insurance", "regulated", "risk_controls"], """
Candidate RL-P09 | Digital Claims Product Analyst

Experience: I support claims intake for a general insurer. Adjusters showed me where policyholders misunderstood document requests, and I rewrote the upload flow with legal and operations review. I defined a checklist for missing evidence, tested it with 12 adjusters, and tracked repeat-contact rates after release. The rate moved in the expected direction, but seasonal claim mix limits any strong causal claim.

I have helped evaluate document extraction supplied by a vendor. I collected cases where tables, handwriting, or multiple claimants produced unreliable fields and asked the team to keep a visible correction step. I reviewed error examples and designed the correction interface; the data-science group selected the model. I have also attended privacy and retention reviews, where I learned to ask which fields are necessary before collecting them. I would not describe myself as an AI engineer.

Education and tools: Degree in business analytics, four years in insurance operations and product. I use SQL, spreadsheet models, wireframes, and structured user testing. My next step is to gain hands-on experience with evaluation of language-model outputs while retaining a strong human review path.
"""),
    profile("RL-P10", "normal", ["public_service", "accessibility", "service_delivery"], """
Candidate RL-P10 | Digital Services Product Lead

Experience: I helped a municipal services team simplify an online permit renewal process. I observed counter staff, read anonymised enquiry themes, and tested two content structures with residents. The chosen version reduced incomplete submissions in one district; differences in local outreach mean I would not generalise the exact percentage to every district. I wrote service-level acceptance criteria and kept a public change log for policy updates.

The team explored an assistant for explaining permit rules. I gathered approved source pages and defined a requirement to show the source and date for every answer. During testing, several answers combined rules from different permit classes. I recommended limiting the assistant to navigation until that failure was addressed. Procurement and security colleagues handled vendor assessment; I handled user tasks and content quality. I am used to policy ambiguity and to documenting when the service should hand someone to a person.

Education and tools: Master of public administration, six years in digital service delivery. I work with analytics dashboards, service blueprints, plain-language content, accessibility checks, and basic SQL. I want to apply these habits to AI features with clear accountability.
"""),
    profile("RL-P11", "normal", ["advertising", "measurement", "stakeholder_management"], """
Candidate RL-P11 | Advertising Product Associate

Experience: At a commerce advertising platform, I support the team that helps small sellers understand campaign performance. Interviews with sellers showed that the dashboard used agency terminology they did not recognise. I rewrote the reporting labels, drafted examples for common decisions, and worked with an analyst to define consistent attribution windows. The new report was used more often in the pilot group, but I cannot claim it improved return on ad spend; budgets shifted during the test.

I coordinated an experiment on suggested campaign descriptions. The creative team wrote the review criteria, and I collected cases in which the generated copy implied discounts that did not exist. We kept the feature in an opt-in internal tool while the review process matured. I did not build the model, and I would not describe that trial as an autonomous campaign optimiser. My day-to-day work includes backlog refinement, stakeholder updates, customer calls, and checking data definitions before release.

Education and tools: Marketing and statistics degree. I use SQL, spreadsheets, Figma, campaign reporting tools, and simple Python for CSV quality checks. I care about separating attractive dashboards from decisions sellers can actually make.
"""),
    profile("RL-P12", "normal", ["hardware", "connected_device", "field_research"], """
Candidate RL-P12 | Connected Device Product Manager

Experience: I have managed software features for a home-energy monitor for three years. Customers complained that alerts arrived after they had already changed appliance use. I visited installation partners, analysed event timestamps, and proposed a shorter alert path plus clearer explanations of uncertainty. Engineers improved device buffering while I changed notification rules. Alerts arrived sooner in lab and field checks, although we do not yet know whether households saved more energy.

Before product management I was a test engineer and wrote scripts to replay device messages. That background helps me discuss sensor failures, battery constraints, and release rollback plans. I took part in a forecast feature review, comparing model outputs with actual meter readings for different home types. A specialist team trained the forecast model; I defined the customer-facing interval and made sure the interface did not display a false precision. I have not worked with language-model retrieval.

Education and tools: Electrical engineering degree, six years in hardware and software teams. I use Python, SQL, prototype dashboards, field notes, and structured release checklists. I often choose reliability fixes ahead of a new feature when home conditions vary from a demo.
"""),
    profile("RL-P13", "normal", ["travel", "marketplace", "customer_research"], """
Candidate RL-P13 | Marketplace Product Manager

Experience: At a travel booking marketplace, I look after the post-booking experience for guests and hosts. I reviewed support conversations to understand why check-in instructions failed and spoke with hosts in three regions. The team redesigned where access details appear and added a reminder for hosts to verify them. Contact volume per booking declined in the trial, but travel mix changed between the comparison periods. I recorded that caveat in the launch note.

I evaluated a vendor translation feature for host messages. Native-language reviewers found polite but incorrect references to local transport and access codes. I prioritised a human correction path and blocked automatic sending for time-critical instructions. The implementation team owned the model integration. My contribution was deciding which communications were safe to automate and which needed confirmation. I have also written marketplace rules for dispute escalation and worked with trust staff when a simple conversion target conflicted with guest safety.

Education and tools: BA in international business; four years in product roles. I use SQL, product analytics, interview guides, Figma, and multilingual content review. I would like to build stronger technical depth in AI evaluation and retrieval.
"""),
    profile("RL-P14", "normal", ["HR_tech", "workflow", "fairness"], """
Candidate RL-P14 | People Systems Product Specialist

Experience: I work on internal mobility tools at an enterprise software firm. Employees previously had to search several pages to find eligibility rules for open roles. I mapped the content with human-resources partners, redesigned filters, and ran task-based usability sessions. People found policy information faster in the sessions; I have no evidence yet that internal hiring improved. I maintained the rule owner and review date for each page to prevent stale guidance.

The team investigated whether skill suggestions could help employees explore roles. I set up a workshop with employees from non-traditional career paths and found that job titles were a poor proxy for experience. I wrote requirements for editable skill evidence and a way to challenge suggestions. A data-science team built a prototype; I reviewed examples of false positives and missing experience. It has not been used for hiring decisions. I understand the fairness concerns from this work but have not run a formal bias audit.

Education and tools: Psychology degree and five years in HR operations and product. I use interviews, SQL extracts, survey analysis, and prototyping tools. I prefer employee-controlled recommendations over opaque scoring.
"""),
    profile("RL-P15", "normal", ["gaming", "community", "moderation"], """
Candidate RL-P15 | Community Product Manager

Experience: At a multiplayer game studio, I own parts of the player-reporting flow and moderator console. I observed moderators working through busy weekend queues and redesigned the evidence summary so they could see context before acting. In a six-week pilot, median review time fell, while overturn rates remained similar. I checked a sample of decisions because speed alone would have been a poor measure of success.

I partnered with a safety engineer on a classifier that routed obvious spam reports to a separate queue. My role was defining routing thresholds, escalation rules, and feedback from moderators. I did not train the classifier. The team left harassment complaints under human review, particularly when slang or friendship groups changed the meaning of a message. I have written policy-facing explanations for players and coordinated with localisation specialists across regions. An early generative reply draft was withdrawn after it suggested actions moderators were not authorised to take.

Education and tools: Sociology degree, community operations background, four years in product. I use event analytics, SQL, user interviews, Figma, and incident reviews. I am comfortable defending a slower workflow when it protects appeal rights.
"""),
    profile("RL-P16", "normal", ["manufacturing", "industrial_analytics", "technical_PM"], """
Candidate RL-P16 | Factory Software Product Owner

Experience: I oversee a manufacturer’s maintenance scheduling interface used by technicians on older tablets. I shadowed night-shift crews and found that work orders often lacked asset history. I worked with engineers to surface recent repairs and with planners to simplify priority rules. In the first plant, repeat visits per work order declined, but a parts-supply change happened at the same time. We are testing the workflow in another plant before making a broader claim.

I previously worked as a process engineer and can interpret sensor readings, maintenance records, and safety procedures. A predictive-maintenance vendor showed anomaly scores to technicians; I ran feedback sessions and learned that the scores needed context before anyone trusted them. I proposed showing the measurements and inspection steps behind an alert. The vendor owned its model, and I did not validate accuracy across all machine types. I have managed release windows around production shutdowns and documented rollback decisions.

Education and tools: Mechanical engineering degree, seven years in industrial operations. I use Python for data cleanup, SQL, process diagrams, and field observation. My product choices usually start with the technician’s next safe action.
"""),
    profile("RL-P17", "normal", ["accessibility", "consumer_app", "inclusive_design"], """
Candidate RL-P17 | Accessibility Product Designer moving into PM

Experience: I spent four years designing account and messaging experiences at a social app. Screen-reader users told us that message previews repeated sender names and hid attachment type. I tested revised flows with a paid accessibility panel, wrote detailed interaction notes, and worked with engineers through release. Task completion improved in moderated testing, but we did not measure long-term messaging behaviour. I also helped set up an issue triage process so accessibility defects were not treated as optional polish.

During the last year I became the product owner for voice-message controls. I balanced requests from users, privacy reviewers, and the infrastructure team, and I wrote a decision memo for transcript retention. A speech-to-text service created draft captions; I sampled errors for accents and background noise and required users to review text before sharing. I have led discovery and prioritisation for this area, though I have less experience with revenue metrics and budget planning.

Education and tools: Interaction-design degree, accessibility certification, Figma, interview research, analytics dashboards, and basic SQL. I am seeking an AI PM role focused on inclusive user experiences rather than model research.
"""),
    profile("RL-P18", "normal", ["sustainability", "data_product", "decision_support"], """
Candidate RL-P18 | Climate Data Product Manager

Experience: I work at a carbon-accounting software company serving mid-sized manufacturers. Customers struggled to trace estimates back to invoices and energy bills. I mapped the calculation workflow, prioritised source links and revision history, and worked with auditors on the export format. A customer panel reported greater confidence in the revised reports, but I have no verified evidence that reporting time decreased. I am cautious about repeating that claim in sales materials.

The team tested an assistant that explained unusual changes in emission estimates. I wrote scenarios based on actual user questions, identified cases where missing data should trigger a question rather than an answer, and manually reviewed 70 drafts for unsupported explanations. Engineers built the retrieval and model call. I specified that the product must show underlying figures and document dates before presenting a narrative. Earlier roles in analytics taught me to check units and denominators before discussing trends.

Education and tools: Environmental science degree, postgraduate data-analytics module, five years in B2B software. I use SQL, spreadsheets, user interviews, issue trackers, and Python for basic data checks. I can turn technical uncertainty into an understandable product choice.
"""),
    profile("RL-P19", "normal", ["customer_support", "knowledge_base", "AI_pilot"], """
Candidate RL-P19 | Support Tools PM

Experience: I moved from support operations into product at a subscription-software company. Agents spent time opening several internal guides before replying to billing questions, so I measured lookup steps, cleaned up duplicated content with policy owners, and redesigned the search screen. In a small pilot, agents resolved common questions faster. We did not include complex refund disputes in that measurement, and I have kept them separate in reporting.

I led product discovery for an answer-drafting assistant. I defined a policy-source allowlist, wrote test questions from anonymised tickets, and asked reviewers to flag unsupported commitments. The prototype could draft helpful first sentences but sometimes ignored account-specific exceptions. I recommended keeping it as a staff-only draft with visible source passages. The engineering team integrated the language model; I did not train it. I am strongest at workflow observation, content governance, and bringing support agents into release decisions.

Education and tools: Business degree, three years in support and two in product. I use SQL, help-desk analytics, Figma, spreadsheets, and documentation systems. I am learning more about retrieval evaluation and cost per response.
"""),
    profile("RL-P20", "normal", ["banking", "onboarding", "compliance"], """
Candidate RL-P20 | Banking Onboarding PM

Experience: I manage a digital account-opening journey at a community bank. Applicants were confused when document checks paused without explanation. I interviewed branch advisers and customers, then introduced clearer status messages and a save-and-return path. Completion rose in the controlled rollout, while customer-service calls about verification fell. I worked with analytics to check that the improvement was not limited to one device type.

I coordinate compliance, security, design, and engineering reviews for changes to identity checks. A document-classification supplier proposed automating a manual routing step. I asked for an error breakdown by document type and for a clear human appeal path before the trial. A small test showed that some valid overseas documents were rejected more often; we did not release automated routing. My role was product risk and customer journey design, not vendor model training. I can make a trade-off document that includes both operational cost and customer harm.

Education and tools: Finance degree, six years in banking digital products. I use SQL, analytics dashboards, process maps, and usability testing. I want to learn more about model monitoring while keeping regulated decisions reviewable.
"""),
    profile("RL-P21", "hard", ["synonyms", "strong_evidence", "few_taxonomy_terms"], """
Candidate RL-P21 | Service Improvement Lead

Recent work: I look after the questions people ask while setting up accounts at a business-software cooperative. The old help journey sent the same question to three different teams. I listened to call recordings, collected examples where written guidance disagreed with the product, and made a single review queue with named owners. The team now resolves a greater share of routine questions in one contact, according to weekly service reports.

We also tried a writing assistant that assembled draft answers from reviewed help pages. I drew up 65 examples of the awkward questions, marked which ones required a person to decide, and compared drafts with the exact policy page available at the time. When the tool combined two policies, I asked engineers to show the passage it used and to pause instead of guessing. I did not choose the underlying provider. My role was deciding what the service should say and proving when it should stay silent.

Before this I coordinated accessibility fixes for an online learning service. I have a humanities degree, some spreadsheet and database-query experience, and no formal product-manager title. Colleagues describe me as patient in workshops and strict about the wording that reaches customers.
"""),
    profile("RL-P22", "hard", ["keyword_stuffing", "weak_evidence", "false_positive"], """
Candidate RL-P22 | Business Development Coordinator

Summary: Interested in AI product management, generative AI, agents, RAG, prompt engineering, responsible AI, machine learning, A/B testing, SQL, Python, strategy, roadmaps, OKRs, and stakeholder management. These topics are listed in the online courses I have watched and in the role descriptions I am using to plan my next move. I want to be transparent that the list is an interest inventory, not a list of delivered projects.

Work history: For two years I have booked demonstrations for a office-software reseller. I maintain contact records, prepare slides for account executives, and collect customer questions after sales calls. Last year I suggested a new demo order based on common objections; the sales manager approved it, but I did not measure a before-and-after outcome. I do not own a software backlog or meet with engineers. An AI sales-assistant vendor showed us a prototype. I attended the session but did not evaluate the model.

Education: Business diploma and several short online AI courses with quizzes. I can use spreadsheets and presentation software. I have not yet written SQL or Python outside guided lessons and would need support to run an experiment or design a product requirement.
"""),
    profile("RL-P23", "hard", ["adjacent_domain", "technical_depth", "no_product_ownership"], """
Candidate RL-P23 | Applied Machine Learning Engineer

Experience: I have built forecasting and classification services for a transport analytics vendor. My team deployed a demand forecast used by planners and monitored performance by city and season. I owned feature checks, offline evaluation, a Python inference service, and alerts for missing upstream data. When the model worsened after a schedule change, I traced the issue to stale route codes and coordinated a rollback. I can explain precision, recall, calibration, and latency with examples from that work.

Product exposure: A product manager supplied the user problem, success definition, and roadmap. I joined two planner interviews to explain model limitations and suggested displaying uncertainty bands, but I did not decide which segment to serve or whether the feature should ship. I have not priced a product, negotiated scope with customers, or led usability tests. I am interested in moving closer to product decisions because some technically accurate features were barely used.

Education and tools: MSc in computer science, five years of engineering work, Python, SQL, model-serving tools, and experiment tracking. I have strong model implementation evidence and limited evidence of discovery, commercial judgement, or ownership of a cross-functional product release.
"""),
    profile("RL-P24", "hard", ["career_switch", "research_to_product", "partial_transfer"], """
Candidate RL-P24 | Education Researcher seeking Product Role

Research history: I spent six years studying how adults learn technical skills at a research institute. I designed interview protocols, recruited participants, analysed transcripts, and published reports for programme managers. In one study I combined surveys with course-completion records and found that shorter practice sessions correlated with higher completion. We did not randomise assignment, so I cautioned against claiming the shorter sessions caused the result.

Practical projects: I volunteered with a small nonprofit to redesign an application form for learners. I observed five users, sketched alternatives, and tested the revised wording. The nonprofit adopted part of the proposal, but I was not involved in its software implementation or later metrics. I also took a semester course on language models and built a local notebook that compared answers to a handful of education-policy questions. It was a class exercise, not a deployed service.

I want to move into AI product work because I enjoy translating research into decisions. I can bring careful evidence gathering and communication, but I have not managed engineers, a product budget, or a live feature. Tools include qualitative coding software, R, spreadsheets, and basic Python.
"""),
    profile("RL-P25", "hard", ["ambiguous_metrics", "ownership_unclear", "marketing_transfer"], """
Candidate RL-P25 | Growth Project Lead

Profile: I have supported launches for a consumer finance app and often present myself as a product-minded growth lead. During a referral campaign, sign-ups increased by 32 percent. I built the weekly report and suggested one change to the invitation copy; several teams also altered incentives, paid-media spend, and landing pages. I do not have an estimate of what my copy change contributed. I was not responsible for the product backlog, although I attended some planning meetings.

My strongest work is interviewing prospective customers about why they hesitate to finish registration. I coded 25 interviews and shared three themes with designers, who changed a disclosure screen. I did not observe the later user test. I have used a text generator to prepare first drafts of survey questions, which a researcher reviewed. I have not built or evaluated an AI feature for customers. My slides mention conversion optimisation, segmentation, personalisation, and experimentation, but those terms refer to campaign operations rather than controlled product tests.

Education and tools: Communications degree, four years in growth roles, spreadsheet reporting, CRM systems, and dashboard reading. I can write clearly and work across teams; I would need coaching to own technical delivery and rigorous causal measurement.
"""),
    profile("RL-P26", "hard", ["negation", "skills_claim_boundary", "not_deployed"], """
Candidate RL-P26 | Junior Product Coordinator

Experience: At an accounting software provider I coordinate release notes, collect support tickets, and arrange user interviews for the product manager. I have written acceptance criteria for two small settings changes after watching the PM do earlier examples. I did not set priorities for the wider roadmap. A cross-team project reduced the number of billing questions, but my work was limited to updating help copy and checking that links worked; I do not claim ownership of the outcome.

My university project proposed a retrieval-based assistant for invoice terminology. I assembled a small set of public definitions and manually compared 20 generated answers to the source text. It was a classroom prototype. It was never used by customers, had no privacy review, and was not monitored after the demo. I have not built an agent, trained a model, or managed a live AI release. I have watched tutorials on these topics and want to learn them properly.

Education and tools: Business information systems degree. I am comfortable in Figma and spreadsheets. I can read a basic SQL query but have not written one for production analysis. I value clear task notes and asking for review when a claim exceeds my evidence.
"""),
    profile("RL-P27", "hard", ["keyword_stuffing", "certificate_only", "false_positive"], """
Candidate RL-P27 | Operations Administrator

Selected training: My certificates cover artificial intelligence, product strategy, foundation models, retrieval augmented generation, prompt engineering, cloud architecture, SQL, Python, experimentation, fairness, privacy, and digital transformation. The provider awarded completion badges after video lessons and multiple-choice quizzes. I have listed their topic names here so a recruiter can see what I have studied; none of the badges required building a working product.

Employment: I organise supplier forms and meeting schedules for a facilities company. I noticed that staff copied the same vendor information into multiple spreadsheets and proposed one shared template. Operations adopted it in my team, saving some manual re-entry, though we did not time the work formally. I sometimes write instructions for colleagues and check whether a new form is understandable. There are no software engineers in my team, and I have not owned an application release.

Next step: I am applying for entry-level technology roles and have begun practising spreadsheet formulas. I can describe what a language model does at a high level, but I could not yet assess its output quality, write a query unaided, or explain model deployment trade-offs from experience. My interests are broad; my delivered evidence is narrower.
"""),
    profile("RL-P28", "hard", ["research_depth", "limited_business_context", "no_release"], """
Candidate RL-P28 | Natural Language Processing Research Assistant

Research work: At a university lab, I studied whether paraphrased instructions changed a model's answers to technical questions. I assembled an evaluation set, wrote Python scripts to compare outputs, and analysed disagreement with another reviewer. A conference workshop accepted our short paper. The experiment used public documents and offline calls; it did not involve a customer interface or a production service. I can discuss sampling, annotation disagreement, and reproducibility in detail.

I helped a community group test a prototype search page for its handbook. I observed four volunteers trying to find rules and reported where document titles misled them. Another volunteer built the page, and I did not prioritise fixes after the test. I enjoy investigating why a system fails, but my work has mostly been bounded research questions rather than choosing a market, maintaining a roadmap, or balancing revenue and support costs.

Education and tools: MSc in computational linguistics, Python, Git, notebooks, and statistical analysis. I have read product case studies and can write technical explanations for non-specialists. I would need experience with discovery, stakeholder negotiation, and shipping constraints before independently owning an AI product.
"""),
    profile("RL-P29", "hard", ["senior_adjacent", "vague_outcomes", "management_vs_hands_on"], """
Candidate RL-P29 | Digital Transformation Director

Career summary: I have led large change programmes at a national retail chain for more than a decade. My teams introduced new inventory reporting, redesigned store training, and negotiated contracts with software providers. A corporate presentation attributes a substantial efficiency gain to the programme, but the number combines several operational initiatives and I cannot isolate software effects. I managed budgets and executive reviews, while specialist teams made day-to-day product and technical choices.

For an AI exploration last year, I sponsored demonstrations of a demand-planning assistant. I asked store managers for concerns, authorised a limited proof of concept, and decided against rollout when its explanations were difficult to verify. I was not involved in prompt design, data labelling, or failure analysis. I can articulate investment criteria, governance, and organisational adoption, but my direct experience with early-stage user testing and implementation detail is limited.

Education and tools: MBA, operations leadership background, executive dashboards, financial planning, and vendor management. My resume uses terms such as roadmap, AI strategy, and platform transformation because those were programme topics. A hands-on associate product role would require me to rebuild habits around individual user interviews, specifications, and iteration.
"""),
    profile("RL-P30", "hard", ["title_mismatch", "prototype_only", "thin_validation"], """
Candidate RL-P30 | AI Product Manager (internship title)

Experience: I held a ten-week AI Product Manager internship at a startup that sells note-taking software. My main assignment was to prepare a demonstration of automatic meeting summaries for investor conversations. I wrote sample prompts, selected three favourable transcripts, and made slides comparing draft styles. The demo ran successfully in meetings. It was not available to customers, and no systematic error review was performed; I do not know how it would behave with noisy audio or sensitive meetings.

I also assisted a product manager by taking notes in two customer calls and writing one user story for an export button. The PM decided priorities and engineers implemented the change after I left. At university I helped organise a student hackathon and built a clickable prototype for a study planner. There were no measured users or production outcomes for that prototype. I am enthusiastic about AI interfaces but my experience is short and concentrated in presentation work.

Education and tools: BSc in information systems, graduating recently. I have used Figma, spreadsheets, basic Python, and public model playgrounds. I have not owned a live AI feature, a retrieval system, evaluation data, or a cost plan. I am looking for a junior role with close mentoring.
"""),
]


def main() -> None:
    output = Path(__file__).with_name("profiles.json")
    ids = [item["id"] for item in PROFILES]
    assert len(PROFILES) == 30 and len(set(ids)) == 30
    assert [p["cohort"] for p in PROFILES].count("normal") == 20
    assert [p["cohort"] for p in PROFILES].count("hard") == 10
    seen_texts: set[str] = set()
    for item in PROFILES:
        words = re.findall(r"\b[\w'-]+\b", item["cv_text"])
        assert 150 <= len(words) <= 300, (item["id"], len(words))
        fingerprint = hashlib.sha256(item["cv_text"].encode("utf-8")).hexdigest()
        assert fingerprint not in seen_texts, item["id"]
        seen_texts.add(fingerprint)
        item["word_count"] = len(words)
        item["sha256_cv_text"] = fingerprint
    output.write_text(json.dumps(PROFILES, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {len(PROFILES)} profiles to {output}")
    print(f"Word counts: min={min(p['word_count'] for p in PROFILES)}, max={max(p['word_count'] for p in PROFILES)}")


if __name__ == "__main__":
    main()
