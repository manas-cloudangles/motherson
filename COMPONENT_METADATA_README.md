# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a title header and expandable content area. It accepts a title string and isExpanded boolean as inputs, and emits a toggle event when the accordion state changes. Use this component to create organized, space-saving content sections that can be expanded or collapsed by user interaction. The component features a chevron icon that indicates the current state and uses content projection (<ng-content>) to display custom content within the expandable body.

**Import Path**: `app/common/components/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable action buttons component that renders a group of small icon buttons based on a configuration array. Accepts an array of action strings (like 'edit', 'delete', 'view', 'approve') and automatically assigns appropriate icons, button styles, and tooltips. Emits the clicked action name via the clicked EventEmitter when any button is pressed. Use this component in tables, cards, or detail views where multiple quick actions are needed per row/item. Supports built-in styling for common actions with hover effects and consistent sizing.

**Import Path**: `app/components/app-action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: A reusable autocomplete component that provides type-ahead search functionality. It accepts an array of data items and filters them based on user input. The component supports both string arrays and object arrays with configurable label keys. It emits a selected event when an item is chosen from the suggestions list. Features include keyboard navigation, click-outside detection to close suggestions, and customizable placeholder text. Use this component when you need a search-as-you-type input field with dropdown suggestions, such as for selecting users, products, or any searchable data set.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides a styled button with customizable label, type, disabled state, and visual variants (primary, secondary, danger). It emits a clicked event when clicked (if not disabled). Use this component throughout the application for consistent button styling and behavior.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal with customizable title, message, and button labels. It provides two-way communication through confirm and cancel events. Use this component when you need user confirmation before executing critical actions like deletions or irreversible operations. The dialog visibility is controlled by the isOpen input property, and it emits events when the user clicks confirm or cancel buttons.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns, actions, and data types. Supports multiple column types including date, status badges, boolean icons, currency formatting, and plain text. Includes loading states, empty state handling, and action buttons per row. Emits actionClicked events when row actions are triggered. Use this component when you need to display structured data in a table format with optional row actions and various data type formatting.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range picker component that provides two date inputs for selecting a start and end date. It validates that the start date is not after the end date and emits the selected range through the rangeChange event. The component displays an error message when the start date is after the end date. Use this component when you need to capture a date range from users, such as for filtering data by date periods or setting date-based search criteria.

**Import Path**: `app/common/components/app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A file upload component that provides a customizable file input with validation. It accepts allowed file types (default: PNG, JPEG, PDF) and maximum file size (default: 5MB). The component validates file type and size, displays the selected filename, shows error messages for invalid files, and emits the selected file through the fileSelected output event. Use this component when you need a user-friendly file upload interface with built-in validation.

**Import Path**: `app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A footer component that displays a copyright notice with the current year and includes a shared component banner indicator. It automatically calculates and displays the current year in the copyright text. The component has a dark theme with a gradient banner at the top and is designed to be used at the bottom of application layouts.

**Import Path**: `app/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent layout for forms with a card-based design. It includes a header with a title, a content area for form fields (via ng-content), and a footer with customizable Submit and Cancel buttons. The component handles form submission state management, loading indicators, and form validation states. It emits events when users submit or cancel the form, and can be disabled based on loading state or invalid form state. Use this component to standardize form layouts across your application while maintaining flexibility for different form content.

**Import Path**: `app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A reusable header component for the ELogbook Zydus application that provides navigation functionality. It displays the application title and contains dropdown menus for navigating to different master components (5 items), record components (4 items), and log components (8 items). The component uses mouse hover events to toggle dropdown visibility and includes router links for navigation. It features a shared component banner and badge to indicate shared component usage.

**Import Path**: `app/common/components/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A search filter component that provides an input field with search and clear functionality. It emits search events when the user types or presses enter, and includes a clear button that appears when text is entered. The component accepts a placeholder text input and outputs search terms as strings. Use this component in forms, tables, or lists where you need to filter data based on user input.

**Import Path**: `app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays a colored badge based on status text. It accepts a status string and an optional mapping object for custom color assignments. The component automatically applies contextual colors (success, danger, warning, info, secondary) based on the status value using built-in heuristics or custom mappings. Use this component to consistently display status indicators throughout the application with minimal configuration.

**Import Path**: `app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

