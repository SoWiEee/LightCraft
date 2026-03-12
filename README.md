# LightCraft Docs Bundle

This archive contains the second-draft Software Design Description for **LightCraft Desktop**, a workflow-based photo editor for photography beginners, plus this README for navigation and usage.

## Included Files

- `sdd.md`  
  Draft 2 of the Software Design Description. This version is more implementation-oriented than the first draft and includes architecture, module boundaries, UI layout, state models, sequence flows, acceptance criteria, risks, and MVP cutline.

## What Changed in v0.2

Compared with an earlier high-level draft, this version adds the parts that usually decide whether implementation stays under control:

1. clearer subsystem boundaries
2. explicit UI layout and navigation rules
3. data model and history snapshot policy
4. slider commit policy to avoid history spam
5. deterministic processing order
6. AI recommendation architecture and fallback path
7. error handling and concurrency guidance
8. sequence flows and class sketch
9. acceptance criteria and testing strategy
10. implementation order and MVP cutline

## Recommended Next Steps

1. derive `tasks.md` from the implementation order in section 31
2. create wireframes for the main window and crop mode
3. freeze exact slider ranges after a small prototype
4. choose one Hugging Face model path for recommendation
5. write a minimal `spec.md` to `sdd.md` traceability check if needed
6. start coding with image load, histogram, and preview render loop

## Suggested Immediate Deliverables After This

- `tasks.md`
- `architecture.drawio` or Mermaid diagrams
- `api_contracts.md` for controller/service interfaces
- `test_plan.md`
- `milestones.md`

## Notes

- The design assumes JPEG and PNG first. RAW is intentionally deferred.
- AI is treated as optional assistance. Manual editing must work even when AI is unavailable.
- The source image is preserved through a non-destructive model.

