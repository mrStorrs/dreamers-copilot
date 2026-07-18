# Rules Pruned V2

Date created: 2026-07-03

Input reviewed: `rules-pruned-v1.md`, 130 pruned rules derived from `inital-rule-research.md` rows 1-1124.

Prune rule applied: **One Concept Rule** - if two rules enforce the same core idea, keep the broader one.

Result: 103 surviving rules. This pass removed 27 v1 rules by merging child concepts into broader parent rules. No source rows were discarded; merged source rows stay attached to the surviving rule.

Review adjustment: after agent review, eight draft merges were restored because they crossed into domain demotion rather than same-concept pruning, and five missed one-concept merges were accepted.

## Removed By This Pass

| Removed V1 Rule | Broader Survivor | Reason |
|---:|---:|---|
| 4 | 14 | Speculative behavior is the child case of designing only for current or likely change. |
| 12 | 11 | DRY is an abstraction rule: unify knowledge only when the abstraction reduces complexity. |
| 20 | 21 | Valid construction is one way to enforce durable invariants. |
| 28 | 23 | External, generated, client, AI, and config data are examples of boundary data that must be distrusted and validated. |
| 34 | 33 | Context binding is part of using cryptographic and proof objects correctly. |
| 38 | 37 | Retention, deletion, archives, and recovery are data lifecycle policy. |
| 41 | 39 | Bounded correlation is part of privacy-safe telemetry. |
| 43 | 42 | Actionable alerting is a child of user-visible health and SLO-driven reliability. |
| 48 | 45 | Backpressure and concurrency limits are resource bounds across async paths. |
| 52 | 122 | Persisting user intent is part of preserving user work across failure and lifecycle changes. |
| 56 | 55 | Read-modify-write safety is data integrity under concurrent mutation. |
| 59 | 58 | Forward-only migration history is part of production-grade migration and backfill work. |
| 60 | 98 | Backup restore drills are a child case of independent, tested recovery paths. |
| 68 | 67 | Backward compatibility is contract evolution. |
| 69 | 67 | Stable output and additive input tolerance are contract evolution details. |
| 72 | 71 | Assertion discipline is part of explicit error handling and invariant restoration. |
| 77 | 74 | Regression tests are a required kind of behavior test for breakage-prone behavior. |
| 83 | 82 | Pinned toolchains and inputs are a mechanism for reproducible builds. |
| 90 | 89 | License and clearance obligations are part of governing reused material as shipped code. |
| 93 | 92 | Rollback and kill switches are recovery controls for reversible rollout. |
| 94 | 95 | Runtime controls are configuration-like behavior controls that need reviewed lifecycle policy. |
| 106 | 103 | Incremental refactoring is a child of small, conceptually separate, protected changes. |
| 109 | 108 | Executable examples and migration guides are documentation quality requirements. |
| 111 | 105 | Requirement-risk-test-release evidence is traceability from decision to verification. |
| 115 | 116 | Client-side authority mistakes are browser/client security-boundary mistakes. |
| 121 | 45 | Hot-path resource behavior is bounded resource use in performance-critical form. |
| 124 | 23 | Trusted instruction separation is part of treating model context and boundary data as untrusted. |

## Surviving Rules

