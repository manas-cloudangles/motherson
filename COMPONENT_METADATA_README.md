# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a title header and expandable content area. It accepts a title input for the header text and an isExpanded input to control the expanded/collapsed state. The component emits a toggle event with the new state when clicked. Use this component to organize content into collapsible sections, ideal for FAQs, settings panels, or any grouped content that should be expandable. The component uses Font Awesome icons to indicate the current state and supports custom content via ng-content projection.

**Import Path**: `app/common/components/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable component that renders a group of small action buttons (edit, delete, view, approve, etc.) as an icon-only button group. It accepts a config array of action strings and emits the clicked action name via EventEmitter. Each button automatically gets an appropriate FontAwesome icon, Bootstrap color class, and hover styling. Use it in tables, cards, or anywhere you need compact action controls.

**Import Path**: `app/common/components/app-action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: A reusable autocomplete component that provides type-ahead search functionality. It accepts an array of data items and displays filtered suggestions as the user types. The component supports custom label keys for object data, customizable placeholder text, and emits a selected event when an item is chosen. It automatically handles click-outside-to-close behavior and works with both string arrays and object arrays. Use this component when you need a search input with dropdown suggestions, such as for selecting from a list of users, products, or any searchable data set.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides a customizable button with multiple variants (primary, secondary, danger). It accepts inputs for label text, button type, disabled state, and visual variant. The component emits a clicked event when clicked (if not disabled). Use this component throughout the application for consistent button styling and behavior, replacing standard HTML buttons with this enhanced version that supports different visual styles and click handling.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal with customizable title, message, and button labels. It accepts inputs for title, message, confirm button text, cancel button text, and visibility state. The component emits confirm and cancel events when the respective buttons are clicked. Use this component when you need user confirmation before performing critical actions like deletions, updates, or other irreversible operations. The dialog can be controlled via the isOpen input to show/hide the modal.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns, supports multiple data types (date, status badges, boolean, currency), includes loading and empty states, and provides action buttons per row. It accepts data array, column configuration, available actions, and loading state as inputs, and emits action events when buttons are clicked. Use this component when you need a consistent, styled data table with built-in formatting for common data types and action handling.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range picker component that provides two date inputs (start and end date) with validation. It accepts startDate and endDate as string inputs, validates that the start date is not after the end date, and emits a rangeChange event with both dates when either date is changed. Displays an error message if the start date is after the end date. Ideal for filtering data by date ranges in forms, reports, or search interfaces.

**Import Path**: `app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A reusable file upload component that provides a styled file input with validation. It accepts file type restrictions via allowedTypes input (defaults to PNG, JPEG, PDF), enforces a maximum file size via maxSizeMB input (defaults to 5MB), and emits the selected File through the fileSelected output event. Displays the chosen filename and validation error messages inline. Use whenever you need a consistent, validated file upload experience across the application.

**Import Path**: `app/common/components/app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A reusable footer component that displays a copyright notice with the current year and includes a shared component banner indicator. It automatically calculates and displays the current year for copyright information. The component has no inputs or outputs and is designed to be used as a standard footer element in Angular applications.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent layout for forms with a card-based UI. It includes a customizable header with title, a content area for form fields (via ng-content), and a footer with submit and cancel buttons. The component handles loading states, form validation, and emits events for form submission and cancellation. It accepts inputs for title, loading state, button labels, and validation state. Use this component to standardize form presentation across your application with built-in loading indicators and disabled states.

**Import Path**: `app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A navigation header component for the ELogbook Zydus application. It displays the application title and provides dropdown navigation menus for accessing different modules including Master components (Customer Master, Product Master, BMR/BPR Tracking, Checklist, Sample Program), Record components (Cleaning Record, DO Activity, Equipment Usage, Line Clearance), and Log components (Authorised List, Autonomous Maintenance, Batch Cancellation, Certificate Numbering, Checklist Management, Datasheet Selection, Disinfectant Preparation, DO HOS Verification). The component uses mouse hover events to toggle dropdown menus and includes router navigation with active state highlighting.

**Import Path**: `app/common/components/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A search input component that provides real-time search functionality with a clear button. It emits search events when the user types or presses enter, and includes a clear button that appears when there's text in the input. The component accepts a customizable placeholder text and uses two-way binding for the search term. Ideal for implementing search functionality in tables, lists, or any content that needs filtering.

**Import Path**: `app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays a colored badge based on status text. It accepts a status string and an optional mapping object to customize badge colors. The component automatically applies CSS classes based on the status value (success, danger, warning, info, secondary) using built-in heuristics or custom mappings. Use this component to display status indicators in tables, cards, or forms where you need to visually represent different states like active/inactive, approved/rejected, pending/completed, etc.

**Import Path**: `app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

