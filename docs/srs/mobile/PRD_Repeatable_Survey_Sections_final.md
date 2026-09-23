**Product Requirements Document**

**Repeatable Survey Sections / Looping Functionality**

Feature for dynamic repeated sections in survey templates and mobile survey completion

| Field | Value |
| :---- | :---- |
| Document type | PRD / SRS input |
| Feature name | Repeatable Survey Sections / Looping |
| Version | 1.0 |
| Date | 2026-07-06 |
| Prepared for | Admin Portal, Mobile App, API, COPS Sync, QA, PM teams |

## **Feature visualization**

![][image1]

# **1\. Feature Overview**

The client requested functionality similar to GoCanvas "looping", where a survey section can be repeated by the technician as many times as needed during survey completion.

This feature allows an admin to create a section once in the survey/template builder, mark it as repeatable, and let the technician add multiple instances of that same section in the mobile app.

Example: a survey contains a section called Room Information. A site may have one room or many rooms. Instead of creating fixed duplicated sections such as Room 1, Room 2, Room 3, etc., the admin creates one Room Information section and enables repeatability. The technician can then add as many rooms as needed while completing the survey.

# **2\. Problem Statement**

Currently, surveys are built with a fixed structure. If the number of required data groups depends on field conditions, the admin must manually create multiple duplicate sections in advance.

* Unnecessary sections: if a survey contains 10 room sections but the site has only 1 room, the technician sees irrelevant fields.  
* Insufficient sections: if a survey contains 5 room sections but the site has 8 rooms, the technician cannot properly capture all required data.

The system needs a flexible way to collect repeated data sets within one survey section.

# **3\. Business Goal**

Allow survey templates to support dynamic repeated sections so that technicians can capture information for multiple rooms, assets, items, or locations without requiring admins to predefine a fixed number of duplicated sections.

# **4\. Primary Use Case**

An admin creates a section called Room Information and marks it as repeatable. The section can contain all existing field types, including the existing Photo type. The section title can be used as any (“Room” used in PRD as a reference). During job execution, the technician can add Room 1, Room 2, Room 3, and more rooms as needed. Each room uses the same field structure but stores a separate set of answers.

* Room Name  
* Room Type  
* Notes  
* Photos  
* Checklist items

# **5\. User Roles**

| Role | Description |
| :---- | :---- |
| Admin / Template Builder | Configures survey templates and decides which sections can be repeated. |
| Technician / Mobile User | Completes the survey in the field and adds repeated section instances as needed. |
| Back Office / Reviewer / Project Facilitator | Reviews submitted survey responses and needs to clearly see each repeated section instance. |
| COPS System / COPS Users | Have access to the Admin Panel where they can edit surveys and view mobile responses. COPS must support nested repeatable section data. |

# **6\. Confirmed MVP Decisions**

| Topic | Confirmed Decision | PRD Impact |
| :---- | :---- | :---- |
| Min/max repeated instances | No min/max limits are needed in MVP. | Exclude min/max configuration and validation from MVP. |
| Delete repeated instances | Technicians can delete instances they created themselves. | Mobile app must support delete flow and offline/draft persistence of deletion. |
| Manual instance rename | Technicians cannot rename instances manually. | Instance naming is controlled by Admin label and system numbering. |
| Field type support | Repeatable sections support all existing field types. | Mobile, API, validation, and storage must support all current field types inside repeated instances. |
| Photo support | Photos are supported through the existing Photo type. | Photo answers must remain linked to the correct repeated instance. |
| Offline/draft mode | Repeatable sections must work offline and in draft mode. | Mobile local state and sync logic must persist repeated instances. |
| COPS access | COPS users have Admin Panel access to edit surveys and view mobile responses. | COPS-related behavior must support survey editing and response visibility. |
| COPS storage | COPS should store repeatable data as nested objects. | Sync/API mapping must preserve nested structure. |
| Admin Response page | Existing Admin Response page does not need frontend changes. | No separate response page frontend task in MVP. |
| Edit after usage | Repeatable sections can be edited after a template has been used. | Backward compatibility and response readability must be preserved. |

