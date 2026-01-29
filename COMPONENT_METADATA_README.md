# Angular Component Metadata

Total Components: 8

---

## 1. AppAccordionComponent

**Description**: A collapsible accordion component that displays a header with a title and chevron icon. When clicked, it toggles the visibility of its content area. It accepts a title input for the header text, an isExpanded input to control its initial state, and emits a toggle event when the state changes. Use this component to organize content into collapsible sections, ideal for FAQs, settings panels, or any content that benefits from a show/hide interface.

**Import Path**: `app/common/components/app-accordion/app-accordion.component`

**ID/Selector**: `app-accordion`

---

## 2. AppActionButtonsComponent

**Description**: A reusable button group component that renders a set of action buttons (edit, delete, view, approve, etc.) based on a configuration array. It accepts an array of action strings via the 'config' input and emits the clicked action name through the 'clicked' output event. Each button is automatically styled with appropriate Bootstrap button classes and Font Awesome icons. Use this component in tables, cards, or any UI where multiple action buttons are needed for an item. The component handles icon mapping, styling, and click events internally, providing a consistent action button interface throughout the application.

**Import Path**: `app/action-buttons/app-action-buttons.component`

**ID/Selector**: `app-action-buttons`

---

## 3. AppConfirmDialogComponent

**Description**: A reusable confirmation dialog component that displays a modal with customizable title, message, and button labels. It provides two-way communication through confirm and cancel events. Use this component when you need user confirmation before executing critical actions like deletions, updates, or irreversible operations. The dialog visibility is controlled by the isOpen input property, and it emits confirm/cancel events when buttons are clicked.

**Import Path**: `app/common/components/app-confirm-dialog/app-confirm-dialog.component`

**ID/Selector**: `app-confirm-dialog`

---

## 4. AppDataTableComponent

**Description**: A reusable data table component that displays tabular data with configurable columns, actions, and data types. Supports multiple column types including date, status badges, boolean icons, currency formatting, and plain text. Provides loading states, empty state handling, and action buttons per row. Emits action events when buttons are clicked. Ideal for displaying lists of entities with edit/delete capabilities or any tabular data presentation.

**Import Path**: `app/common/components/app-data-table/app-data-table.component`

**ID/Selector**: `app-data-table`

---

## 5. AppDateRangeComponent

**Description**: A date range picker component that provides two date inputs (start and end date) with validation. It accepts startDate and endDate as string inputs, validates that the start date is not after the end date, and emits a rangeChange event with both dates when either date is changed. Use this component when you need to capture a date range from users, such as for filtering data by date periods or setting date-based search criteria. The component displays validation errors inline and prevents invalid ranges from being emitted.

**Import Path**: `app/common/components/app-date-range/app-date-range.component`

**ID/Selector**: `app-date-range`

---

## 6. AppFileUploadComponent

**Description**: A reusable file upload component that provides a styled file input with validation. It accepts allowed file types and maximum file size as inputs, validates selected files against these constraints, and emits the selected file through an event emitter. Use this component when you need a consistent file upload experience with built-in validation across your application.

**Import Path**: `app/app-file-upload/app-file-upload.component`

**ID/Selector**: `app-file-upload`

---

## 7. AppFormWrapperComponent

**Description**: A reusable form wrapper component that provides a consistent layout for forms with a card-based design. It includes a header with a title, a content area for form fields (via ng-content), and a footer with customizable submit and cancel buttons. The component handles loading states, form validation states, and emits events when submit or cancel actions are triggered. It supports customization of button labels, title text, and can be disabled based on loading or invalid states.

**Import Path**: `app-form-wrapper/app-form-wrapper.component`

**ID/Selector**: `app-form-wrapper`

---

## 8. AppSearchFilterComponent

**Description**: A reusable search filter component that provides a styled input field with search and clear functionality. It features a search icon on the left, a clear button that appears when text is entered, and emits search events when the user types or presses enter. The component accepts a placeholder text input and outputs search term changes, making it ideal for implementing search functionality in lists, tables, or any content that needs filtering.

**Import Path**: `app-search-filter/app-search-filter.component`

**ID/Selector**: `app-search-filter`

---

