# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a title header with expand/collapse functionality. The component accepts a title string and initial expanded state as inputs, and emits toggle events when expanded or collapsed. Content is projected using ng-content, making it flexible for displaying any type of content within the accordion body. Features a clickable header with chevron icons that indicate the current state (up when expanded, down when collapsed). Styled with Bootstrap classes and includes subtle shadow effects.

**Import Path**: `app/common/components/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable component that renders a group of action buttons (edit, delete, view, approve, etc.) based on configuration. Takes an array of action names as input and emits click events when buttons are pressed. Each button automatically gets appropriate FontAwesome icons, Bootstrap CSS classes, and hover effects. Supports common actions like 'edit', 'delete', 'view', 'approve', 'reject', 'info', and 'check' with predefined styling, but can handle custom actions with default styling. Perfect for data tables, cards, or any UI where you need consistent action buttons.

**Import Path**: `app/common/components/app-action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: A reusable autocomplete input component that provides real-time search suggestions as the user types. It accepts an array of data items and filters them based on user input, displaying matching results in a dropdown list. The component supports both string arrays and object arrays with configurable label keys. Key features include: customizable placeholder text, configurable data source and label field, real-time filtering with case-insensitive search, dropdown suggestions with hover effects, click-outside-to-close functionality, and emits selected item events. Use this component when you need to provide users with searchable dropdown functionality for selecting from a list of options.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides customizable styling and behavior. It accepts inputs for label text, button type (button/submit/reset), disabled state, and visual variant (primary/secondary/danger). The component emits a 'clicked' event when the button is pressed (unless disabled). It includes hover effects and proper disabled state handling. Use this component anywhere you need a styled button with consistent appearance and behavior across the application.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal popup for user confirmation actions. It provides customizable title, message, and button labels through input properties. The component emits events when the user confirms or cancels the action. It includes a backdrop overlay and uses Bootstrap modal styling. Use this component when you need to ask users to confirm destructive or important actions like deletions, form submissions, or navigation changes.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns and actions. Supports multiple column types including text, date, status badges, boolean (with icons), and currency. Features include loading state with spinner, empty state message, hover effects, and action buttons for each row. Inputs: data (array of objects to display), cols (column configuration with field, header, and optional type), actions (array of action names like 'edit', 'delete'), loading (boolean for loading state). Outputs: actionClicked event emitter that fires when an action button is clicked, providing the action name and row data. Handles nested object properties in data fields and provides a responsive, Bootstrap-styled table with rounded corners and shadows.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range picker component that allows users to select start and end dates with validation. It provides two date input fields (From and To) with Bootstrap styling and input group labels. The component validates that the start date is not after the end date and displays an error message if validation fails. It emits a rangeChange event with the selected date range when valid dates are entered. Use this component when you need users to select a date range for filtering, reporting, or any other date-based operations.

**Import Path**: `app/common/components/app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A reusable file upload component that provides file selection with validation. Features include: configurable allowed file types (defaults to PNG, JPEG, PDF), maximum file size validation (defaults to 5MB), displays selected file name or placeholder text, shows validation error messages, and emits the selected file through fileSelected output. Use this component when you need a styled file input with built-in validation for file type and size constraints.

**Import Path**: `app/common/components/app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A footer component that displays copyright information and a shared component banner. It shows the current year dynamically and includes the ELogbook Zydus copyright notice. The component features a dark blue background with white text, centered content, and a green gradient banner indicating it's a shared component. It's designed to be placed at the bottom of pages and automatically updates the year display.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent card-based layout for forms with a header, content area, and footer with action buttons. It includes inputs for customizing the title, submit/cancel button labels, loading state, and form validation state. The component uses content projection (ng-content) to allow any form content to be placed inside it. It emits events when submit or cancel buttons are clicked, and automatically disables the submit button when the form is loading or invalid. Features a clean Bootstrap-styled card design with shadow and rounded corners.

**Import Path**: `app/common/components/app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A navigation header component for the ELogbook Zydus application that provides the main navigation menu with dropdown functionality. Features include: a fixed application title, three main navigation sections (Master, Records, Logs) with dropdown menus containing route links, hover-based dropdown interactions, and visual indicators for shared components. The component manages dropdown visibility states and provides navigation to various application modules including Customer Master, Product Master, BMR/BPR Tracking, Cleaning Records, Equipment Usage, and various log components. Should be used as the primary navigation header across the application.

**Import Path**: `app/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A reusable search input component with a search icon, customizable placeholder text, and clear functionality. It features a Bootstrap-styled input group with a search icon on the left and an optional clear button (X) that appears when there is text. The component emits search events both on Enter key press and on text changes for real-time filtering. It accepts a placeholder input property to customize the search prompt text and outputs search events with the current search term. Use this component when you need to provide search/filter functionality in lists, tables, or any data display components.

**Import Path**: `app/common/components/app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays status text with appropriate color-coded styling. Takes a status string and optional custom mapping to display colored badges (success, danger, warning, info, secondary). Automatically applies color classes based on common status keywords like 'active', 'pending', 'failed', etc. The status text is displayed in title case format. Useful for showing status indicators throughout the application with consistent styling.

**Import Path**: `app/common/components/app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