# **7\. MVP Scope**

* Admin can mark a survey/template section as repeatable.  
* Admin can configure the repeated instance label, for example Room.  
* The system automatically names repeated instances based on Admin-defined label and sequence number, for example Room 1, Room 2, Room 3\.  
* Technician cannot manually rename repeated instances.  
* Technician can add multiple repeated instances.  
* Technician can edit repeated instances.  
* Technician can delete instances they created.  
* Repeatable sections support all existing field types.  
* Photos/attachments are supported through the existing Photo type.  
* Repeatable sections work in draft mode and offline mode.  
* Mobile app submits repeated section data as nested grouped instances.  
* API supports repeatable sections in Survey, Survey Template, and Survey Response entities.  
* COPS stores repeatable section data as nested objects.  
* Existing Admin Response page does not require separate frontend changes.  
* Repeatable sections can be edited after a template has already been used in submitted surveys.  
* Admin Panel and Mobile App regression testing are required.  
* SRS documentation must be updated.

# **8\. Out of Scope for MVP**

* Minimum number of repeated instances.  
* Maximum number of repeated instances.  
* Manual renaming of repeated instances by technician.  
* Nested repeatable sections.  
* Reordering repeated instances.  
* Duplicating an existing repeated instance.  
* Cross-instance validation, for example unique room names.  
* Custom Admin Response page redesign.  
* Advanced export/report customization.  
* Advanced analytics based on repeated section data.

# **9\. Functional Requirements**

## **9.1 Admin Panel Requirements**

* Admin can enable or disable repeatability at the section level.  
* Admin can define the instance label, for example Room.  
* The system uses this label to generate instance names automatically: Room 1, Room 2, Room 3\.  
* Admin can edit repeatable section settings after a template has already been used.  
* Existing submitted responses should remain readable and should not be broken by later template changes.  
* Min/max instance configuration is not required for MVP.  
* Existing non-repeatable sections continue working as before.

  ***Admin Acceptance Criteria***

* Admin can mark a section as repeatable.  
* Admin can define the repeated instance label.  
* Repeatable configuration is saved successfully.  
* Repeatable configuration is restored when editing the survey/template.  
* The system automatically generates repeated instance names based on the Admin-defined label.  
* Existing templates without repeatable sections continue working.  
* Previously submitted responses remain accessible after template changes.

## **9.2 Mobile App Requirements**

* Mobile app detects repeatable sections from the survey/template data.  
* Mobile app renders a repeatable section container.  
* Technician can add a new repeated instance.  
* Each new instance uses the same fields configured in the original section.  
* Technician can edit an existing repeated instance.  
* Technician can delete instances they created.  
* Technician cannot rename repeated instances manually.  
* Instance names are generated automatically using Admin-defined label and sequence number.  
* Repeatable sections support all existing field types.  
* Photo fields work inside repeatable sections.  
* Repeatable section data must be preserved in draft mode and offline mode.

  ***Mobile Acceptance Criteria***

* Technician can add multiple instances of a repeatable section.  
* Technician can complete all supported field types inside each instance.  
* Technician can add photos inside repeated instances using the existing Photo type.  
* Technician can edit saved instances.  
* Technician can delete created instances.  
* Technician cannot manually change instance names.  
* Instance names are shown as system-generated labels, for example Room 1, Room 2\.  
* Repeated data is not lost when the technician saves a draft or works offline and syncs later.  
* Non-repeatable sections continue working as before.

## **9.3 Mobile Submission Payload Requirements**

* Each repeatable section is submitted as a nested object containing repeated instances.  
* Each instance has an instance ID, system-generated display label, sort order, answers, and photo/attachment data where applicable.  
* All existing field types are supported inside repeated instances.  
* Submission payload must preserve instance order, answer-to-instance mapping, and photo-to-instance mapping.  
* Submission must work after offline/draft completion.

