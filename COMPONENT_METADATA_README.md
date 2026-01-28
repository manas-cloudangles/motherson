# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a header with a title and expandable content area. Features include: @Input() title (string) for the section header text, @Input() isExpanded (boolean) to control expanded/collapsed state, @Output() toggle (EventEmitter<boolean>) that emits the new expanded state when clicked. Use this component to organize content into collapsible sections, ideal for FAQs, settings panels, or any grouped content that should be expandable. The component automatically handles expand/collapse animations and provides visual feedback with chevron icons.

**Import Path**: `app/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable action buttons component that renders a group of small icon buttons based on a configuration array. It accepts a 'config' input array of action strings (like 'edit', 'delete', 'view', 'approve') and dynamically creates buttons with appropriate Font Awesome icons and Bootstrap button styling. The component emits a 'clicked' event with the action string when any button is clicked. Use this component in tables, cards, or any UI area where you need compact action buttons for operations like edit, delete, view, approve, etc.

**Import Path**: `app/action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: A reusable autocomplete component that provides type-ahead suggestions from a provided data array. It filters data based on user input and emits the selected item. Features include customizable label keys, placeholder text, and click-outside-to-close functionality. Use this component when you need a search input with dynamic suggestions, such as for selecting users, products, or any searchable list. The component accepts an array of objects or strings as data, displays filtered suggestions in a dropdown, and emits the selected item through the 'selected' output event.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides consistent styling and behavior across the application. It supports multiple button types (button, submit, reset), three visual variants (primary, secondary, danger), and can be disabled. The component emits a 'clicked' event when clicked (if not disabled). Use this component whenever you need a button in forms, dialogs, or action panels to ensure consistent styling and behavior.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal with customizable title, message, and button labels. It provides two-way communication through confirm and cancel events. Use this component when you need user confirmation before proceeding with destructive or important actions like deletions, updates, or form submissions. The dialog visibility is controlled by the isOpen input property.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with customizable columns, supports multiple data types (date, status, boolean, currency), includes loading states, and provides action buttons for row operations. It accepts data array, column configuration, available actions, and loading state as inputs, and emits action events when buttons are clicked. Use this component when you need to display structured data in a table format with sorting, filtering, or action capabilities.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range picker component that provides two date inputs (start and end date) with validation. It accepts startDate and endDate as string inputs, validates that the start date is not after the end date, and emits a rangeChange event with both dates when either date is modified. Use this component in forms or filters where users need to select a date range, such as report generation, data filtering, or booking systems. The component displays an error message if the start date is after the end date and prevents invalid ranges from being emitted.

**Import Path**: `app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A reusable file upload component that provides a styled file input with validation. It accepts allowed file types and maximum file size as inputs, validates selected files against these constraints, and emits the selected file through an output event. Use this component when you need a consistent file upload experience with built-in validation for file type and size. The component displays validation errors and shows the selected file name.

**Import Path**: `app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A reusable footer component that displays a copyright notice with the current year and includes a shared component banner indicator. It automatically calculates and displays the current year for copyright information. Use this component as the standard footer across the application to ensure consistent branding and legal compliance. The component has no inputs or outputs - it operates independently once included in a template.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent card-based layout for forms with header, content area, and footer actions. It includes customizable title, submit/cancel buttons with labels, loading state management, and form validation state handling. The component emits events when submit or cancel actions are triggered. Use this component to wrap form content and provide standard form UI patterns across the application.

**Import Path**: `app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A navigation header component that displays the application title 'ELogbook Zydus' and provides dropdown navigation menus for accessing different sections of the application. It contains three main navigation categories: Master (5 components), Records (4 components), and Logs (8 components), each with hover-triggered dropdown menus. The component manages dropdown visibility states and provides routing links to various master, record, and log components. It features a shared component banner indicator and is designed to be used as the main header across the application.

**Import Path**: `app/common/components/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A search input component that provides a styled search box with an integrated search icon and clear button. It emits search events when the user types or presses enter, and allows clearing the search term. Features include customizable placeholder text, immediate search on input change, and a clear button that appears when there's text. Use this component in list views, tables, or any UI that requires filtering content by search terms.

**Import Path**: `app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays a colored badge based on status text. It accepts a status string and an optional custom mapping object to determine the badge color. The component automatically applies CSS classes for styling based on predefined heuristics (success, danger, warning, info, secondary) or custom mappings. Use this component to consistently display status indicators throughout your application with automatic color coding based on status text.

**Import Path**: `app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

