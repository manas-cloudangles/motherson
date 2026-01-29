# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A reusable accordion component that provides collapsible content sections. It accepts a title input for the header text and an isExpanded input to control the initial state. The component emits a toggle event when the accordion is opened or closed. Use this component to organize content into collapsible sections, ideal for FAQs, settings panels, or any content that benefits from a show/hide functionality. The component uses Font Awesome icons to indicate the expanded/collapsed state and supports content projection via ng-content.

**Import Path**: `app/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable action buttons component that dynamically renders a group of small icon buttons based on a configuration array. Supports standard actions like edit, delete, view, approve, reject with appropriate icons and styling. Emits the clicked action name when any button is pressed. Ideal for table rows, cards, or any UI element that needs compact action controls.

**Import Path**: `app/components/app-action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: A reusable autocomplete component that provides type-ahead functionality with a dropdown list of suggestions. It accepts an array of data items and filters them based on user input. The component supports both string arrays and object arrays with configurable label keys. Key features include: @Input() data - array of items to search through; @Input() labelKey - property name for object labels (default: 'name'); @Input() placeholder - input field placeholder text; @Output() selected - emits the selected item when user clicks a suggestion. The component automatically handles click-outside-to-close behavior and displays filtered results in a styled dropdown. Use this component in forms where users need to select from a large dataset with type-ahead assistance, such as country selection, product search, or user lookup fields.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides customizable styling and behavior. It accepts inputs for label text, button type (button/submit/reset), disabled state, and visual variant (primary/secondary/danger). The component emits a clicked event when clicked (if not disabled). Use this component throughout your application for consistent button styling and behavior, replacing standard HTML buttons with this enhanced version that supports different visual themes and click handling.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal with customizable title, message, and button labels. It provides two-way communication through confirm and cancel events. Use this component when you need user confirmation before proceeding with destructive or important actions. The dialog visibility is controlled by the isOpen input property, and it emits events when the user clicks confirm or cancel buttons.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns, actions, and data types. Supports multiple data types (date, status badges, boolean, currency) with automatic formatting. Provides loading states, empty state handling, and action buttons per row. Emits action events when users click on row actions like edit or delete. Ideal for displaying lists of entities with consistent formatting and interactive capabilities.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range selector component that provides two date inputs (start and end date) with built-in validation. It accepts startDate and endDate as string inputs, validates that the start date is not after the end date, displays an error message if validation fails, and emits a rangeChange event with both dates whenever either date is changed. Use this component in forms or filters where users need to select a date range, such as report filters, search criteria, or date-based data filtering interfaces.

**Import Path**: `app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A reusable file-upload component that restricts uploads by file type and size. It accepts an array of allowed MIME types (default: PNG, JPEG, PDF) and a maximum file size in MB (default: 5 MB). When a valid file is selected it emits the File object through the fileSelected output event. The component displays the chosen filename and any validation errors inline. Use it anywhere a single-file upload is needed while enforcing type/size constraints.

**Import Path**: `app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A reusable footer component that displays a copyright notice with the current year and a shared component banner indicator. It automatically calculates and displays the current year for copyright information. The component features a dark theme with gradient styling and is designed to be placed at the bottom of application layouts. It has no inputs or outputs and is purely presentational.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent card-based layout for forms with header, content area, and footer actions. It includes customizable title, submit/cancel buttons with labels, loading state management, and form validation state. The component emits events when submit or cancel is clicked, and disables the submit button during loading or when the form is invalid. Use this component to wrap any form content to ensure consistent styling and behavior across the application.

**Import Path**: `app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A navigation header component that displays the application title 'ELogbook Zydus' and provides dropdown navigation menus for Master components (Customer Master, Product Master, BMR/BPR Tracking, Checklist, Sample Program) and Logs components (Authorised List, Autonomous Maintenance, Batch Cancellation, Certificate Numbering, Checklist Management, Datasheet Selection, Disinfectant Preparation, DO HOS Verification). The component uses mouseenter/mouseleave events to toggle dropdown visibility and includes router navigation with active link highlighting. It also displays a shared component usage banner and badge indicating that all navigation items use the app-button component.

**Import Path**: `app/common/components/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A reusable search input component that provides a styled search box with an integrated search icon and clear button. It emits search events when the user types or presses enter, and allows clearing the search term. Features include customizable placeholder text, immediate search on input change, and a clear button that appears only when there's text. Use this component in list views, tables, or any interface requiring search functionality.

**Import Path**: `app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays a colored badge based on status text. It accepts a status string input and an optional mapping object for custom color assignments. The component automatically applies semantic colors (success, danger, warning, info, secondary) based on predefined keywords or custom mappings. Use this component to display status indicators in tables, cards, or forms where visual status representation is needed.

**Import Path**: `app/common/components/app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

