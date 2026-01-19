# Angular Component Metadata

Total Components: 13

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a title header with expand/collapse functionality. The component accepts a title string and initial expanded state as inputs, and emits toggle events when expanded or collapsed. Content is projected using ng-content, making it flexible for displaying any type of content within the accordion body. Features a clickable header with chevron icons that indicate the current state (up when expanded, down when collapsed). Styled with Bootstrap classes and includes subtle shadow effects.

**Import Path**: `app/common/components/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable component that renders a group of action buttons (edit, delete, view, approve, etc.) based on configuration. Takes an array of action names as input and emits click events when buttons are pressed. Each button automatically gets appropriate icons, CSS classes, and tooltips based on the action type. Supports common actions like 'edit', 'delete', 'view', 'approve', 'reject', 'info', and 'check' with predefined styling and FontAwesome icons. Perfect for data tables, cards, or any UI where you need consistent action buttons.

**Import Path**: `app/common/components/app-action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppAutocompleteComponent

**Description**: A reusable autocomplete input component that provides real-time search suggestions as the user types. It accepts an array of data items and filters them based on user input, displaying matching results in a dropdown list. The component supports both string arrays and object arrays with configurable label keys. Key features include: customizable placeholder text, configurable data source and label field, real-time filtering with case-insensitive search, dropdown suggestions with hover effects, click-outside-to-close functionality, and emits selected item events. Use this component when you need to provide users with searchable dropdown functionality for selecting from a list of options.

**Import Path**: `app/common/components/app-autocomplete/app-autocomplete.component`

**ID/Selector**: `app-autocomplete`

---

## 4. AppButtonComponent

**Description**: A reusable button component that provides customizable styling and behavior. It accepts inputs for label text, button type (button/submit/reset), disabled state, and visual variant (primary/secondary/danger). The component emits a 'clicked' event when the button is pressed (unless disabled). It includes hover effects and proper disabled state styling. Use this component whenever you need a styled button with consistent appearance across the application.

**Import Path**: `app/common/components/app-button/app-button.component`

**ID/Selector**: `app-button`

---

## 5. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal popup for user confirmation actions. It provides customizable title, message, and button labels through input properties. The component emits events when the user confirms or cancels the action. It includes a backdrop overlay and uses Bootstrap modal styling. Use this component when you need to ask users to confirm destructive or important actions like deletions, form submissions, or navigation changes.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 6. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns and actions. It accepts an array of data objects and column definitions to render a responsive Bootstrap-styled table. Features include: loading state with spinner, empty state message, support for nested object properties, date formatting for date columns, and customizable action buttons for each row. The component emits events when action buttons are clicked, passing both the action type and the row data. Ideal for displaying lists of records with CRUD operations like edit/delete actions.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 7. AppDateRangeComponent

**Description**: A date range picker component that allows users to select start and end dates with validation. It provides two date input fields (From and To) with Bootstrap styling and input group labels. The component validates that the start date is not after the end date and displays an error message if validation fails. It emits a rangeChange event with the selected date range when valid dates are entered. Use this component when you need users to select a date range for filtering, reporting, or any other date-based operations.

**Import Path**: `app/common/components/app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 8. AppFileUploadComponent

**Description**: A reusable file upload component that provides file selection with validation capabilities. It accepts inputs for allowed file types (defaulting to PNG, JPEG, and PDF) and maximum file size in MB (defaulting to 5MB). The component validates selected files against these constraints and displays error messages for invalid files. It emits a fileSelected event when a valid file is chosen, making it suitable for forms and file management interfaces where controlled file uploads are needed.

**Import Path**: `app/common/components/app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 9. AppFooterComponent

**Description**: A footer component that displays copyright information and a shared component banner. It shows the current year dynamically and includes the ELogbook Zydus copyright notice. The component features a dark background with white text, centered content, and a green gradient banner indicating it's a shared component. It's designed to be placed at the bottom of pages and automatically updates the year display.

**Import Path**: `app/common/components/app-footer/app-footer.component`

**ID/Selector**: `app-footer`

---

## 10. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent card-based layout for forms with a header, content area, and footer with action buttons. It includes inputs for customizing the title, submit/cancel button labels, loading state, and form validation state. The component uses content projection (ng-content) to allow any form content to be placed inside it. It emits events when submit or cancel buttons are clicked, with the submit button being disabled during loading or when the form is invalid. The wrapper provides a professional card design with shadow, rounded corners, and Bootstrap-styled buttons.

**Import Path**: `app/common/components/app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 11. AppHeaderComponent

**Description**: A navigation header component for the ELogbook Zydus application that provides the main application title and dropdown navigation menus. Features three main navigation sections: Master (5 components), Records (4 components), and Logs (8 components). Each dropdown menu contains links to various application modules with hover-based toggle functionality. The component manages dropdown visibility states and provides visual indicators for shared components. Includes responsive styling with a dark theme and gradient banner indicating it's a shared component.

**Import Path**: `app/components/app-header/app-header.component`

**ID/Selector**: `app-header`

---

## 12. AppSearchFilterComponent

**Description**: A reusable search input component with a search icon, customizable placeholder text, and clear functionality. Features a Bootstrap-styled input group with a search icon on the left and an optional clear button (X) that appears when text is entered. Emits search events both on Enter key press and on text change for real-time filtering. Accepts a placeholder input property to customize the search prompt text. Should be used wherever search/filter functionality is needed in forms or data tables.

**Import Path**: `app/common/components/app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

## 13. AppStatusBadgeComponent

**Description**: A reusable status badge component that displays status text with appropriate color-coded styling. Takes a status string and optional custom mapping to display colored badges (success, danger, warning, info, secondary). Automatically applies color classes based on common status keywords like 'active', 'pending', 'failed', etc. The status text is displayed in title case format. Useful for showing entity states, process statuses, or any categorical information that needs visual distinction.

**Import Path**: `app/common/components/app-status-badge/app-status-badge.component`

**ID/Selector**: `app-status-badge`

---

