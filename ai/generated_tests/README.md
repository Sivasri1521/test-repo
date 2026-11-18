# AI-generated test pack (review exercise)

`test_ai_generated.py` was produced by an AI assistant from the BRD, the STTM and the pipeline code. It runs green:

    pytest ai/generated_tests -v

Your job: review it like a tech lead, then like the business user. Log every gap in
`templates/06_ai_review_log.md` (what the model got wrong, why it matters, your fix), and move corrected
versions into `tests/`. The list of model errors is the deliverable, not the code.

Ask of every test: what would make it fail? And was it written from the requirement, or from the code?
