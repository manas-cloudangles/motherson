# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a header with a title and a chevron icon. When clicked, it toggles the visibility of its content area. It accepts a title input for the header text, an isExpanded input to control its initial state, and emits a toggle event when the state changes. Use this component to organize content into collapsible sections, ideal for FAQs, settings panels, or any grouped information that should be expandable/collapsible. The component uses ng-content to project custom content into the expandable body area.

**Import Path**: `app/common/components/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable action buttons component that renders a group of small icon buttons based on a configuration array. Supports standard actions like edit, delete, view, approve, reject with appropriate icons and styling. Emits the clicked action name when any button is pressed. Used in tables, cards, or any UI element that needs compact action controls.

**Import Path**: `app/action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: An autocomplete input component that filters a list of items based on user input. It accepts an array of data items, displays matching suggestions in a dropdown, and emits the selected item. Features include customizable placeholder text, configurable label key for object properties, click-outside-to-close functionality, and keyboard navigation support. Use this component when you need a type-ahead search input with filtered suggestions, such as for selecting users, products, or any searchable list.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides a styled button with customizable label, type, variant, and disabled state. It supports three variants (primary, secondary, danger) and emits a clicked event when clicked (if not disabled). Use this component whenever you need a consistent, styled button across your application with proper event handling and disabled state management.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal with customizable title, message, and button labels. It provides two-way communication through confirm and cancel events. Use this component when you need user confirmation before executing critical actions like deletions, updates, or irreversible operations. The dialog visibility is controlled by the isOpen input property.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns, supports multiple data types (date, status, boolean, currency), includes loading states, and provides action buttons for each row. It accepts data array, column definitions, action types, and loading state as inputs, and emits action events when buttons are clicked. Use this component when you need to display structured data with consistent formatting and row-level actions like edit/delete.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range picker component that provides two date inputs (start and end date) with validation. It accepts startDate and endDate as string inputs, validates that the start date is not after the end date, and emits a rangeChange event with both dates when either date is changed. Displays an error message if the start date is after the end date. Used for filtering data by date ranges in forms or search interfaces.

**Import Path**: `app/common/components/app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A reusable file upload component that provides a styled file input with validation. It accepts allowed file types and maximum file size as inputs, validates selected files against these constraints, and emits the selected file through an output event. Use this component when you need a consistent file upload experience with built-in validation for file types and size limits.

**Import Path**: `app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A reusable footer component that displays a shared component banner and copyright information. It automatically displays the current year and shows a visual indicator when shared components are being used. The component has a dark background with white text and is designed to be placed at the bottom of the application layout.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent layout for forms with a card-based design. It includes a customizable header with title, a content area for form fields (using ng-content), and a footer with submit and cancel buttons. The component handles form submission logic with loading states and validation checks. It accepts inputs for title, loading state, button labels, and validation status, and emits events for form submission and cancellation. Ideal for standardizing form appearance across an application with built-in loading indicators and disabled states.

**Import Path**: `app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A navigation header component for the ELogbook Zydus application. It displays the application title and provides dropdown navigation menus for accessing different sections of the application including Master components (5 items), Records (4 items), and Logs (8 items). The component features hover-based dropdown menus that show/hide navigation links to various routes. It includes visual indicators showing that shared components are being used and that all navigation items use the app-button component.

**Import Path**: `app/common/components/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A reusable search filter component that provides a text input field with search and clear functionality. It features a search icon on the left, a clear button that appears when text is entered, and emits search events when the user types or presses enter. The component accepts a placeholder text as input and outputs search terms as the user types or submits. Ideal for implementing search functionality in lists, tables, or any data display that requires filtering capabilities.

**Import Path**: `app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays status text with appropriate color styling based on the status value. It accepts a status string and an optional custom mapping object to determine the badge color. The component uses built-in heuristics to automatically assign colors for common status values (e.g., 'active' → green, 'rejected' → red, 'pending' → yellow). The badge is pill-shaped with subtle shadow styling and displays the status text in title case. Use this component to consistently display status indicators throughout your application with minimal configuration.

**Import Path**: `app/common/components/app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

