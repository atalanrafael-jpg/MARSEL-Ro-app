# MARSEL — Ремонт очков: рабочая модель V1

Status: DESIGN / NOT LIVE IN RO APP

## 1. Карточка заказа
- customer_id
- received_at
- promised_at
- eyewear_brand
- eyewear_model
- frame_material
- frame_color
- lens_type
- serial/reference when applicable
- condition_at_receipt
- customer_complaint
- diagnosis
- agreed_work
- estimate
- final_price
- technician_id
- status
- acceptance/delivery evidence
- photos/documents

## 2. Defect directory
- broken_frame
- cracked_frame
- bent_frame
- broken_temple
- loose_hinge
- broken_hinge
- missing_screw
- missing_nose_pad
- damaged_lens
- loose_lens
- poor_adjustment
- contamination
- other

Russian labels must be maintained in the reference-data layer.

## 3. Operation directory
- frame_repair
- temple_repair
- hinge_repair
- nose_pad_replacement
- lens_replacement
- screw_replacement
- soldering
- alignment_adjustment
- cleaning
- polishing
- diagnostics
- other

## 4. Parts/materials
Each consumed item should link to a canonical material/part ID, quantity, unit, cost basis and warehouse movement where supported.

Examples: screws, nose pads, hinges, temples, lenses, solder/materials, cleaning consumables.

Do not invent stock, prices or supplier data.

## 5. Status lifecycle
`received → diagnostics → awaiting_customer → approved → in_repair → quality_check → ready → delivered`

Alternative terminal state: `cancelled`.

Actual status values must be mapped to the live Ro App schema before implementation.

## 6. Documents/evidence
Recommended attachments: intake photos, defect photos, estimate/approval, repair evidence, final condition, delivery/acceptance document.

## 7. Pricing/cost control
Keep estimated and final price separate. Component cost should remain traceable to consumed parts/materials and defined labor/operation basis. Exact production formula requires approval and live-system validation.

## 8. Quality gate
Before closing a repair order:
- customer/item identity verified;
- diagnosis recorded;
- agreed operation recorded;
- consumed parts reconciled;
- final inspection recorded;
- attachments available where required;
- final price recorded;
- delivery evidence recorded.

## Safety
This is a design specification only. It does not authorize production writes. Live Ro App capabilities, schemas, backup/restore and API access must be verified first.