{  
  "sectionId": "room\_information",  
  "isRepeatable": true,  
  "instances": \[  
    {  
      "instanceId": "uuid-room-1",  
      "displayLabel": "Room 1",  
      "sortOrder": 1,  
      "answers": \[  
        { "fieldId": "room\_name", "value": "Conference Room" },  
        { "fieldId": "room\_type", "value": "Office" },  
        { "fieldId": "photo", "value": \[{ "fileId": "photo-001", "fileName": "conference-room.jpg" }\] }  
      \]  
    }  
  \]  
}

# **10\. Entity / Data Model Requirements**

## **10.1 Survey Entity**

* Survey entity supports surveys that contain repeatable sections.  
* Existing surveys remain valid.  
* Repeatable section configuration should not break existing survey behavior.  
* Surveys with repeatable sections should support offline/draft response completion from mobile.  
* Survey can be edited after it has already been used in submitted responses.

  ***Acceptance Criteria***

* Existing Survey records remain compatible.  
* New Survey records can include repeatable sections.  
* Survey retrieval works for repeatable and non-repeatable surveys.  
* Editing a survey/template after submitted responses does not break existing response data.

## **10.2 Survey Template Entity**

* Section-level repeatability flag is supported.  
* Repeatable section label is stored.  
* Min/max instance configuration is not included in MVP.  
* Technician rename option is not included.  
* All existing field types are allowed inside repeatable sections.  
* Nested repeatable sections are not allowed.  
* Repeatable section settings can be edited after template usage.  
* Existing templates are treated as non-repeatable by default.

{  
  "sectionId": "room\_information",  
  "title": "Room Information",  
  "isRepeatable": true,  
  "repeatConfig": {  
    "itemLabel": "Room",  
    "allowDelete": true,  
    "allowManualRename": false  
  },  
  "fields": \[\]  
}

***Acceptance Criteria***

* Template entity stores repeatable section settings.  
* Existing templates are treated as non-repeatable.  
* Repeatable sections support all existing field types.  
* Invalid nested repeatable structures are rejected.  
* Min/max values are not required for configuration.  
* Manual rename is not supported.  
* Editing repeatable settings after template usage does not corrupt previous responses.

## **10.3 Survey Response Entity**

* Survey Response entity stores repeated section answers as nested objects.  
* Each repeated instance has instance ID, display label, sort order, and answers.  
* Photo answers are stored under the correct repeated instance.  
* All existing field types are supported inside repeated instances.  
* Draft/offline responses preserve repeated instance data.  
* Existing non-repeatable responses remain readable.

  ***Acceptance Criteria***

* Repeated section responses are stored as nested objects.  
* Each repeated instance is uniquely identifiable.  
* Answers and photos are associated with the correct instance.  
* Instance order is preserved.  
* Existing response data remains readable.  
* Draft/offline sync does not lose repeated instance data.

# **11\. COPS System Sync Requirements**

COPS users have access to the Admin Panel and can edit Surveys and view Responses received from the mobile app. Therefore, COPS-related behavior must support repeatable section structures in both survey editing and response handling.

* COPS should support repeatable section configuration in survey/template editing.  
* COPS should receive and store repeatable response data as nested objects.  
* COPS should preserve section ID, instance ID, instance display label, sort order, field answers, and photo data where applicable.  
* COPS should support viewing mobile responses that contain repeatable section data.  
* COPS should not flatten repeated instances into unrelated fields.  
* COPS should remain backward compatible with non-repeatable survey data.  
* COPS should support survey/template edits after responses have already been submitted.

  ***Acceptance Criteria***

* COPS can work with surveys that contain repeatable sections.  
* COPS stores repeatable response data as nested objects.  
* Repeated instances are not lost during sync.  
* Answers and photos remain mapped to the correct repeated instance.  
* Existing non-repeatable survey data continues to sync and display correctly.  
* Responses submitted before template changes remain readable.