| # | Surviving Rule | V1 Rule(s) | Research Rows |
|---:|---|---|---|
| 1 | Make the code correct for real users. | 1 | 2, 17, 64, 224-226, 430-434 |
| 2 | Optimize for maintainability over time. | 2 | 1, 18, 62-63, 65, 493-500 |
| 3 | Keep code structurally simple and locally understandable. | 3 | 3, 26, 50, 134, 137, 206-215, 471, 989-993 |
| 4 | Prefer clear idioms and boring technology over cleverness. | 5 | 6, 50, 214, 470, 990, 1002 |
| 5 | Choose precise names that reveal intent. | 6 | 5, 121, 993 |
| 6 | Automate style and follow the local style. | 7 | 7, 147, 215 |
| 7 | Use principles as judgment tools, not rituals. | 8 | 51, 75, 393, 398, 401, 501, 1053 |
| 8 | Give each module one coherent responsibility. | 9 | 67, 73-74, 213, 398 |
| 9 | Hide volatile decisions behind stable boundaries. | 10 | 24, 65-72 |
| 10 | Use abstractions only when they remove more complexity than they add. | 11, 12 | 22-23, 70, 149, 394-397, 399 |
| 11 | Keep coupling explicit, minimal, and directional. | 13 | 20, 68, 72, 417, 721-722 |
| 12 | Design for current needs and likely change; make every flexibility point justify its cost. | 4, 14 | 4, 58-60, 69, 402, 469 |
| 13 | Use proven components and standard protocols when they meet security, compatibility, licensing, and maintenance needs. | 15 | 61, 79, 129, 766 |
| 14 | Make code easy to delete. | 16 | 469, 500, 991 |
| 15 | Never rely on undefined, undocumented, or unspecified behavior. | 17 | 217, 435, 438 |
| 16 | Let the language and type system carry real meaning. | 18 | 216, 218-222, 669-676 |
| 17 | Treat escapes from language and runtime safety as audited contract boundaries. | 19 | 140, 164, 436-438, 847-856, 982-988 |
| 18 | Enforce durable invariants as early as construction, types, contracts, or constraints allow. | 20, 21 | 32, 83, 221, 253, 262-264, 589-595, 741, 1003 |
| 19 | Model absence, failure, and state explicitly. | 22 | 150, 185, 218-220, 447, 568, 671-673 |
| 20 | Treat boundary data, model context, and configuration as untrusted; validate it against explicit contracts and keep trusted instructions separate. | 23, 28, 124 | 11, 122, 139, 241, 353, 385, 456, 552-558, 629-635, 970, 1036, 1050-1051, 1097 |
| 21 | Parse, canonicalize, authorize, then use the exact object you checked. | 24 | 321-324, 632, 1006-1009, 1099 |
| 22 | Reject ambiguous input instead of choosing a convenient interpretation. | 25 | 631, 637, 790, 984, 1101 |
| 23 | Never concatenate untrusted text into interpreter surfaces. | 26 | 13, 328-329, 535-536, 641, 965, 1100 |
| 24 | Encode or sanitize output for the exact destination context. | 27 | 12, 388 |
| 25 | Authorize every action, object, request, and service boundary. | 29 | 341-345, 533, 541, 749-752 |
| 26 | Scope credentials, roles, tokens, and privileges narrowly. | 30 | 14, 104-105, 346-350, 750, 756-759 |
| 27 | Model identity, recovery, and abuse-sensitive workflows as explicit security flows. | 31 | 114, 351-352, 539, 745-748, 751, 858-869, 1038-1044 |
| 28 | Give every secret a lifecycle and keep secrets out of code, logs, and artifacts. | 32 | 21, 33, 119, 304-306, 387, 538, 756-757, 893, 1001 |
| 29 | Use vetted cryptography and bind tokens, ciphertexts, challenges, and proofs to their intended context. | 33, 34 | 299-311, 537, 753-755, 1037-1045 |
| 30 | Treat privileged capabilities, including outbound fetches, as brokered access. | 35 | 223, 360, 534, 542, 677, 881-897, 1072-1073, 1098, 1103 |
| 31 | Secure by design, secure by default, and fail closed. | 36 | 15-17, 141, 190, 223-226, 431-432, 739-744 |
| 32 | Collect, process, retain, and delete data only under specific lifecycle policy. | 37, 38 | 88-89, 120, 260, 384, 502-516, 725-735, 765, 951, 1054-1058, 1077 |
| 33 | Make telemetry privacy-safe, low-cardinality, and sufficient to correlate events without over-identifying users. | 39, 41 | 33-34, 119, 159, 193-196, 376-383, 599-606, 1025 |
| 34 | Log structured events and preserve accountability evidence. | 40 | 133, 350, 378, 572, 731, 767, 949-959 |
| 35 | Measure user-visible health, set SLOs for reliability tradeoffs, and alert only on owned, actionable user impact. | 42, 43 | 160, 192, 197-198, 418-422, 604, 607 |
| 36 | Design for partial failure, overload, and recovery. | 44 | 36, 161-168, 191, 235, 406, 417, 428-429 |
| 37 | Bound resource use, concurrency, and hot-path work explicitly. | 45, 48, 121 | 96, 135-136, 167-170, 403-404, 540, 561, 736-738, 761, 812-821, 825-827, 902-912, 937-948, 1021-1022, 1124 |
| 38 | Propagate deadlines and cancellation through the real work. | 46 | 76, 166, 204, 233-234, 578, 967, 1005, 1104-1105 |
| 39 | Retry only when it is bounded, backed off, jittered, idempotent, and within budget. | 47 | 77-78, 232-239, 407, 489, 653-660 |
| 40 | Make shared-fate dependencies visible and limit them with failure domains. | 49 | 317-320, 417, 721-722, 880, 1112 |
| 41 | Treat external systems, networks, clocks, and delivery as unreliable. | 50 | 236, 573-581, 740, 807-808, 870-879, 1111 |
| 42 | Treat caches as derived state with explicit keys, freshness, invalidation, and privacy rules. | 51 | 247, 392, 413, 661, 781-789, 996, 1108-1110 |
| 43 | Scope distributed-system guarantees exactly and enforce them with named primitives. | 53 | 237-240, 653-660, 807, 928, 1019-1026, 1123 |
| 44 | Give every mutation a stable operation identity. | 54 | 78, 232, 239, 489, 877 |
| 45 | Preserve data integrity under transactions, constraints, and concurrent mutation. | 55, 56 | 83-85, 97-100, 129, 253-256, 564-566, 570-571, 589-598, 662, 979-981, 1006-1013, 1083-1088 |
| 46 | Use durable intent logs for cross-system side effects. | 57 | 132, 239-240, 520, 567, 569, 654 |
| 47 | Run migrations, backfills, restores, and destructive data jobs as production workloads; evolve applied history forward with compatibility gates. | 58, 59 | 125, 256, 261, 516-518, 775, 803, 840-844, 925-936, 1083-1090 |
| 48 | Treat derived and pipeline state as rebuildable from sources, replayable where needed, and freshness-bounded. | 61 | 595, 661, 704, 709, 808-810, 925-927 |
| 49 | Treat time, money, units, text, locale, and coordinates as domain data. | 62 | 82, 115-118, 130-131, 284-288, 332-340, 522-532, 562-563, 914-924 |
| 50 | Make numeric precision, rounding, overflow, and tolerance explicit. | 63 | 284-286, 333-335, 642-648, 941-943, 1069 |
| 51 | Own randomness, stochastic behavior, and determinism deliberately. | 64 | 649-652, 940 |
| 52 | Parse data with real parsers and serialize data, not executable object graphs. | 65 | 123, 128, 165, 629-641, 844-846, 1097 |
| 53 | Treat every public and automation-facing surface as a contract. | 66 | 19, 31, 79-80, 123-127, 175-179, 241, 483-492, 710-718, 777, 960-969, 1080-1082, 1091 |
| 54 | Version public contracts, preserve compatibility, and define how unknown future fields are handled. | 67, 68, 69 | 19, 80, 128, 179, 289-298, 486-488, 491, 634, 717, 840-845, 888, 913, 1046, 1119 |
| 55 | Make every failure diagnosable without leaking internals. | 70 | 81, 127, 391, 443-455, 718, 1091-1092 |
| 56 | Handle errors explicitly, restore invariants, and reserve assertions for impossible internal states. | 71, 72 | 27, 138, 150-154, 185-189, 264, 441-452 |
| 57 | Release resources on every exit path and check cleanup that can fail. | 73 | 154, 171-172, 822, 1004 |
| 58 | Put automated and regression tests around behavior you cannot afford to break. | 74, 77 | 8, 39-41, 44, 47-48, 145, 473, 1015 |
| 59 | Keep tests fast, deterministic, hermetic, and actionable. | 75 | 9-10, 41-42, 145, 246, 479 |
| 60 | Test public behavior and contracts, not private implementation details. | 76 | 43, 472, 477-478, 831, 835 |
| 61 | Test edge cases, interactions, failure modes, and negative paths. | 78 | 45-46, 480-482, 637-639, 752, 831-839, 977 |
| 62 | Match advanced verification techniques to risk. | 79 | 46, 265-266, 474-476, 481, 831-838, 1015-1017 |
| 63 | Treat test code, test data, and test oracles as production-quality assets. | 80 | 45, 48, 839 |
| 64 | Use coverage and metrics as risk signals, not goals. | 81 | 49, 148, 208-209, 476, 683 |
| 65 | Make builds reproducible from explicit, hermetic, pinned inputs. | 82, 83 | 35, 52-55, 91-93, 102-108, 242-250, 365-373, 543-548, 995-1000, 1065-1070, 1102 |
| 66 | Generated code and asset pipelines need one source of truth and freshness gates. | 84 | 249, 842, 1121 |
| 67 | Treat CI, release, edge, and workflow pipelines as production code. | 85 | 101, 199, 251-252, 548-550, 776, 791, 1048-1049, 1059 |
| 68 | Keep main green with high-signal automated checks. | 86 | 37-38, 52, 55, 140, 142, 146, 244-245, 267-268, 439-440, 1018, 1095 |
| 69 | Protect the release path with review, ownership, and least privilege. | 87 | 92, 101, 104-107, 252, 271, 550 |
| 70 | Ship immutable, signed, provenance-tracked artifacts. | 88 | 90, 106, 250, 281, 371, 546-547, 857, 890-892, 1060, 1113 |
| 71 | Treat dependencies, snippets, generated output, AI suggestions, and other reused material as governed shipped code, including license clearance. | 89, 90 | 35, 227-231, 277-283, 353-359, 619-628 |
| 72 | Govern dependencies for update, execution, and abandonment risk. | 91 | 274-276, 365-375, 1061-1064 |
| 73 | Deploy small, automated, reversible changes with recovery controls. | 92, 93 | 199-203, 312-320, 551, 613-618, 857, 860, 888, 1049, 1060, 1114-1116 |
| 74 | Treat configuration and runtime controls as reviewed, versioned, validated, observable code with owners and cleanup paths. | 94, 95 | 21, 163, 201-202, 313, 608-618, 968-971, 1048 |
| 75 | Keep environments similar where behavior depends on the environment. | 96 | 161, 609, 713 |
| 76 | Make processes disposable and shutdown graceful. | 97 | 162, 204, 872-873 |
| 77 | Keep recovery paths independent and prove them with tested restores and incident response. | 60, 98 | 257-259, 318, 423-427, 513-521, 721-724, 880, 978 |
| 78 | Make operational scope, privilege, and blast radius explicit. | 99 | 314-315, 677, 719-720, 778-780, 973-976, 1096 |
| 79 | Put dangerous operations behind preview, confirmation, and machine-checkable preconditions. | 100 | 315, 778-780, 1086, 1090 |
| 80 | Manage declarative operational state as reviewed, versioned code. | 101 | 684-691, 972-976 |
| 81 | Treat the observability pipeline as production infrastructure. | 102 | 205, 418, 605-607, 975 |
| 82 | Keep changes and refactors small, conceptually separate, and behaviorally protected. | 103, 106 | 25, 29, 56-57, 206, 270, 275, 678 |
| 83 | Use code review for shared understanding and automate mechanical feedback. | 104 | 142-144, 206-207, 267, 680-683, 994 |
| 84 | Preserve traceability, ownership, and release evidence from decision to verification. | 105, 111 | 269, 271-273, 430, 493, 679, 744, 955-959, 1096 |
| 85 | Give accepted technical debt an owner, reason, and closure path. | 107 | 63, 493-500 |
| 86 | Keep documentation, examples, and migration guidance accurate, task-oriented, and executable. | 108, 109 | 28, 155-184, 663-668, 715, 1093-1094 |
| 87 | Record consequential decisions and tradeoffs with context. | 110 | 69, 157, 668 |
| 88 | Treat accessibility and user recovery as correctness requirements. | 112 | 86-87, 109-114, 389-390, 582-588, 773-774, 1027 |
| 89 | Publish files and external file content through safe, durable protocols. | 113 | 325-331, 1006-1014 |
| 90 | Give each piece of UI state one owner and model async UI explicitly. | 114 | 701-709, 760-764, 1106-1107 |
| 91 | Treat browser origins, scripts, storage, and permissions as security boundaries; never treat client validation or state as authority. | 115, 116 | 385-387, 692-700, 704, 709, 1028-1034 |
| 92 | Build internationalization into the data model and UI layout. | 117 | 115-118, 522-532 |
| 93 | Optimize from evidence, budgets, percentiles, and saturation, not guesses or averages. | 118 | 94-95, 400, 404-405, 823, 829-830, 904, 1035, 1122 |
| 94 | Treat data movement, locality, remote calls, and layout as design costs. | 119 | 411-414, 802-806, 811-824, 937-938, 1124 |
| 95 | Assign owners and release gates for load, capacity, cost, and resource budgets. | 120 | 408-410, 415-416, 827-830, 947, 1071 |
| 96 | Preserve user intent, work, and durable state across failure and lifecycle changes. | 52, 122 | 87, 446, 573-580, 760-765, 1074-1079, 1117, 1120 |
| 97 | Treat automation and tool calls as scoped proposals requiring authorization. | 123 | 360-364, 554-560, 1052-1053 |
| 98 | Define decisions, guardrails, denominators, and stopping rules before trusting metrics. | 125 | 30, 148, 792-801 |
| 99 | Treat data, model, and evaluation pipelines as reproducible production systems. | 126 | 457-468, 1047, 1066, 1070 |
| 100 | Log adaptive-system decisions and defend them against feedback gaming. | 127 | 767-772, 1051 |
| 101 | Assign accountable actors, durable evidence, and role separation for high-impact systems. | 128 | 949-959, 1053 |
| 102 | Use public platform APIs and make compatibility a tested release matrix. | 129 | 766, 881-901 |
| 103 | Updates are remote privileged code; sign them, validate them, and preserve recovery paths. | 130 | 890-901, 1114-1119 |
