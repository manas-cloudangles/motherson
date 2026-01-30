# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a header with a title and chevron icon. When clicked, it toggles the visibility of its content area. It accepts a title input for the header text and an isExpanded input to control the initial state. The component emits a toggle event with the current expanded state when clicked. Use this component to create collapsible sections in forms, settings panels, or content organization where space needs to be managed efficiently.

**Import Path**: `app/common/components/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable button group component that renders a set of action buttons (edit, delete, view, approve, etc.) based on a configuration array. Each button displays an appropriate Font Awesome icon and uses color-coded styling. The component emits the name of the clicked action through the 'clicked' output event. Use this component in tables, cards, or any UI where multiple row-level actions are needed. It automatically assigns icons, CSS classes, and tooltips based on the action names provided in the config input.

**Import Path**: `app/common/components/app-action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: A reusable autocomplete component that provides type-ahead search functionality with dropdown suggestions. It accepts an array of data items and filters them based on user input, displaying matching results in a dropdown list. The component supports custom labeling through the labelKey input, customizable placeholder text, and emits a selected event when an item is chosen. It includes click-outside detection to close the suggestions list when clicking elsewhere on the page. Use this component in forms or search interfaces where users need to select from a predefined list of options with type-ahead assistance.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides consistent styling and behavior across the application. It accepts inputs for label text, button type (button/submit/reset), disabled state, and visual variant (primary/secondary/danger). The component emits a clicked event when clicked (if not disabled). Use this component whenever you need a styled button with consistent behavior, especially in forms or action panels where you need different button types and states.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal with customizable title, message, and button labels. It provides two-way binding through isOpen input to control visibility, and emits confirm/cancel events when buttons are clicked. Use this component when you need user confirmation before executing critical actions like deletions, updates, or irreversible operations. The dialog automatically handles backdrop clicks and includes proper ARIA attributes for accessibility.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns, actions, and data types. Supports multiple column types (date, status badge, boolean, currency, text), loading states, empty states, and action buttons per row. Emits actionClicked events when action buttons are clicked. Use this component when you need to display structured data in a table format with optional row actions and different data type formatting.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range picker component that provides two date inputs (start and end date) with validation. It accepts startDate and endDate as string inputs and emits a rangeChange event with an object containing both dates when either date changes. The component validates that the start date is not after the end date and displays an error message if this condition is violated. Use this component when you need a simple, validated date range selector in forms or filters.

**Import Path**: `app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A reusable file upload component that handles file selection with validation for file type and size. It accepts allowed file types and maximum file size as inputs, validates selected files against these constraints, and emits the selected file through an output event. Use this component when you need a consistent file upload experience with built-in validation across your application.

**Import Path**: `app/app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A footer component that displays copyright information with the current year and a shared component banner indicator. It automatically calculates and displays the current year for copyright notices. The component has a dark theme with a gradient banner showing 'SHARED COMPONENT USED' and is designed to be used at the bottom of application layouts.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent layout for forms with a card-based design. It includes a customizable header with title, a content area for form fields (using ng-content), and a footer with submit and cancel buttons. The component handles loading states, form validation states, and emits events for form submission and cancellation. It accepts inputs for title, loading state, button labels, and validation state, making it ideal for standardizing form presentation across the application.

**Import Path**: `app/common/components/app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A navigation header component for the ELogbook Zydus application. It displays the application title and provides dropdown navigation menus for Master components (5 items), Records components (4 items), and Logs components (8 items). The component uses hover-based dropdown toggling and includes router links for navigation. It also displays a shared component usage banner and badge to indicate component reuse patterns.

**Import Path**: `app/common/components/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A reusable search input component that provides a styled search box with an integrated clear button. It emits search events when the user types or presses enter, and includes a clear functionality to reset the search term. The component accepts a placeholder text input and outputs search terms as strings. Use this component in list views, tables, or any UI that requires filtering by text search.

**Import Path**: `app/search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays status text with appropriate styling based on the status value. It accepts a status string input and an optional mapping object for custom status-to-style mappings. The component automatically applies CSS classes (badge-success, badge-danger, badge-warning, badge-info, badge-secondary) based on the status value using built-in heuristics or custom mappings. Use this component to display status indicators throughout your application with consistent styling.

**Import Path**: `app/common/components/app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