# **12\. User Stories and Acceptance Criteria**

### **Story 1: Admin configures a repeatable section**

**As a** admin, **I want** to mark a survey/template section as repeatable, **so that** technicians can complete the same section multiple times when needed.

***Acceptance Criteria***

* Admin can enable and disable repeatability for a section.  
* Repeatable configuration is saved successfully.  
* Repeatable configuration is restored when editing the survey/template.  
* Existing fields inside the section remain unchanged.  
* Existing non-repeatable sections continue working as before.

### **Story 2: Admin configures repeated instance label**

**As a** admin, **I want** to define the repeated instance label, **so that** the mobile app can display clear system-generated instance names.

***Acceptance Criteria***

* Admin can define an item label, for example Room.  
* The system generates instance names based on label and sequence number.  
* Technician cannot manually rename instances.  
* The configured label is used in mobile and response data.

### **Story 3: Technician adds a repeated instance**

**As a** technician, **I want** to add a new instance of a repeatable section, **so that** I can collect data for multiple rooms, items, or assets.

***Acceptance Criteria***

* Technician sees a repeatable section container.  
* Technician sees an add button, for example Add Room.  
* Tapping the add button creates a new instance.  
* The new instance contains the same fields configured in the template.  
* Technician can complete and save the instance.  
* Saved instance appears in the list of repeated instances.

### **Story 4: Technician edits a repeated instance**

**As a** technician, **I want** to edit a previously added repeated instance, **so that** I can correct or update data before submission.

***Acceptance Criteria***

* Technician can open an existing repeated instance.  
* Existing answers are displayed correctly.  
* Technician can update answers.  
* Updated answers are saved under the same instance.  
* No duplicate instance is created during editing.

### **Story 5: Technician deletes a repeated instance**

**As a** technician, **I want** to delete a repeated instance that I created, **so that** I can remove data added by mistake.

***Acceptance Criteria***

* Technician can delete repeated instances they created.  
* System asks for confirmation before deleting an instance.  
* Deleted instance is removed from the mobile survey state.  
* Deleted instance is not included in the final submission payload.  
* Deleting an instance does not corrupt other repeated instances.  
* If working offline, deletion is preserved and synced correctly later.

### **Story 6: Technician works with repeatable sections offline**

**As a** technician, **I want** repeatable sections to work while offline or in draft mode, **so that** I can continue completing surveys without network dependency.

***Acceptance Criteria***

* Technician can add, edit, and delete repeated instances while offline.  
* Repeated instance data is saved in local/draft state.  
* Repeated instance data is submitted correctly after sync.  
* Photos added inside repeated instances remain linked to the correct instance after sync.

### **Story 7: API stores repeated survey data**

**As a** system, **I want** to store repeatable section responses correctly, **so that** the data can be retrieved, reviewed, and synced.

***Acceptance Criteria***

* Survey entity supports repeatable sections.  
* Survey Template entity stores repeatable configuration.  
* Survey Response entity stores repeated instances.  
* API validates submitted repeated responses.  
* API returns repeated responses in a structured format.  
* Existing non-repeatable survey data remains compatible.

### **Story 8: COPS stores repeatable data as nested objects**

**As a** COPS system, **I want** to store repeatable survey responses as nested objects, **so that** repeated section data remains structured and correctly mapped.

***Acceptance Criteria***

* Repeatable response data is stored as nested objects.  
* Each repeated instance remains under the correct section.  
* Each answer remains under the correct repeated instance.  
* Photos remain linked to the correct repeated instance.  
* COPS can display or process submitted repeatable response data.  
* Existing non-repeatable data is not affected.

# **13\. Updated Task Breakdown**

## **\[UI/UX\] Admin panel survey/template page redesign**

***Scope***

