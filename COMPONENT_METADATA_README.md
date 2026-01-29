# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a header with a title and expandable content area. It accepts a title string and isExpanded boolean as inputs, and emits a toggle event when the header is clicked. The component shows/hides content using ng-content projection and displays a chevron icon that changes direction based on the expanded state. Use this component to organize content into collapsible sections, ideal for FAQs, settings panels, or any content that benefits from a compact, expandable interface.

**Import Path**: `app/common/components/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable action buttons component that renders a group of small icon buttons based on a configuration array. It accepts a 'config' input array of action strings (e.g., ['edit','delete','view','approve']) and dynamically assigns appropriate Font Awesome icons, Bootstrap button classes, and titles. The component emits a 'clicked' event with the action string when any button is pressed. Use this component in tables, cards, or lists where multiple row/item actions are needed without writing individual buttons.

**Import Path**: `app/common/components/app-action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: A reusable autocomplete input component that provides typeahead functionality with dropdown suggestions. It accepts an array of data items and filters them based on user input, displaying matching results in a dropdown list. The component supports both string arrays and object arrays with configurable label keys. Key inputs include 'data' (the array of items to search), 'labelKey' (property name for object labels), and 'placeholder' (input placeholder text). It emits a 'selected' event when a user selects an item from the suggestions. Use this component when you need search-as-you-type functionality in forms, search bars, or any input field requiring autocomplete features. The component automatically handles click-outside events to close the dropdown and provides keyboard-friendly interaction.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides consistent styling and behavior across the application. It supports multiple button types (button, submit, reset), visual variants (primary, secondary, danger), and can be disabled. The component emits a clicked event when clicked (if not disabled). Use this component whenever you need a button in forms, dialogs, or action panels to maintain consistent styling and behavior.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal with customizable title, message, and button labels. It provides two-way communication through confirm and cancel events. Use this component when you need user confirmation before executing critical actions like deletions, updates, or irreversible operations. The component accepts inputs for title, message, button labels, and visibility state, and emits events when the user confirms or cancels the action.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns, actions, and data types. Supports multiple data types including dates, status badges, booleans, and currency. Features loading states, empty state handling, and action buttons for each row. Emits action events when buttons are clicked. Ideal for displaying lists of records with consistent formatting and interactive capabilities.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range picker component that provides two date inputs for selecting start and end dates. It validates that the start date is not after the end date and emits the selected range via the rangeChange event. Use this component when you need users to select a date range for filtering, reporting, or date-based operations. The component displays validation errors inline and uses Bootstrap styling for the form controls.

**Import Path**: `app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A reusable file-upload component that wraps a native file input with validation. It accepts @Input allowedTypes (array of MIME types, default ['image/png','image/jpeg','application/pdf']) and @Input maxSizeMB (number, default 5). When a file is selected it validates type and size; on success it sets the label to the filename and @Output fileSelected emits the File object, otherwise an inline error message is shown. Use it anywhere a single file needs to be uploaded with immediate client-side validation.

**Import Path**: `app/common/components/app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A reusable footer component that displays a shared component banner and a copyright notice with the current year. It automatically calculates and displays the current year for copyright information. Use this component as the standard footer across the application to ensure consistent branding and legal information display.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent card-based layout for forms with header, content area, and footer actions. It includes customizable title, submit/cancel buttons with configurable labels, loading state management, and form validation integration. The component emits events for form submission and cancellation, and supports content projection for the main form content. Use this component when you need a standardized form container with consistent styling and behavior across your application.

**Import Path**: `app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A navigation header component for the ELogbook Zydus application. It displays the application title and provides dropdown navigation menus for accessing master components (Customer Master, Product Master, BMR/BPR Tracking, Checklist, Sample Program) and log components (Authorised List, Autonomous Maintenance, Batch Cancellation, Certificate Numbering, Checklist Management, Datasheet Selection, Disinfectant Preparation, DO HOS Verification). The component uses mouse hover events to toggle dropdown menus and includes router links for navigation. It also displays a banner indicating shared component usage and a badge showing that all navigation items use the app-button component.

**Import Path**: `app/common/components/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A search input component that provides real-time search functionality with a clear button. It accepts a placeholder text as input and emits search events when the user types or presses enter. The component includes a search icon on the left and a clear button that appears on the right when there's text. Use this component in forms, tables, or anywhere you need search/filter functionality. It supports immediate search on model change and clear functionality to reset the search term.

**Import Path**: `app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays status text with appropriate styling based on the status value. It accepts a status string and an optional custom mapping object that maps status values to CSS classes. The component automatically applies color-coded badge styles (success, danger, warning, info, secondary) based on predefined heuristics or custom mappings. Use this component to display status indicators in tables, cards, or forms where you need to visually distinguish different states like active/inactive, approved/rejected, pending/completed, etc. The badge is pill-shaped with subtle shadow and proper padding for better visibility.

**Import Path**: `app/common/components/app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