* Design repeatable toggle and Admin-defined item label.  
* Define system-generated naming behavior, for example Room 1, Room 2, Room 3\.  
* Exclude min/max configuration and manual technician rename from MVP designs.  
* Include delete support for technician-created instances.  
* Confirm support for all existing field types and edit-after-usage behavior.

  ***Acceptance Criteria***

* Approved Figma screens and UX notes clearly describe Admin configuration, edge states, and exclusions.

## **\[UI/UX\] Mobile app survey screen redesign**

***Scope***

* Design add, edit, and delete instance flows.  
* Design draft/offline behavior and validation states.  
* Use system-generated instance names.  
* Cover all existing field types and Photo support.

  ***Acceptance Criteria***

* Approved mobile flow covers repeatable section completion and validation without min/max, reorder, duplicate, or manual rename.

## **\[WEB-Frontend\] Add repeatable section to a survey/template editor**

***Scope***

* Add repeatable toggle and item label to the editor.  
* Update template state and create/update payloads.  
* Load existing repeatable configuration when editing a template.  
* Validate repeatable configuration and preserve non-repeatable behavior.

  ***Acceptance Criteria***

* Admin can configure, save, and edit repeatable sections.  
* Non-repeatable templates remain unaffected.

## **\[Mobile-Frontend\] Add repeatable instance creation flow**

***Scope***

* Detect repeatable sections and render the repeatable container.  
* Support add, edit, and delete for repeated instances.  
* Support all existing field types and the existing Photo type.  
* Preserve state in draft and offline mode.

  ***Acceptance Criteria***

* Technician can manage instances successfully.  
* Validation works per instance and data is not lost during navigation or offline use.

## **\[Mobile-Frontend\] Update submission payload**

***Scope***

* Submit nested object structure with instance ID, display label, and sort order.  
* Submit all field answers and Photo data under the correct instance.  
* Support offline/draft sync compatibility.

  ***Acceptance Criteria***

* API receives correctly grouped repeated data.  
* Non-repeatable submissions remain functional.

## **\[API\] Update Survey entity**

***Scope***

* Support surveys containing repeatable sections.  
* Preserve compatibility with existing surveys.

  ***Acceptance Criteria***

* Survey retrieval works for repeatable and non-repeatable surveys.  
* Existing data is not broken.

## **\[API\] Update Survey template entity**

***Scope***

* Store section-level repeatability flag and repeat configuration.  
* Reject nested repeatable sections.  
* Default existing templates to non-repeatable.

  ***Acceptance Criteria***

* Templates store and return repeatable settings.  
* Invalid repeatable structures are rejected.

## **\[API\] Update Survey response entity**

***Scope***

* Store repeated responses as nested objects with instance ID, label, order, answers, and Photo data.

  ***Acceptance Criteria***

* Repeated responses are saved and retrieved correctly.  
* Old responses remain readable.

## **\[API\] COPS system sync**

***Scope***

* Support repeatable section data in COPS as nested objects.  
* Preserve labels, order, answer mapping, and Photo mapping.  
* Maintain backward compatibility for non-repeatable sync.

  ***Acceptance Criteria***

* COPS sync stores/displays repeated data without loss.  
* Non-repeatable sync still works.

## **\[QA\] Admin panel regression testing**

***Scope***

* Test template creation/editing, repeatable configuration, edit-after-usage, and existing templates.  
* Verify no regression in regular section editing.

  ***Acceptance Criteria***

* Admin Panel repeatable functionality passes and existing survey/template behavior remains stable.

## **\[QA\] Mobile app regression testing**

***Scope***

* Test add/edit/delete, all field types, Photo type, validation, draft/offline, sync, and surveys without repeatable sections.

  ***Acceptance Criteria***

* Mobile repeatable flow works and existing survey completion flows remain stable.

## **\[PM\] Updating SRS documentation**

***Scope***

* Update SRS with overview, scope, functional requirements, API/data model, COPS sync, task breakdown, and acceptance criteria.

  ***Acceptance Criteria***

* SRS aligns with confirmed MVP decisions and is ready for estimation and implementation.

# **14\. Validation Rules**

## **14.1 Admin Configuration Validation**

* Section can be either repeatable or non-repeatable.  
* Repeatable section must have a valid item label.  
* Min/max validation is not required in MVP.  
* Nested repeatable sections are not allowed in MVP.  
* Existing fields inside the section should remain valid after enabling repeatability.

## **14.2 Mobile Validation**

* Required fields are validated inside each repeated instance.  
* If one repeated instance is incomplete, survey submission is blocked.  
* Validation message should identify the affected section and instance.  
* Validation should identify the specific field with an issue.  
* Repeated instance data should be preserved until the user intentionally removes or clears it.

## **14.3 API Validation**

* Submitted repeatable section data must match the related template configuration.  
* Instance IDs must be valid and unique within the section.  
* Instance order should be valid.  
* Required answers must be provided per instance.  
* Unsupported nested repeatable structures must be rejected.  
* Non-repeatable sections should not accept repeated instance arrays unless explicitly supported for backward compatibility.

# **15\. Review / Response Display Requirements**

Existing Admin Response page does not require frontend changes for MVP. However, submitted repeated data must remain retrievable and readable through the current response viewing approach.

* Submitted repeated section data should be retrievable through the API.  
* Admin/reviewer should be able to distinguish repeated instances.  
* Each instance should have a clear label, for example Room 1, Room 2, Room 3\.  
* Answers should be displayed under the correct instance.  
* Photos should be displayed under the correct instance.  
* Existing response views should not break when repeatable data is present.

# **16\. Dependencies**

* Survey/template builder structure.  
* Mobile survey rendering engine.  
* Mobile local state/draft storage.  
* Mobile offline sync logic.  
* Mobile submission payload structure.  
* Survey entity.  
* Survey Template entity.  
* Survey Response entity.  
* COPS sync contract.  
* Photo field handling.  
* Validation engine.  
* Existing response/review page behavior.  
* Existing sync error handling and logs.

# **17\. Risks and Mitigation**

| Risk | Description | Mitigation |
| :---- | :---- | :---- |
| Data model complexity | Repeatable sections change response structure from single answers to grouped nested instances. | Define API contract before frontend implementation and cover with API tests. |
| COPS incompatibility | COPS may need updates to store nested objects correctly. | Analyze COPS sync contract early and align on nested storage format. |
| Mobile state issues | Repeated instances may be lost during navigation, draft save, or offline mode. | Add dedicated mobile local state and draft/offline regression tests. |
| Photo mapping issues | Photos may be linked to the wrong repeated instance. | Include instance IDs in Photo mapping and QA test Photo fields inside repeated sections. |
| Backward compatibility | Existing surveys/responses may break if schema changes are not handled carefully. | Add migrations/default values and regression testing. |
| Edit after usage | Template changes after responses exist can create mismatch between old response data and new template structure. | Preserve response snapshots or compatible references; keep previous submitted responses readable. |
| Scope growth | Client may expect full GoCanvas looping features. | Clearly define MVP exclusions: no nested loops, no min/max, no reorder, no duplicate, no manual rename. |

# **18\. Final MVP Definition**

The first version of Repeatable Survey Sections includes:

* Admin Panel survey/template page redesign.  
* Mobile app survey screen redesign.  
* Web frontend support for configuring repeatable sections in the survey/template editor.  
* Mobile frontend support for adding, editing, and deleting repeated instances.  
* Mobile support for repeatable sections in offline and draft mode.  
* Support for all existing field types inside repeatable sections.  
* Support for Photo type inside repeatable sections.  
* System-generated instance names based on Admin-defined label.  
* No technician manual renaming.  
* No min/max instance settings.  
* API updates for Survey, Survey Template, and Survey Response entities.  
* COPS system sync support with nested object storage.  
* Admin Panel regression testing.  
* Mobile App regression testing.  
* SRS documentation update.

[image1]: <data:image/png;base64,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>